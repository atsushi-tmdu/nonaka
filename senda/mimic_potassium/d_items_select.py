#%%
waveform_path='/export/work/data/deep_learning/mimic_waveform/raw/mimic3wdb/1.0/matched'
dtflag=0

import sys
sys.path.append("/home/senda1980/.pyenv/versions/3.8.5/lib/python3.8/site-packages")
import subprocess
import shutil
import re
import csv
import pprint
from numpy.core.arrayprint import SubArrayFormat
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pandas.io.parsers import read_csv
import wfdb
import itertools
import pickle
from tqdm import tqdm
import slackweb
from datetime import datetime as dt

def slacknotify(notify):
    import slackweb
    slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
    slack.notify(text=notify)

current_path='/home/senda1980/mimic_potassium/mimic_potassium/'


slacknotify('starting d_items')
if(dtflag):
    d_items_df = pd.read_csv('/home/senda1980/mimic_potassium/mimic_potassium/D_ITEMS_selected.csv')
    d_items_df=d_items_df[['itemid','label','flag']]
    d_items_df=d_items_df.query('flag==1')

    #flag==1以外のものを削除
    d_items_df.to_csv('d_items_df_reduced.csv')

d_items_df = read_csv(current_path+'d_items_df_reduced.csv')

if (dtflag): #selected_events_df作成に時間がかかるため必要がない限り読み込みで対処
    merged_csv_df=pd.read_csv('/home/senda1980/mimic_potassium/mimic_potassium/merged_csv')
    d_items_df=d_items_df.rename(columns={'itemid':'ITEMID'})
    selected_events_df=pd.merge(d_items_df,merged_csv_df,on='ITEMID',how='left')

    #charteventsの中からwaveformと照合できたもののうちD_ITEMSの項目のうち今後
    # 使える可能性のあるitemidだけをpickupしたものがselected_events_df
    #これをcsvに保存

    selected_events_df.to_csv('selected_events_df.csv')

selected_events_df = read_csv(current_path+'selected_events_df.csv')

###以下はpotassiumに関連あるものだけとした

if(0):  #selected_eventsの抜き出しは１回だけやれば良いし時間かかるのでコメントアウト

    pot_id=[829,4194,3725,3792,1535,220640,226535,227442,227464]
    pot_id_df=pd.DataFrame(pot_id,columns=['ITEMID'])
    selected_events_df=pd.merge(pot_id_df,selected_events_df,on='ITEMID',how='left')

    selected_events_df=selected_events_df.dropna(subset=['SUBJECT_ID'])
    selected_events_df['SUBJECT_ID']=selected_events_df['SUBJECT_ID'].astype(int)
    #selected_events_df.head()

    #potassium.csvに出力。waveformに関連する患者情報でpotassiumの値と関連するもののみのデータとなっている
    selected_events_df.to_csv('potassium.csv')

#loadする
selected_events_df = read_csv(current_path+'potassium.csv')


#  subjectid, filepathを読み込み

import pickle
with open ('subject.txt','rb') as f:
    subject_id,subject_path = pickle.load(f)


### この情報を取得しheader_filesに格納 len(header_files)はlen(subject_id)に一致する
import itertools

if(dtflag):
    cmd = ['ls']
    header_files=[]
    for i,path in enumerate(tqdm(subject_path)):
        p1 = subprocess.check_output(cmd,cwd=path)
        p1=p1.decode()
        p1=p1.split('\n')
        #print(p1)
        id_matched=[]
        for j in p1:
            my_regex = re.compile(subject_id[i] +'-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}\.hea')
            matched_file = re.findall(my_regex,j) 
            if matched_file !=[]:
                id_matched.append(matched_file)

        header_files.append(list(itertools.chain.from_iterable(id_matched)))

    header_files_df = pd.DataFrame(header_files)
    header_files_df.to_csv("header_files.csv")

header_files_df = pd.read_csv("header_files.csv")
subject_id=pd.DataFrame(subject_id,columns={'SUBJECT_ID'})
header_files_df=header_files_df.iloc[:,1:]
subject_and_header_df = pd.concat([subject_id,header_files_df],axis=1)

