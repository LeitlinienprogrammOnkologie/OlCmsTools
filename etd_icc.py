import pandas as pd
import pingouin as pg
import os

source_dir = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Kongresse_Vorträge_Publikationen/Guidelines International Network (G-I-N)/G-I-N 2024/EtD-Prüfung durch KI"
source_file1 = "2024-02-13_Bewertungsbogen KI 1.xlsx"
source_path1 = os.path.join(source_dir, source_file1)
source_file2 = "2024-02-13_Bewertungsbogen KI 2.xlsx"
source_path2 = os.path.join(source_dir, source_file2)
source_file3 = "2024-02-13_Bewertungsbogen KI 3.xlsx"
source_path3 = os.path.join(source_dir, source_file3)

assessment1 = pd.read_excel(source_path1)
assessment2 = pd.read_excel(source_path2)
assessment3 = pd.read_excel(source_path3)

source_file = "2024-02-13_Bewertungsbogen AJ.xlsx"
assessment_h1 = pd.read_excel(os.path.join(source_dir, source_file), sheet_name="konsensbasiert")
source_file = "2024-02-13_Bewertungsbogen GW.xlsx"
assessment_h2 = pd.read_excel(os.path.join(source_dir, source_file), sheet_name="konsensbasiert")

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

assessment_h1_long = assessment_h1.melt(id_vars=['Index', 'Topic'],
                                    value_vars=["clarityAndActionability", "necessityInHealthcare",
                                                "netPositiveConsequence", "opportunityCost",
                                                "rationaleForIndirectEvidence"],
                                    var_name='AssessmentItem', value_name='Score')

assessment_h2_long = assessment_h2.melt(id_vars=['Index', 'Topic'],
                                    value_vars=["clarityAndActionability", "necessityInHealthcare",
                                                "netPositiveConsequence", "opportunityCost",
                                                "rationaleForIndirectEvidence"],
                                    var_name='AssessmentItem', value_name='Score')

assessment1_long['AssessmentInstance'] = 1
assessment2_long['AssessmentInstance'] = 2
assessment3_long['AssessmentInstance'] = 3
combined_assessment = pd.concat([assessment1_long, assessment2_long, assessment3_long])
average_scores = combined_assessment.groupby(['Topic', 'AssessmentItem']).agg(AverageScore=('Score', 'mean')).reset_index()
average_scores['AssessmentInstance'] = 6

assessment_h1_long['AssessmentInstance'] = 4
assessment_h2_long['AssessmentInstance'] = 5
combined_assessment_h = pd.concat([assessment_h1_long, assessment_h2_long])
average_h_scores = combined_assessment_h.groupby(['Topic', 'AssessmentItem']).agg(AverageScore=('Score', 'mean')).reset_index()
average_h_scores['AssessmentInstance'] = 7

combined_assessments_long = pd.concat([assessment1_long, assessment2_long, assessment3_long], ignore_index=True)
combined_assessments_h_long = pd.concat([assessment_h1_long, assessment_h2_long], ignore_index=True)

combined_assessments_2_long = pd.concat([average_scores, average_h_scores], ignore_index=True).reset_index()

icc_results = {}

out_csv = "Assessor|Topic|AssessmentItem|Type|Description|ICC|F|df1|df2|pval|CI95%|CI Low|CI High\n"
topic_list = list(combined_assessments_long['Topic'].unique())
topic_list.append("Pooled")
for topic in topic_list:
    for item in combined_assessments_long['AssessmentItem'].unique():
        # Filter data for the current topic and item
        if topic == "Pooled":
            item_data = combined_assessments_long[combined_assessments_long['AssessmentItem'] == item]
        else:
            item_data = combined_assessments_long[
                (combined_assessments_long['Topic'] == topic) & (combined_assessments_long['AssessmentItem'] == item)]
        # Calculate ICC
        icc = pg.intraclass_corr(data=item_data, targets='Index', raters='AssessmentInstance', ratings='Score',
                                 nan_policy='omit')  # Adjust 'nan_policy' as needed

        for idx, row in icc.iterrows():
            row_list = [str(x) for x in list(row)]
            ci_arr = row_list[-1].replace(" ]","]").split(" ")
            ci_low = ci_arr[0].replace("[", "").strip()
            ci_high = ci_arr[-1].replace("]", "").strip()
            out_row = "AI|%s|%s|%s|%s|%s\n" % (topic, item, "|".join(row_list), ci_low, ci_high)
            out_csv += out_row

for topic in topic_list:
    for item in combined_assessments_h_long['AssessmentItem'].unique():
        # Filter data for the current topic and item
        if topic == "Pooled":
            item_data = combined_assessments_h_long[combined_assessments_h_long['AssessmentItem'] == item]
        else:
            item_data = combined_assessments_h_long[(combined_assessments_h_long['Topic'] == topic) & (combined_assessments_h_long['AssessmentItem'] == item)]
        # Calculate ICC
        icc = pg.intraclass_corr(data=item_data, targets='Index', raters='AssessmentInstance', ratings='Score',
                                 nan_policy='omit')  # Adjust 'nan_policy' as needed

        for idx, row in icc.iterrows():
            row_list = [str(x) for x in list(row)]
            ci_arr = row_list[-1].split(" ")
            ci_low = ci_arr[0].replace("[", "").strip()
            ci_high = ci_arr[-1].replace("]", "").strip()
            out_row = "Human|%s|%s|%s|%s|%s\n" % (topic, item, "|".join(row_list), ci_low, ci_high)
            out_csv += out_row

for topic in topic_list:
    for item in combined_assessments_2_long['AssessmentItem'].unique():
        # Filter data for the current topic and item
        if topic == "Pooled":
            item_data = combined_assessments_2_long[combined_assessments_2_long['AssessmentItem'] == item]
        else:
            item_data = combined_assessments_2_long[(combined_assessments_2_long['Topic'] == topic) & (combined_assessments_2_long['AssessmentItem'] == item)]
        # Calculate ICC
        icc = pg.intraclass_corr(data=item_data, targets='index', raters='AssessmentInstance', ratings='AverageScore',
                                 nan_policy='omit')  # Adjust 'nan_policy' as needed

        for idx, row in icc.iterrows():
            row_list = [str(x) for x in list(row)]
            ci_arr = row_list[-1].split(" ")
            ci_low = ci_arr[0].replace("[", "").strip()
            ci_high = ci_arr[-1].replace("]", "").strip()
            out_row = "Human vs AI|%s|%s|%s|%s|%s\n" % (topic, item, "|".join(row_list), ci_low, ci_high)
            out_csv += out_row

out_csv = out_csv.replace(".", ",")
with open("ICC_by_topic.csv", "w", encoding="utf-8") as f:
    f.write(out_csv)
