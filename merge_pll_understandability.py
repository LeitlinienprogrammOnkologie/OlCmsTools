import pandas as pd
from PllUnderstandability.TextParser import IndexCalculator

index_calculator = IndexCalculator()

input_file = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Vorträge/G-I-N 2023/Easy Language Guidelines with KI/2023-02-13_SUMM_results.xlsx"

df = pd.read_excel(input_file, sheet_name="SUMM")

out_file = "Leitlinie|Kapitel|PLL-Text|PLL-ASL|PLL-ASW|PLL-LIX|PLL-FLESH_DE|DV3-Text|DV3-ASL|DV3-ASW|DV3-LIX|DV3-FLESH_DE|SUMM-Text|SUMM-ASL|SUMM-ASW|SUMM-LIX|SUMM-FLESH_DE\n"

N= len(df)
i = 0
for index, row in df.iterrows():
    i+=1
    pll_text = row['PLL']
    metrics = index_calculator.Handle(pll_text)
    if metrics is not None:
        flesh_de = 180 - metrics.ASL - (58.5 * metrics.ASW)
    else:
        flesh_de = -1
        pass
    try:
        out_row = "%s|%s|%s|%s|%s|%s|%s" % (
            row['LL'], row['Kapitel'],
            pll_text, metrics.ASL, metrics.ASW, metrics.lix_index, flesh_de)
    except:
        out_row = "%s|%s|||||" % (row['LL'], row['Kapitel'])

    summ_text = row['SUMM']
    if isinstance(summ_text, str):
        summ_text = summ_text.replace(".", ". ").replace(",",", ").replace("  ", " ")
        metrics = index_calculator.Handle(summ_text)
        if metrics is not None:
            flesh_de = 180 - metrics.ASL - (58.5 * metrics.ASW)
            out_row += "|%s|%s|%s|%s|%s\n" % (
                summ_text, metrics.ASL, metrics.ASW, metrics.lix_index, flesh_de)
        else:
            out_row += "\n"
    else:
        out_row += "\n"

    out_file += out_row
    print("%s or %s (%s)%%" % (index, N, 100*(i/N)))

with open("pll_undestandability_with_KI.csv", "w", encoding="utf-8") as f:
    f.write(out_file)