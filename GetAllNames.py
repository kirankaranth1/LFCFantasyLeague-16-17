# -*- coding: utf-8 -*-
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
import time

success = True
wd = WebDriver()
wd.implicitly_wait(60)

def is_alert_present(wd):
    try:
        wd.switch_to_alert().text
        return True
    except:
        return False
pfile=open("PList.csv",'w')
try:
    f = open('playerIDs.txt')
    for line in iter(f):
        url="https://fantasy.premierleague.com/a/entry/"+str(line).strip()+"/history"
        wd.get(url)
        name=wd.find_element_by_css_selector("h2.subHeader.ism-sub-header").text
        
        print(str(name)+","+str(line),file=pfile)
    
finally:
    wd.quit()
    if not success:
        raise Exception("Test failed.")
