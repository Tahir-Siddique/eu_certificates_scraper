#!/usr/bin/env python
# coding: utf-8

from seleniumbase import SB
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd

AUTH_TOKEN = None
def open_the_turnstile_page(sb):
    sb.driver.uc_open_with_reconnect(
        "https://eudragmdp.ema.europa.eu/inspections/gmpc/searchGMPCompliance.do", reconnect_time=1,
    )

df = pd.read_csv("certificates7.csv")

data = df.to_dict('records')
_data = pd.read_csv("output7.csv").to_dict('records')
with SB(uc=True, test=True, headless=True) as sb:
    for idx, item in enumerate(data):
        try:
            certifcate_number = item.get("Certificate Number")
            if certifcate_number in [x.get("Certificate Number") for x in _data]:
                continue
            print("="*10)
            print(certifcate_number)
            print("="*10)
            open_the_turnstile_page(sb)
            sb.driver.implicitly_wait(100)
            sb.driver.find_element(By.NAME, "certificateNumber").send_keys(certifcate_number)
            sb.driver.execute_script('document.getElementsByName("country")[0].options.selectedIndex = 1')
            sb.driver.find_element(By.ID, "btnSearchGMPCLabel").click()
            # Find elements with cellspacing="1" using CSS selector

            # Wait for the table to load
            time.sleep(1)

            # Sort the table by the "Certificate Number" column
            sb.driver.find_element(By.XPATH, "//a[contains(text(),'Certificate Number')]").click()

            # Wait for the table to sort
            time.sleep(1)

            # Click on the first link in the sorted table
            first_link_in_table = sb.driver.find_element(By.XPATH, "//table[contains(@class,'ibody')]//tr[@class='even']/td[@class='cl']/a")
            if first_link_in_table:
                first_link_in_table.click()
                # Wait for the new page to load
                time.sleep(1)

                # Save the HTML code of the page in a variable
                html_code = sb.driver.page_source

                # Assuming html_code contains the HTML code
                soup = BeautifulSoup(html_code, 'html.parser')

                # Find the div with the specified id
                div_content = soup.find('div', id='table_mfgOperations_IMP')
                d = {
                    "Certificate Number": item.get("Certificate Number"),
                    "Certificate": ""
                }
                if div_content:
                    div_text_content = div_content.get_text(separator=' ', strip=True).replace('\xa0', ' ').replace('\n', ' ').replace('\t', ' ')
                    d["Certificate"] = div_text_content
                _data.append(d)    
                pd.DataFrame(_data).to_csv("output7.csv", index=False)
            open_the_turnstile_page(sb)
        except Exception as e:
            print(e)
            continue

        # Close the browser
    sb.driver.close()