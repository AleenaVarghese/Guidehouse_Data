import camelot
import pandas as pd
import numpy as np

full_path = "./AD1_CO42602_1107945_Vcu Health Systems_DBS_20190927_20230514.pdf"

'''
Camelot
#tables = camelot.read_pdf(full_path, pages="all")#, flavor = "stream",encoding='utf-8')
try:
	#for idx, tbl in enumerate(tables):    
	#    tables[idx].df.to_csv(os.path.join("./output","table_"+str(idx)+".csv"))
	tables = camelot.read_pdf(full_path, pages="all")
	print(tables)
except Exception as e:
    print(".........................!",e,e.args)
'''
import os
import ocrmypdf 
#ocrmypdf --skip-text --pages 3 f1.pdf out.pdf
from PyPDF2 import PdfFileWriter, PdfFileReader

def split_pdf(invoice_pdf):
	inputpdf = PdfFileReader(open(invoice_pdf, "rb"))
	if not os.path.exists(os.path.join("output",invoice_pdf)):
		os.makedirs(os.path.join("output",invoice_pdf))
	for i in range(inputpdf.numPages):
		output = PdfFileWriter()
		output.addPage(inputpdf.getPage(i))
		with open(os.path.join("output",invoice_pdf,"document-page%s.pdf" % i), "wb") as outputStream:
			output.write(outputStream)



if __name__ == '__main__':
	invoice_pdf = '2ndpage.pdf'
	invoice_pdf = 'f1.pdf'
	#split_pdf(invoice_pdf)
	try:		
		a = ocrmypdf.ocr(invoice_pdf,"./output/out-2ndpage.pdf", deskew=True,skip_text=True,pages=7)
	except Exception as e:
		print("...",e)

