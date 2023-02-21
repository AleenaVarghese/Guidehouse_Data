# Packages for scraping
#import pyodbc # library used for Pandas
import pyautogui # library for Keystroke Operation
import time    # for Time waiting on driver
import random
import csv
from datetime import datetime
from lxml import html  # used to use Xpath
from time import sleep
from random import randint
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys   # For feeding user creditials
from selenium.webdriver.common.action_chains import ActionChains
import requests
import json
import pandas as pd
import os
from datetime import date
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities

from core.helpers import JSON_OP_DIRECTORY_VENDOR, VENDOR_NAME_LIST_FILE, OUTPUT_FILE_VENDOR

vendor_dict = dict()
with open (VENDOR_NAME_LIST_FILE,'r') as conf_f:
    reader = csv.DictReader(conf_f)
    for idx, row in enumerate(reader):
        vendor_dict[row['VendorKey']] = row['VendorName']

PAGE_SIZE = 10000
current_year = date.today().strftime('%m/%Y')
prev_year = current_year.replace(current_year.partition("/")[2], str(int(current_year.partition("/")[2]) - 1) )
#clean month
if current_year.partition("/")[0].strip() != "01":
  current_year = current_year.replace(current_year.partition("/")[0],str(int(current_year.partition("/")[0]) - 1))
  prev_year = prev_year.replace(prev_year.partition("/")[0],str(int(prev_year.partition("/")[0]) - 1))
else:
  current_year = current_year.replace("01/","12/")
  prev_year = prev_year.replace("01/","12/")
if len(current_year.partition("/")[0].strip()) == 1:
  current_year = "0"+current_year
  prev_year = "0"+prev_year
  
DATA_URL = "https://supplyguidedb.ecri.org/National/HierarchyBinding_NationalDetail"

data_dict = {}#Form data
data_dict["sort"] = ""
data_dict["page"] = "1"
data_dict["pageSize"] = str(PAGE_SIZE)
data_dict["group"] = ""
data_dict["filter"] = ""
data_dict["GroupingColumnKey"] = ""
data_dict["GroupingColumnName"] = ""
data_dict["OptionalColumns[0]"] = "Vendor"
data_dict["OptionalColumns[1]"] = "ConversionFactor"
data_dict["searchFilterPanelModel.StartDate"] = prev_year
data_dict["searchFilterPanelModel.EndDate"] = current_year
data_dict["searchFilterPanelModel.SelectedVendorKeys"] = ""
data_dict["searchFilterPanelModel.SelectedVendorDesc"] = ""
data_dict["searchFilterPanelModel.VendorCatalogNumber"] = ""
data_dict["searchFilterPanelModel.SelectedManufacturerKeys"] = ""
data_dict["searchFilterPanelModel.SelectedManufacturerDesc"] = ""
data_dict["searchFilterPanelModel.ManufacturerCatalogNumber"] = ""
data_dict["searchFilterPanelModel.SelectedCategoryGroupId"] = ""
data_dict["searchFilterPanelModel.SelectedCategoryGroupDesc"] = "" 
data_dict["searchFilterPanelModel.SelectedCategoriesKeys"] = ""
data_dict["searchFilterPanelModel.SelectedCategoriesDesc"] = ""
data_dict["searchFilterPanelModel.Items"] = ""
data_dict["searchFilterPanelModel.ItemsDesc"] = ""
data_dict["searchFilterPanelModel.SelectedItemKey"] = ""
data_dict["searchFilterPanelModel.SelectedUOMKey"] = ""
data_dict["searchFilterPanelModel.SelectedDepartmentKeys"] = ""
data_dict["searchFilterPanelModel.Department"] = ""
data_dict["searchFilterPanelModel.SelectedFacilityKeys"] = ""
data_dict["searchFilterPanelModel.Facility"] = ""
data_dict["searchFilterPanelModel.CheckedBedSizeValues"] = ""
data_dict["searchFilterPanelModel.CheckedRegionValues"] = ""
data_dict["searchFilterPanelModel.CheckedHealthSystemPriceRangeValues"] = ""
data_dict["searchFilterPanelModel.CheckedAdmissionsRangeValues"] = ""
data_dict["searchFilterPanelModel.CheckedInpatientDaysRangeValues"] = ""
data_dict["searchFilterPanelModel.CheckedCaseMixIndexRangeValues"] = ""
data_dict["searchFilterPanelModel.MemberItemSpend"] = ""
data_dict["searchFilterPanelModel.SelectedPieSeries"] = ""
data_dict["searchFilterPanelModel.Source"] = ""
data_dict["searchFilterPanelModel.SimpleSearchText"] = ""
data_dict["searchFilterPanelModel.SearchSavedTag"] = ""
data_dict["OrderBy"] = "Total Spend"

