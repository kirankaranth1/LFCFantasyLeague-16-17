#from __future__ import print_function
import re
import requests
from lxml import html
from io import StringIO
import sys
import os
import json
import math
import signal


def downloadPage(url):
    
    page = requests.get(url)    
    return page

name_xpath=".//*[@id='ismr-side']/div/section/h2"
f = open('playerIDs.txt')
for line in iter(f):
    url="https://fantasy.premierleague.com/a/entry/"+str(line).strip()+"/history"
    #print(url)
    page=downloadPage(url)
    tree = html.parse(StringIO(page.text)).getroot()
    name=tree.xpath(name_xpath)
    print(str(name)+" "+str(line))
f.close()


