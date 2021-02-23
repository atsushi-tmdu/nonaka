## mimic waveformと一致する患者のidを取り出す
##　subject_idそれぞれに対応するpathと両方をpickleにて保存
## 保存ファイルはsubject.txt
## subject_idとcharteventsを照合した結果をleft joinしたもの
## merged_csvに保存

#%%
import subprocess
import shutil
import re
import csv
import pprint
import pandas as pd

mimic_parent_path='/export/work/data/deep_learning/mimic_waveform/raw/mimic3wdb/1.0/matched/'
current_path='/home/senda1980/mimic_potassium/'
cmd = ['ls']

p1 = subprocess.check_output(cmd,cwd=mimic_parent_path)
p1=p1.decode()
p1=p1.split('\n')
intermediate_path=[]
for i in p1:
  subdir= re.match(r'p0[0-9]',i) 
  #subdir=filter(None,subdir)
  if subdir != None:
    curdir = mimic_parent_path+subdir.group()
    #print(curdir)
    intermediate_path.append(curdir)

subject_path=[]
subject_id=[]
for i in intermediate_path:
    p2 = subprocess.check_output(cmd,cwd=i)
    p2=p2.decode()
    p2=p2.split('\n')
    for j in p2:
        if j !='index.html' and j!='':
            #print(j)
            sub_dir = i+'/'+j+'/'
            subject_path.append(sub_dir)
            subject_id.append(j)


stripped_subject_id=[]
for i in subject_id:
    if i != '':
        temp_i = i.lstrip('p')
        temp_i = int(temp_i)
        stripped_subject_id.append(temp_i)

patient_csv = pd.read_csv(current_path+"PATIENTS.csv")
waveform_id_df=pd.DataFrame(stripped_subject_id,columns=['SUBJECT_ID'])
waveform_id_df=pd.merge(waveform_id_df,patient_csv,on='SUBJECT_ID',how='left')

# %%
if(0):
    chartevents_csv=pd.read_csv(current_path+'CHARTEVENTS.csv')
    all_df = pd.merge(waveform_id_df,chartevents_csv,on='SUBJECT_ID',how='left')
    all_df.to_csv('/home/senda1980/mimic_potassium/merged_csv')

# %%
import pickle
f = open('subject.txt','wb')
pickle.dump([subject_id,subject_path], f)
# %% pickle確認
if(0):
    with open('subject.txt','rb') as f:
     a, b = pickle.load(f)
# %%
