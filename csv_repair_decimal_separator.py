file_path = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Vorträge/G-I-N 2023/Easy Language Guidelines with KI/count_results.csv"
file_path = "pll_undestandability_with_KI.csv"
file_path = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Vorträge/EbM-Kongress 2023/Verständlichkeitsanalyse PLL/2023-03-14_Verständlichkeit_WSF.csv"

index_list = [3, 4, 5, 6, 8, 9, 10, 11]

with open(file_path, "r", encoding="utf-8") as f:
    csv_list = f.readlines()

repair_char = [".", ","]

for line_index in range(len(csv_list)):
    line = csv_list[line_index]
    column_arr = line.split("|")
    for i in range(len(column_arr)):
        if i in index_list:
            column = column_arr[i]
            column = column.replace(repair_char[0], repair_char[1])
            column_arr[i] = column

    csv_list[line_index] = "|".join(column_arr)

out_path = file_path.replace(".csv", "_reparied.csv")
with open(out_path, "w", encoding="utf-8") as f:
    f.writelines(csv_list)