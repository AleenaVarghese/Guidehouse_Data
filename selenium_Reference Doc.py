from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['acceptSslCerts']=True
capabilities['acceptInsecureCerts']=True
#chrome_options.headless = True

#WebDriverWait(driver,MAX_WAIT).until(EC.visibility_of_element_located((By.xpath,'')))
DRIVER_PATH = str(os.getcwd())+ '\chromedriver.exe' 
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=DRIVER_PATH)
div_select = Select(driver.find_element_by_tag_name("select"))
for div_new_option in div_select.options:
	pass
	
with open ('./BSC.csv','r') as inp_f, \
		open('./BSC_data.csv','w', newline='') as op_f:
		writer = writer = csv.writer(op_f)
		reader = csv.DictReader(inp_f)
		writer.writerow(header_list)
		for idx, row in enumerate(reader):
			main_url = row["URL"]

with open ('./config/zip_config.csv','r') as conf_f:
	reader = csv.DictReader(conf_f)
	for idx, row in enumerate(reader):
		zip_list.append(row["ZipCodes"])

if __name__ == "__main__":
	obj = USFC()