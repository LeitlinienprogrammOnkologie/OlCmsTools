import pandas as pd
import numpy as np

df = pd.read_excel("//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Publikationen/2023/Auswertung CoI/coi.xlsx", sheet_name=None)

out_csv = "Leitline|Autoren|ohne IK|geringe IK|moderate IK|hohe IK\n"

for sheet_name in df:
    sheet = df[sheet_name]
    author_count = 0
    high_coi_count = 0
    moderate_coi_count = 0
    low_coi_count = 0
    no_coi_count = 0
    author_dict = {}
    current_author = None
    last_author = None
    coi_list = [0, 0, 0, 0]
    for index, row in sheet.iterrows():
        author = row[0]
        if not pd.isna(author):
            author_count += 1
            current_author = author
        if last_author is not None and current_author is not None and current_author != last_author:
            try:
                max_coi = np.where(coi_list)[0].max()
            except:
                max_coi = 0
            author_dict[last_author] = max_coi
            coi_list = [0, 0, 0, 0]
        if current_author is not None:
            if pd.isna(row[8]): continue
            coi_text = row[8].lower()
            if "ohne mandat" in coi_text or ("nicht an" in coi_text and "beteiligt" in coi_text):
                continue
            if "hoch" in coi_text or "hohe" in coi_text:
                coi_list[3] += 1
            elif "moderat" in coi_text or "doppelabstimmung" in coi_text:
                coi_list[2] += 1
            elif "enthaltung" in coi_text:
                coi_list[2] += 1
                print(coi_text)
            elif "gering" in coi_text or "niedrig" in coi_text:
                coi_list[1] += 1
            else:
                coi_list[0] += 1
            last_author = current_author
    coi_list = [0, 0, 0, 0]
    if sheet_name == "Endometrium":
        pass
    for author, max_coi in author_dict.items():
        coi_list[max_coi] += 1
    out_csv += "%s|%s|%s|%s|%s|%s\n" % (sheet_name, len(author_dict), coi_list[0], coi_list[1], coi_list[2], coi_list[3])

with open("coi_analysis.csv", "w", encoding="utf-8") as f:
    f.write(out_csv)
