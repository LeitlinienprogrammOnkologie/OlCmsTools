file_path = "C:/Users/User/PycharmProjects/OlCmsTools/count_results.csv"

with open(file_path, "r", encoding="utf-8") as f:
    csv_list = f.readlines()

index_list = [15, 16, 17, 18, 19, 20, 21, 22, 23]
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