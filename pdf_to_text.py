'''Read PDF files and extract all text (pdftotext or OCR)'''

# standard libraries
import io
import ntpath
import os
import pathlib
import sys
import time

import multiprocessing as mp
from multiprocessing.dummy import Pool as ThreadPool

import subprocess as sp

import PyPDF2
import pdfminer
import pdfminer.high_level
import pdfminer.layout


def get_pdf_text_v1(full_path):
    ''' Reads text from each page using PyPDF2. '''
    all_pages = {}
    with open(full_path, 'rb') as file_in:
        pdf = PyPDF2.PdfFileReader(file_in)
        for page_index in range(pdf.getNumPages()):
            all_lines = ''
            try:
                all_lines = pdf.getPage(page_index).extractText()
            except Exception as error:
                print(str(error))
            all_lines = all_lines.strip()
            if all_lines:
                all_pages[page_index + 1] = all_lines
    return all_pages

def get_pdf_text_v2(full_path):
    ''' Reads text from each page using pdfminer. '''
    all_pages = {}
    with open(full_path, 'rb') as file_in:
        total_pages = len(list(pdfminer.high_level.extract_pages(file_in)))
        for page_index in range(total_pages):
            buffer = io.StringIO(newline=None)
            all_lines = ''
            try:
                pdfminer.high_level.extract_text_to_fp(inf=file_in, outfp=buffer, laparams=pdfminer.layout.LAParams(),
                                                       maxpages=1, page_numbers=[page_index])
                all_lines = buffer.getvalue()
            except Exception as error:
                print(str(error))
            finally:
                buffer.close()
            all_lines = all_lines.strip()
            if all_lines:
                all_pages[page_index + 1] = all_lines
    return all_pages

def get_pdf_text_ocr(full_path):
    ''' Gets PDF readable text. '''
    all_pages = {}
    output_dir = os.path.splitext(full_path)[0]
    txt_files = [os.path.join(output_dir, filename) for filename in os.listdir(output_dir) if filename[-4:] == '.txt']
    for filepath in txt_files:
        filename = ntpath.basename(filepath)
        hyphen_loc = filename.rfind('-')
        page_number = int(filename[hyphen_loc+1:-len('.tif.txt')])
        try:
            with open(filepath, 'r') as file_in:
                all_pages[page_number] = file_in.read()
        except Exception as error:
            print(str(error))
    return all_pages

def get_pdf_text(argument):
    ''' Calls the corresponding get_pdf_text function. '''
    which, full_path = argument
    try:
        pages = globals()['get_pdf_text_{}'.format(which)](full_path)
    except Exception as error:
        pages = {}
        print(str(error))
    return pages

def pdf_text_merger(full_path):
    ''' Tries to extract text from this PDF. '''
    arguments = [
        ('v1', full_path),
        ('v2', full_path),
        ('ocr', full_path),
    ]
    with mp.Pool(processes=3) as pool:
        pages_v1, pages_v2, pages_ocr = pool.map(get_pdf_text, arguments)
    page_numbers_list = set(pages_v1.keys())
    page_numbers_list.update(pages_v2.keys())
    page_numbers_list.update(pages_ocr.keys())
    total_pages = max(page_numbers_list)
    pages_max_digits = len(str(total_pages))
    pages_max_digits = 5
    output_dir = os.path.splitext(full_path)[0]
    output_template = os.path.splitext(os.path.basename(full_path))[0]
    for page_number in range(1, total_pages + 1):
        all_lines = ''
        if page_number in pages_ocr:
            all_lines += '\n\n\nOCR\n\n\n' + pages_ocr[page_number]
        if page_number in pages_v1:
            all_lines += '\n\n\nPyPDF2\n\n\n' + pages_v1[page_number]
        if page_number in pages_v2:
            all_lines += '\n\n\npdfminer.six\n\n\n' + pages_v2[page_number]
        if all_lines:
            try:
                with open('{dir}/{template}-{page}.tif.txt'.format(dir=output_dir, template=output_template,
                                                                   page=str(page_number).zfill(pages_max_digits)), 'w',encoding='utf-8') as file_out:
                    file_out.write(all_lines)
            except Exception as error:
                print(str(error))


