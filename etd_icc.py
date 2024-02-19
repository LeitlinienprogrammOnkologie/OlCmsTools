import pandas as pd
import pingouin as pg
import os

source_dir = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Kongresse_Vorträge_Publikationen/Guidelines International Network (G-I-N)/G-I-N 2024/EtD-Prüfung durch KI"
source_file1 = "2024-02-13_Bewertungsbogen KI 1.xlsx"
source_path1 = os.path.join(source_dir, source_file1)
source_file2 = "2024-02-13_Bewertungsbogen KI 2.xlsx"
source_path2 = os.path.join(source_dir, source_file2)
source_file3 = "2024-02-13_Bewertungsbogen KI 3_neu.xlsx"
source_path3 = os.path.join(source_dir, source_file3)

assessment1 = pd.read_excel(source_path1)
assessment2 = pd.read_excel(source_path2)
assessment3 = pd.read_excel(source_path3)

assessment1_long = assessment1.melt(id_vars=['Index', 'Topic'],
                                    value_vars=["clarityAndActionability", "necessityInHealthcare",
                                                "netPositiveConsequence", "opportunityCost",
                                                "rationaleForIndirectEvidence"],
                                    var_name='AssessmentItem', value_name='Score')

assessment2_long = assessment2.melt(id_vars=['Index', 'Topic'],
                                    value_vars=["clarityAndActionability", "necessityInHealthcare",
                                                "netPositiveConsequence", "opportunityCost",
                                                "rationaleForIndirectEvidence"],
                                    var_name='AssessmentItem', value_name='Score')

assessment3_long = assessment3.melt(id_vars=['Index', 'Topic'],
                                    value_vars=["clarityAndActionability", "necessityInHealthcare",
                                                "netPositiveConsequence", "opportunityCost",
                                                "rationaleForIndirectEvidence"],
                                    var_name='AssessmentItem', value_name='Score')

assessment1_long['AssessmentInstance'] = 1
assessment2_long['AssessmentInstance'] = 2
assessment3_long['AssessmentInstance'] = 3

combined_assessments_long = pd.concat([assessment1_long, assessment2_long, assessment3_long], ignore_index=True)

icc_results = {}

out_csv = "Topic|AssessmentItem|ICC|F|df1|df2|pval|CI95%\n"

for topic in combined_assessments_long['Topic'].unique():
    for item in combined_assessments_long['AssessmentItem'].unique():
        # Filter data for the current topic and item
        item_data = combined_assessments_long[(combined_assessments_long['Topic'] == topic) & (combined_assessments_long['AssessmentItem'] == item)]

        # Calculate ICC
        try:
            icc = pg.intraclass_corr(data=item_data, targets='Index', raters='AssessmentInstance', ratings='Score',
                                     nan_policy='omit')  # Adjust 'nan_policy' as needed

            icc_value = icc.set_index('Type').at['ICC2k', 'ICC']  # 'ICC2k' for average measures, adjust as needed

            df_string = icc.apply(lambda row: '|'.join([topic, item] + row.astype(str).tolist()), axis=1).str.cat(
                sep='\n')
            df_string += "\n%s|%s|%s\n" % (topic, item, icc_value)
            out_csv += df_string
            # Store ICC result
            icc_results[(topic, item)] = icc_value
        except:
            pass

with open("ICC_by_topic.csv", "w", encoding="utf-8") as f:
    f.write(out_csv)
