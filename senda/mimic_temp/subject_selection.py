#%%mimic-iiiでKの測定が行われているデータと、対応する患者と照合が取れているものを抽出しmatched_idに格納
import pandas as pd
import glob
import os


subject_id= pd.read_csv("/home/senda1980/mimic_temp/subject_id.csv", skiprows=1)
waveform_id = pd.read_csv("/export/work/data/deep_learning/mimic_waveform/raw/physionet.org/files/mimic3wdb/1.0/matched/RECORDS-waveforms", delimiter="/",header=None)

waveform_id=waveform_id.iloc[:,1]
waveform_id=pd.DataFrame(waveform_id)
waveform_id.columns=['subject_id']
subject_id.columns=['subject_id']
subject_id=subject_id.iloc[:-1,:]
subject_id=subject_id['subject_id'].astype('str').str.strip().str[-5:]
subject_id=pd.DataFrame(subject_id)
subject_id.columns=['subject_id']
subject_id=subject_id['subject_id'].astype('str').str.zfill(6)
subject_id = pd.DataFrame(subject_id)
subject_id.columns=['subject_id']
subject_id='p'+subject_id

matched_id = pd.merge(waveform_id,subject_id, on='subject_id',how='inner')
matched_id.to_csv("matched_subject_id.csv")

# %%
matched_id['dir']=matched_id['subject_id'].str[0:3]
pass_to_parent="/export/work/data/deep_learning/mimic_waveform/raw/physionet.org/files/mimic3wdb/1.0/matched"
matched_id['fullpath']=pass_to_parent+matched_id['subject_id']+matched_id['dir']
# %%
matched_id

# %%
