import camelot
import pandas as pd
import numpy as np

full_path = r"C:\Users\avarghese\Desktop\test poc\PDF Extracter\Editable-Pdf\f2.pdf"
file_name = full_path.rpartition("\\")[-1].rpartition(".")[0]
import pdfplumber
import os 
#Camelot
#tables = camelot.read_pdf(full_path, pages="all")#, flavor = "stream",encoding='utf-8')
try:
	#for idx, tbl in enumerate(tables):    
	#    tables[idx].df.to_csv(os.path.join("./output","table_"+str(idx)+".csv"))
    tables = camelot.read_pdf(full_path, pages="all")#, flavor = "lattice")
    print(full_path,tables)
    for idx, tbl in enumerate(tables):    
        tables[idx].df.to_csv(os.path.join("./output",str(file_name)+"-table_"+str(idx)+".csv"))
    '''with pdfplumber.open(full_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text(x_tolerance=2)
        print("==",text)
        f = open(os.path.join("./output","table_"+str(idx)+".txt"),'w')
        f.write(text)
    '''
except Exception as e:
    print(".........................!",e,e.args)