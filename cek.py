import pandas as pd
 
raw = pd.read_csv('data-pipeline-assignment/data/raw/automobileEDA_dirty_training.csv')
out = pd.read_csv('data-pipeline-assignment/data/processed/automobileEDA_processed.csv')
 
print('raw       :', raw.shape)
print('processed :', out.shape)
print('missing   :', out.isnull().sum().sum())
print('duplikat  :', out.duplicated().sum())