def merge_text_files(pdf_files):
    ''' Extract text from PDFs and merge with OCR files. '''
    max_processes = int(mp.cpu_count() / 3)
    with ThreadPool(processes=max_processes) as pool:
        return pool.map(pdf_text_merger, pdf_files)


PDF2TIFF_TEMPLATE_CMD = [
    'cd "{work_dir}"',
    #'convert -density 300 "{filename}" -depth 8 -strip -background white -alpha off -scene 1 "{template}-%05d.tif"', # >/dev/null 2>&1',
    'convert -density 200 "{filename}" -depth 8  -background white -alpha off -scene 1 "{template}-%05d.tif"', # >/dev/null 2>&1',
    'cd "{final_dir}"',
]
def pdf_processor(full_path):
    ''' Extract pages as images from PDF. '''
    cwd = os.getcwd()
    output_dir = os.path.splitext(full_path)[0]
    try:
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
    except OSError as error:
        print('Cannot create output directory {}: {}'.format(output_dir, error))
        return
    output_template = os.path.splitext(os.path.basename(full_path))[0]
    cmd = ';'.join(PDF2TIFF_TEMPLATE_CMD).format(work_dir=output_dir, dpi=200, filename=full_path, template=output_template, final_dir=cwd)
    try:
        sp.run(cmd, shell=True, check=True)
    except sp.SubprocessError as error:
        print('Failed converting PDF {} to images: {}.'.format(output_template, str(error)))

def process_pdf_files(pdf_files):
    ''' Process PDF files and convert to TIFF. '''
    max_processes = int(mp.cpu_count() - 2)
    with ThreadPool(processes=max_processes) as pool:
        return pool.map(pdf_processor, pdf_files)


OCR_TEMPLATE_CMD = [
    'cd "{work_dir}"',
    'cp "{filename}" "{filename}.tif" >/dev/null 2>&1',
    'tesseract "{filename}.tif" "{filename}" --tessdata-dir /$HOME/tessdata/ >/dev/null 2>&1',
    'cd "{final_dir}"',
]

def tiff_to_text_worker(full_path):
    ''' Comvert image to text with OCR. '''
    if full_path[-len('.tif.tif'):] == '.tif.tif':
        return
    cwd = os.getcwd()
    output_dir = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    cmd = ';'.join(OCR_TEMPLATE_CMD).format(work_dir=output_dir, filename=filename, threshold='50%', zoom='250%', final_dir=cwd)
    try:
        sp.run(cmd, shell=True, check=True)
    except sp.SubprocessError as error:
        print('Failed OCR of {}: {}.'.format(filename, str(error)))

def process_tiff_files(tiff_files):
    ''' Process TIFF files and extract text using OCR. '''
    max_processes = int(mp.cpu_count() / 4)
    with ThreadPool(processes=max_processes) as pool:
        return pool.map(tiff_to_text_worker, tiff_files)


def main_process(working_path):
    ''' Generates list of PDF files and extract text from each of them. '''
    start_time = time.time()
    pdf_files = sorted(map(lambda p: str(p.resolve()), list(pathlib.Path(working_path).rglob('*.[Pp][Dd][Ff]'))))
    process_pdf_files(pdf_files)
    tiff_files = sorted(map(lambda p: str(p.resolve()), list(pathlib.Path(working_path).rglob('*.[Tt][Ii][Ff]'))))
    process_tiff_files(tiff_files)
    merge_text_files(pdf_files)
    print('--- {} seconds ---'.format(time.time() - start_time))


if __name__ == '__main__':
    main_process(working_path='./input')
    sys.exit(0)
