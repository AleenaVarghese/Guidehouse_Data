import pandas as pd
import numpy as np 

filename = 'inputdata.csv'
df= pd.read_csv(filename)
'''print(df.head(1))
print("***************************")
print(df.tail(1))
print("***************************")
print(df.info())'''
print("***************************")
#df.to_excel("testfile.xlsx",sheet_name= "test sheet",index =False)
#pd.read_excel("testfile.xlsx", sheet_name="test sheet")
test_var = df[["Category Group","scraped_Vendor_name","Vendor_name_confidence"]]
#print(test_var.head())
#print(type(test_var))
#print(df["scraped_Vendor_name"])
#print(df.describe())
#print(np.count_nonzero(df["Members Submitting"]))
print(df.fillna(0))
print("***************************")