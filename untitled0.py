# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 11:12:10 2023

@author: edgar
"""

from selenium import webdriver
import os
path=os.getcwd()+'/bin/geckodriver.exe'
#path=os.path.dirname(os.getcwd())+'/bin/'
print (path)
driver = webdriver.Firefox()
# driver.get("https://dev.to")
 
# driver.find_element_by_id("nav-search").send_keys("Selenium")


