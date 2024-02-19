import os
import pandas as pd
import numpy as np
import pingouin as pg

# Define paths (Adjust with your specific directories)
source_dir = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Kongresse_Vorträge_Publikationen/Guidelines International Network (G-I-N)/G-I-N 2024/EtD-Prüfung durch KI"
source_file = "2024-02-13_Bewertungsbogen gepoolt.xlsx"
source_path = os.path.join(source_dir, source_file)

# Load the Excel file
df = pd.read_excel(source_path, sheet_name='reduced')

# Define the columns of interest
columns_of_interest = ['clarityAndActionability', 'necessityInHealthcare', 'netPositiveConsequence',
                       'opportunityCost', 'rationaleForIndirectEvidence', 'justificationForStrengthOfRecommendation']

# Preparing DataFrame for ICC calculation
long_df = pd.melt(df, id_vars=['Rater'], value_vars=columns_of_interest, var_name='Item', value_name='Score')

# Initialize output string for saving results
out_csv = "Item|ICC\n"

# Calculate ICC for each item
for column in columns_of_interest:
    # Select the data for the current column/item
    data = long_df[long_df['Item'] == column]
    # Calculate the ICC using Pingouin
    icc = pg.intraclass_corr(data=data, targets='Item', raters='Raters', ratings='Score').round(3)
    # Append the results to the output string
    out_csv += "%s|%s\n" % (column, icc.set_index('Type').loc['ICC3k']['ICC'])  # Choose ICC type as needed

# Save the results to a CSV file
with open("etd_icc.csv", "w", encoding="utf-8") as f:
    f.write(out_csv)
