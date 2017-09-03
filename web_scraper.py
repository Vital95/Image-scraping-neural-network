from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import proxy, desired_capabilities
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
import os
import codecs
import unittest, time, re
import random
from multiprocessing import Pool
import multiprocessing
import logger

allText = list()

proxyList = [
    #'58.11.178.232:3128',
   # '61.93.246.49,3128',
    #'36.232.227.141:8888',
    #'190.153.55.86:6588',
    '172.93.148.247:3128',
    '173.255.233.249:8888',
    '8.33.234.3:80'
]

#make string from tuples of data
def MakeString(data):
    string = ''
    for link, source in data:
        string = string + link + "\n" + source + "\n"
    return string

def GetRandomProxy(proxyList):
    return random.choice(proxyList)

def setUp(inputData):
    proxy = None
    sleepTime = 3
    maxScrols = 20
    url, proxy, sleepTime, maxScrols = inputData
    print(1)
    if(proxy is None):
        PROXY = "191.252.103.93:8080"
    else:
        PROXY = proxy
    desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
    desired_capabilities['proxy'] = {
    "httpProxy":PROXY,
    "ftpProxy":PROXY,
    "sslProxy":PROXY,
    "noProxy":None,
    "proxyType":"MANUAL",
    "class":"org.openqa.selenium.Proxy",
    "autodetect":False
    }
    executable_path = "E:\Master_G\Moduls\chromedriver.exe"
    os.environ["webdriver.chrome.driver"] = executable_path
    driver = webdriver.Chrome(executable_path = executable_path,desired_capabilities=desired_capabilities)
    driver.implicitly_wait(sleepTime)
    base_url = url
    verificationErrors = []
    accept_next_alert = True
    delay = sleepTime
    driver.get(base_url)
    for i in range(0, maxScrols):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleepTime)
        if(i == maxScrols - 1):
            html_source = driver.page_source
            linkData = url, html_source
            string = MakeString(linkData)
            logger.LogFromTread(string, file_name = 'test.log')
    driver.quit()
    
with open("new_blonde links.txt", encoding="utf-8") as file:
    my_list = file.readlines()

#to do create tuple unpack 
tupleList = list()
for item in my_list:
    proxy = GetRandomProxy(proxyList)
    sleepTime = 5
    maxScrols = 10
    tupleTmp =  item, proxy, sleepTime, maxScrols
    tupleList.append(tupleTmp)

if __name__ == '__main__':
        pool = Pool(processes = multiprocessing.cpu_count())
        pool.map(setUp, tupleList)

'''
for url in my_list:
    try:
        print(url)
        prox = GetRandomProxy(proxyList)
        setUp(url = url.strip(), proxy = prox, sleepTime = 3, maxScrols = 10)
    except Exception as exp:
        print(exp.args)
        pass
'''

#with codecs.open("tets.txt", "w", "utf-16") as stream:   # or utf-8
#    stream.write(string)