potassium_df=pd.read_csv("potassium.csv")
potassium_df=potassium_df[['SUBJECT_ID','GENDER','DOB','DOD','CHARTTIME','VALUE','ITEMID']]
potassium_df['SUBJECT_ID']='p'+potassium_df['SUBJECT_ID'].astype(str).str.zfill(6)


potassium_df=pd.merge(potassium_df,subject_and_header_df,how='left',on='SUBJECT_ID')
potassium_df=potassium_df.assign(dir="")
for i in range(len(potassium_df)):
    potassium_df['dir'][i]=os.path.join(waveform_path,potassium_df.iloc[i]['SUBJECT_ID'][:3]+'/',potassium_df.iloc[i]['SUBJECT_ID'])


#%%
potassium_df=potassium_df.assign(file="")
potassium_df=potassium_df.assign(diff="")

def header_reader(potassium_df=potassium_df):
    from datetime import datetime as dt

#    for i in tqdm(range(len(potassium_df))):
    for i in range(100):
        charttime = dt.strptime(potassium_df.iloc[i]['CHARTTIME'], '%Y-%m-%d %H:%M:%S')
        target_file= pd.DataFrame(index=[], columns=['file','diff'])
        for j in range(58): 
            file = potassium_df.iloc[i][str(j)]

            if file is np.nan:
                continue

            filename= os.path.join(potassium_df.iloc[i]['dir'],file)
            filename=filename[:-4]
            record=wfdb.rdheader(filename)
            sig_len = record.sig_len
            date_time = record.base_datetime
            fs = record.fs
            #K測定時刻と心電図開始時間の照合
            diff_time = date_time - charttime
            pot_len = diff_time.seconds *  fs
            #print(i,j)
            #print(charttime)
            #print(pot_len)
            if(pot_len > sig_len): #headerのどこにも合わない場合にはcontinueで時間節約
                continue

            #全体のheader fileから各ファイルの名前とseq長の表を作成
            header_table_df=pd.DataFrame(np.vstack([record.seg_name,record.seg_len]).T,columns=['file', 'sequence'])
            #header_table_df=header_table_df.query('file.str.match("[0-9]{7}_[0-9]{4}")')
            header_table_df['cumsum']=header_table_df['sequence'].astype(int).cumsum()
            #header_table_df.query('cumsum-pot_len>0').iloc[0] #K測定時刻に相当するファイルを取り出す
            header_table_df['diff']=header_table_df['cumsum']-pot_len
            # target fileにはpotassium測定時刻に対応するfile名file、当該時刻における初めからの系列の長さを記録
            if len(target_file.index)==1:
                print('{},{}: target file already exists!!'.format(i,j))

            target_file = header_table_df.query('diff>0')

            if len(target_file.index)==0:
                continue
            elif len(target_file.index)==1:
                #print('---')
                target_file = target_file.iloc[0][['file','diff']]
                #print(i,j)
                #print(target_file)
                #print('test')
        potassium_df['file'][i]= target_file['file']
        potassium_df['diff'][i] = target_file['diff']
   
    return(potassium_df)

#%%
a=header_reader(potassium_df=potassium_df)  

#%%
a.head()
#%%
type(potassium_df.iloc[0]['CHARTTIME'])




#%%
temp ='/export/work/data/deep_learning/mimic_waveform/raw/mimic3wdb/1.0/matched/p00/p000020/p000020-2183-04-28-17-47.hea.hea'
#%%
potassium_df

#%%
filename=waveform_path+'/p00/p000020/'+'p000020-2183-04-28-17-47'
filename=waveform_path+'/p00/p000033/p000033-2116-12-24-12-35'
record=wfdb.rdheader(filename)
record.sig_len
#record.d_signal
record.fs
record.base_datetime

#%%
potassium_df.head()
# %%

# %%
record.segments
# %%
record.layout
# %%
record.seg_name
# %%
record.sig_segments
# %%
record.seg_len
# %%
len(record.seg_len)
# %%
len(record.seg_name)
# %%
record.sig_len
# %%
record.fs
# %%
record.sig_len/record.fs
# %%
record.base_datetime
# %%
type(potassium_df.iloc[1]['CHARTTIME'])
#
# %%
record.base_datetime.minute
# %%
header_table_df=pd.DataFrame(np.vstack([record.seg_name,record.seg_len]).T,columns=['file', 'sequence'])
