import camelot
import pandas as pd
import numpy as np

full_path = "102848_PS-00142696_May2021-02.pdf"

tables = camelot.read_pdf(full_path, pages="all")#, flavor = "stream",encoding='utf-8')
try:
    #for idx, tbl in enumerate(tables):    
    #    tables[idx].df.to_csv(os.path.join("./output","table_"+str(idx)+".csv"))
    print(tables)
except Exception as e:
    print(".........................!",e,e.args)