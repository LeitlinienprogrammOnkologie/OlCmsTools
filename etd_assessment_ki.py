import os
import pandas as pd
import numpy as np
from pingouin import intraclass_corr

source_dir = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Kongresse_Vorträge_Publikationen/Guidelines International Network (G-I-N)/G-I-N 2024/EtD-Prüfung durch KI"
source_file = "2024-02-13_Bewertungsbogen gepoolt.xlsx"
source_path = os.path.join(source_dir, source_file)

df = pd.read_excel(source_path, sheet_name='reduced')
ai_df = df[df['Rater'].str.startswith('AI_')]

#    icc = pg.intraclass_corr(data=data_for_icc, targets=item, raters='Rater', ratings='Score', nan_policy='omit').round(3)

icc_ca = intraclass_corr(data=ai_df, raters="Rater", targets='clarityAndActionability', ratings='Score', nan_policy='omit').round(3)
icc_nh = intraclass_corr(data=ai_df, targets='Rater', raters='necessityInHealthcare')
icc_np = intraclass_corr(data=ai_df, targets='Rater', raters='netPositiveConsequence')
icc_oc = intraclass_corr(data=ai_df, targets='Rater', raters='opportunityCost')
icc_ri = intraclass_corr(data=ai_df, targets='Rater', raters='rationaleForIndirectEvidence')
icc_js = intraclass_corr(data=ai_df, targets='Rater', raters='justificationForStrengthOfRecommendation')

print(icc_ca)
print(icc_nh)
pass