header_dict = {}
header_dict["origin"] = "//supplyguidedb.ecri.org"#"https://priceguidedb.ecri.org"
header_dict["pragma"] = "no-cache"
header_dict["referer"] = "https://supplyguidedb.ecri.org/national/national"
header_dict["sec-ch-ua"] = '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"'
header_dict["sec-ch-ua-mobile"] = "?0"
header_dict["sec-fetch-dest"] = "empty"
header_dict["sec-fetch-mode"] = "cors"
header_dict["sec-fetch-site"] = "same-origin"
header_dict["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
header_dict["x-requested-with"] = "XMLHttpRequest"


dateTimeObj = datetime.now()
date_filename = dateTimeObj.strftime('%m_%d_%y%y_%H_%M_%S')

def merge_to_csv():
  """
  Load data into csv forat from json.  
  """
  headers = [
        'Category Group',
        'Vendor',
        'Vendor Catalog Number',
        'Manufacturer',
        'Manufacturer Catalog Number',
        'Description',
        'UOM',
        'Conversion Factor',
        'National Usage',
        'National Spend',
        'PG Low',
        '25th',
        'PG Median',
        '75th',
        'PG High',
        'Members Submitting',
        'Category Name',
        'Scrape date',
        #'Total Records Available in Website',
        ]
  list_out = []
  for each_file in os.listdir(JSON_OP_DIRECTORY_VENDOR):
    if not each_file.endswith('.json'):
      continue
    print(each_file)
    try:
      json_data = json.load(open(os.path.join(JSON_OP_DIRECTORY_VENDOR , each_file), encoding="utf-8", errors='ignore'), strict=False)
      for each_record in json_data['Data']:
            #print(each_record)
            vendor = str(each_record['VendorName']).replace(",", " ")
            vendor_catalog = str(each_record['VendorCatalogNumber']).replace(",", " ")
            manafacturer = str(each_record['ManufacturerName']).replace(",", " ")
            manafacturer_catalog = \
                str(each_record['ManufacturerCatalogNumber']).replace(",", " ")
            description = str(each_record['ItemDesc']).replace(",", " ")
            uom = str(each_record['UOM']).replace(",", " ")
            conversion_factor = str(each_record['ConversionFactorUnits']).replace(",", " ")
            national_usage = str(each_record['TotalUsage']).replace(",", " ")
            national_spend = str(each_record['TotalSpend']).replace(",", " ")
            low = str(each_record['PGLow']).replace(",", " ")
            twenty_fifth = str(each_record['FirstQuartilePrice']).replace(",", " ")
            median = str(each_record['PGAvg']).replace(",", " ")
            seventy_fifth = str(each_record['ThirdQuartilePrice']).replace(",", " ")
            high = str(each_record['PGHigh']).replace(",", " ")
            memebers_submitting = str(each_record['MemberInterest']).replace(",", " ")
            category = str(each_record['CategoryName']).replace(",", " ")
            
            list_out.append([
                'Vendor Name',
                vendor,
                vendor_catalog,
                manafacturer,
                manafacturer_catalog,
                description,
                uom,
                conversion_factor,
                national_usage,
                national_spend,
                low,
                twenty_fifth,
                median,
                seventy_fifth,
                high,
                memebers_submitting,
                category,
                date.today(),
                #json_data['Total'],
                ])
    except:
      pass
  print("To csv")
  df = pd.DataFrame(list_out, columns=headers)
  df.to_csv(OUTPUT_FILE_VENDOR, index=False)
  print("DUMPED DOWNLOADED DATA TO CSV")
	
def delete_files():
  """
  Deleting json files after convering into csv
  """
  for each_file in os.listdir(JSON_OP_DIRECTORY_VENDOR):
    if not each_file.endswith(".json"):
      continue
    os.remove(os.path.join(JSON_OP_DIRECTORY_VENDOR,each_file))

def refresh_page(driver):
  """
  In some cases data may not be loaded from backend so, We should try refreshing page.
  """
  driver.refresh()
  time.sleep(5)
  s = requests.Session()
  cookies = driver.get_cookies()
  for cookie in cookies:
    s.cookies.set(cookie['name'], cookie['value'])
  return s, driver

def download_json(VendorKey_str, vendor_desc_txt, chunk_no, driver,  s):
  """
  Downloading Json data using vendor name list chunks of 10.
  """
  print('DOWNLOADING DATA USING VENDOR NAME FN')    
  key_list_temp = [str(key) for key in vendor_dict.keys()]
  val_list_temp = [str(val) for val in vendor_dict.values()]
  for i in range(1, 10000):
      data_dict['page'] = i      
      data_dict["searchFilterPanelModel.SelectedVendorKeys"] = VendorKey_str
      data_dict["searchFilterPanelModel.SelectedVendorDesc"] = vendor_desc_txt
      retry = 0
      while True:
          response = s.post(DATA_URL, headers=header_dict,
                          data=data_dict )
          if response.status_code == 200:
            break
          if retry == 5:
            print('INITIAL RETRY FAILED REFRESHING PAGE')
            s, driver = refresh_page(driver)
          if retry == 10:
            print('RETRYING FAILED')
            break
          retry += 1
          #time.sleep(10)
          sleep(randint(8,15))
          print('RETRYING')
      with open(os.path.join(JSON_OP_DIRECTORY_VENDOR , 'ECRI' + '_' + str(chunk_no) +'-chunk-'+ str(i) + '.json')
                , 'w', encoding="utf-8") as opfile:
          opfile.write(response.text)
      print('DOWNLOADED VENDOR LIST -' + str(i))
      if len(json.loads(response.text)['Data']) < PAGE_SIZE:
          print('COMPLETED DOWNLOADING!!!!')
          break
  return driver

def Data_Scraper_vendor(driver):
  """
  Program starts here

  """   
  key_list_temp = [str(key) for key in vendor_dict.keys()]
  val_list_temp = [str(val) for val in vendor_dict.values()] 
  s = requests.Session()
  cookies = driver.get_cookies()
  for cookie in cookies:
    s.cookies.set(cookie['name'], cookie['value'])
  
  start = 0
  
  for i in range(0,len(key_list_temp),10): 
    #Dividing vendor name data into chunks of 10 for getting maximum data
    key_list = [str(key) for key in key_list_temp[start:i]]
    val_list = [str(val) for val in val_list_temp[start:i]] 
    VendorKey_str = ','.join(key_list)
    vendor_desc_txt = ",".join(val_list)
    
    start = i
    if len(key_list) >0:
      driver = download_json(VendorKey_str, vendor_desc_txt, i, driver, s)
      
  final_chunk = len(key_list_temp)/10
  final_chunk_multiple = int(final_chunk) * 10
  if final_chunk != final_chunk_multiple:
    # To fetch the data of remaining portion - reminder section after dividing the list into chunks of 10
    key_list = [str(key) for key in key_list_temp[final_chunk_multiple:len(key_list_temp)]]
    val_list = [str(val) for val in val_list_temp[final_chunk_multiple:len(key_list_temp)]] 
    VendorKey_str = ','.join(key_list)
    vendor_desc_txt = ",".join(val_list)
    if len(key_list) >0:
      driver = download_json(VendorKey_str, vendor_desc_txt, len(key_list), driver, s)

  merge_to_csv()
    
  

    
