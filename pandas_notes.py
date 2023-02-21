"""
Pandas is python's open source library.
"""
import pandas as pd

data_set = pd.read_csv('datasets\iris_csv.csv')

#groupby()- will group data set based on given column name.
# groupby() function will bydefault sort group elements in alphabetical order.
# So, we can specify sort = False if sorting is not needed.
class_group = data_set.groupby('class') #will sort data
class_group = data_set.groupby(['class'], sort = False) #will not sort data.s
'''first() will return first row of each group returned by groupby() function. 
first() won't return every records in grouped data. And it will return the specified column name as index.
'''
first_class = class_group.first()
print(first_class)

# to return all records available in a particular group, we can should use get_group() method.
setosa_group = class_group.get_group('Iris-setosa')
print(setosa_group)

# To get Aggregated results of grouped data, we can use .aggregatfunction-name() on any numeric column 
# eg, get count of column petalwidth for each group,
petalwidth_count = class_group.petalwidth.count()
print(petalwidth_count)
# eg, get sum of sepalwidth column fr each group.
sepalwidth_sum = class_group.sepalwidth.sum()
print(sepalwidth_sum)
# eg, get mean operation on sepallength column for each group.
sepallength_mean = class_group.sepallength.mean()
print(sepallength_mean)