import pandas as pd
import numpy as np

test = 'C:\\Users\\ekate\\OneDrive\\Desktop\\test.xlsx'
filename = 'C:\\Users\\ekate\\Downloads\\Резерв Инская -Тайга после обточки (Сек. А 29.05.20).xlsx'
data = pd.read_excel(filename, index="index")

# Получим массив заголовков
headers = list(map(lambda x: str(x), data.columns.to_list()))
print(len(headers))

# Получим bool-массив для определения NAN
data_bool = data.isna()

headers_new = []

# Определим столбец Unnamed, в котором больше всего NAN
# Определим правильные названия заголовков для остальных столбцов
max_nan = -1;
for col in data_bool.columns:
    temp = -1
    un = False
    if "Unnamed" in col:
        un = True
    for i in range(len(data_bool)):
        if data_bool[col][i]:
            if "Unnamed" in col:
                if max_nan < i:
                    max_nan = i
            else:
                if temp == -1:
                    temp = i
    if temp != -1:
        if temp == 0:
            headers_new.append(col)
        else:
            headers_new.append(data[col][temp-1])
    else:
        if not un:
            headers_new.append(data[col][0])

# Определим заголовки для Unnamed
for col in data.columns:
    if "Unnamed" in col:
        headers_new.append(data[col][max_nan + 1])

# Получим новый датафрейм. Создадим соответствующее столбцам количество словарей
if len(headers_new) == 0:
     data_new = data
else:
    print(headers_new)
    dic = dict.fromkeys(headers_new)
    for i in range(len(headers_new)):
        l = []
        if "Unnamed" in data.columns[i]:
            for j in range(max_nan + 2, len(data)):
                l.append(data[data.columns[i]][j])
        else:
            temp = False
            for j in range(len(data)):
                if not data_bool[data.columns[i]][j] and temp == True:
                    l.append(data[data.columns[i]][j])
                if data_bool[data.columns[i]][j] == True:
                    temp = True
            if not temp:
                for j in range(1, len(data)):
                    l.append(data[data.columns[i]][j])
                    
        print(headers_new[i])
        print(len(l))
        dic[headers_new[i]] = l

    data_new = pd.DataFrame(dic)
