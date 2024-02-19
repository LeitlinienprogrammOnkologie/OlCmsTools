import os
import pandas as pd
import numpy as np
import pingouin as pg

source_dir = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Kongresse_Vorträge_Publikationen/Guidelines International Network (G-I-N)/G-I-N 2024/EtD-Prüfung durch KI"
source_file = "2024-02-13_Bewertungsbogen gepoolt.xlsx"
source_path = os.path.join(source_dir, source_file)

df = pd.read_excel(source_path, sheet_name='reduced')
df_dropped_last_two = df.iloc[:, :-2]

human_df = df_dropped_last_two[df_dropped_last_two['Rater'].str.startswith('Human')]
df_long = pd.melt(human_df, id_vars=['Rater'], var_name='Criteria', value_name='Rating')

ai_df = df[df['Rater'].str.startswith('AI')]
numeric_cols = ai_df.select_dtypes(include=np.number)

# Calculate the mean for each numeric column
mean_values = numeric_cols.mean()
mean_values_df = mean_values.to_frame().transpose()
mean_values_df.insert(0, 'Rater', 'AI')
mean_values_df.index = ['AI']

df_ai_long = pd.melt(mean_values_df, id_vars=['Rater'], var_name='Criteria', value_name='Rating')

df_appended = df_long.append(df_ai_long, ignore_index=True)

icc = pg.intraclass_corr(data=df_appended, targets='Criteria', raters='Rater', ratings='Rating', nan_policy='omit').round(3)
pass
