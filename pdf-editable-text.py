import os
import ocrmypdf 
#ocrmypdf --skip-text --pages 3 f1.pdf out.pdf
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import ntpath
import pathlib
import sys
import time
import pdfplumber


if __name__ == '__main__':
    pdf_files = sorted(map(lambda p: str(p.resolve()), list(pathlib.Path('input').rglob('*.[Pp][Dd][Ff]'))))
    
    for idx,pdf_f in enumerate(pdf_files):
        out_file = pdf_f.replace("\input\\","\Editable-Pdf\\")
        txt_file = pdf_f.replace("\input\\","\output\\").rpartition(".")[0]+".txt"
        #Convert Scanned PDF to Editable PDF
        ocrmypdf.ocr(pdf_f,out_file, deskew=True,force_ocr=True)
        #Text File for each pdf
        f = open(txt_file,'w')
        with pdfplumber.open(out_file) as pdf:
            for page_no,page in enumerate(pdf.pages):
                text = page.extract_text(x_tolerance=2)
                print("==",text)
                f.write(text)
    
