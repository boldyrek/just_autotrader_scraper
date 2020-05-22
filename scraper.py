import urllib
import urllib.request
import html.parser
from bs4 import BeautifulSoup
import requests
import html_text
import sys
import re
import pandas as pd
from time import sleep
import os
import uuid
"""
first need to spoof that we are using some kind of coockies probably
"""
#page = int(sys.argv[1])
#last_page = int(sys.argv[2])
page = 1
last_page = 3000
import time, os, fnmatch, shutil

def get_pics(img_hrefs):
    car_dir = str(uuid.uuid4())
    directory = 'pics/' + car_dir + '/'
    if not os.path.isdir(directory):
        os.mkdir(directory)
    i=0
    for href in img_hrefs:
        print('downloanding :', href)
        response = requests.get(href)
        if response.status_code == 200:
            image_name = directory + str(i) + "image.jpg"
            f = open(image_name, "wb")
            f.write(response.content)
            i+=1
    return car_dir

def get_text(href):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    req = requests.get(href, headers=headers)
    html = req.text
    text = html_text.extract_text(html)
    return text, html 


def grab_data(html):
    #print(html)
    price = re.findall('.*\$[. ]*(\d*\,\d*)', html, re.MULTILINE)
    if len(price) == 0:
        price = 0
    #price = re.findall('987', html, re.MULTILINE)
    data = [price]# return a list so we can appen d later to it
    return data 

def get_img_links( html, main_link):

    # get image links from a page, those link that have 1024*786 resolution

    fi = open('html.txt','w')
    fi.write(html)
    found = re.findall(r'(https?://tdrp[^\s"]+)', html)
    fi = open('links.txt','w')
    fi.write(str(found))
    im_li = [elm for elm in found if '1024x786' in elm] 

    return im_li

def save_to_csv(first_run,data,file_name):
        #Save data to csv
        if first_run:
            df= pd.DataFrame(data, columns =  ['price','directory'])  # adding a row
        else:
            df_new= pd.DataFrame(data, columns = ['price','directory'])  # adding a row
            df = df.append(df_new)
        df.to_csv('csv/'+file_name, index = False) # not sure if header should be not false

######### MAIN PAGE ##################

t = time.localtime()
timestamp = time.strftime('%b-%d-%Y_%H%M', t)
columns = ['date','vin','make','model','price','year','trim','mileage','state','link']
first_run = True
file_name = str(page) +'to' + str(last_page) + timestamp + '.csv' 
for i in range(1734,3000):
    i = i*30
    page = "https://www.autotrader.ca/cars/on/richmond%20hill/?rcp=30&rcs={0}&srt=3&prx=100&prv=Ontario&loc=L4E5A7&hprc=True&wcp=True&sts=New-Used&inMarket=basicSearch".format(i)
    text, html = get_text(page) 
    soup = BeautifulSoup(html,features="lxml")
    elms_a = soup.findAll('a', href=re.compile("/a/"))
    hrefs = set() 
    for elm in elms_a:
        href = elm.get('href')
        hrefs.add(href)
    for href in hrefs:
        main_link = 'https://www.autotrader.ca'   
        full_link = main_link + href  
        print('********* NEW CAR PAGE **********',full_link)
        text, html = get_text(full_link)
        data  = grab_data(html)
        data.append(full_link)
        # because there are other photos on a page
        img_hrefs = get_img_links(html,main_link)
        print(data) # see what is wrong with an error the object is not subscriptable
        price = data[0][0]#need to read price to pass it to the get_pics
    
        print(price)
        print(img_hrefs)
        
        if isinstance(price,type('abc')):
            car_dir = get_pics(img_hrefs)
        data = [[data[0][0],car_dir]]
        
        save_to_csv(first_run,data,file_name)
        print(data)
        first_run = False
        exit()    


