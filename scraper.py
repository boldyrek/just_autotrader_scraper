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
from libs.get_car_features import *
import time, os, fnmatch, shutil

"""
first need to spoof that we are using some kind of coockies probably
"""
#page = int(sys.argv[1])
#last_page = int(sys.argv[2])
page = 1
last_page = 3000
data_dir = "pic4"


def reliable_request(href):
    """
    catch all connection errors wait and try again
    return response
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    done = False
    while not done:
        try:
            resp = requests.get( href, headers = headers )
        except Exception as e:
           print('connection error', e)
           time.sleep(5)
        else:
           done = True
    return resp


def download_pics( img_hrefs, directory ):
    # downloading pics of the car
    i=0
    for href in img_hrefs:
        print('downloanding :', href)
        #response = requests.get(href)
        response = reliable_request(href)
        if response.status_code == 200:
            image_name = str(i) + "image.jpg"
            f = open( data_dir + '/' + directory + '/' + image_name, "wb")
            f.write(response.content)
            i+=1
    return True 


def get_text_html( href ):

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    #req = requests.get(href, headers=headers)
    req = reliable_request(href)
    html = req.text
    text = html_text.extract_text(html)

    return text, html 


def parse_car_page( html ):
    #print(html)
    #price = re.findall('.*\$[. ]*(\d*\,\d*)', html, re.MULTILINE)
    price = re.findall('ce":"(\d*)', html, re.MULTILINE)
    print(price)
    if len(price) == 0:
        price = 0
        return price
    #price = re.findall('987', html, re.MULTILINE)
    else: return price[1] 


def get_img_links( html, main_link):

    # get image links from a page, those link that have 1024*786 resolution

    fi = open('html.txt','w')
    fi.write(html)
    found = re.findall(r'(https?://tdrp[^\s"]+)', html)
    fi = open('links.txt','w')
    fi.write(str(found))
    im_li = [elm for elm in found if '1024x786' in elm] 

    return im_li


def save_to_csv( df, data, file_name ):

    #Save data to csv
    
    df = df.append(data, ignore_index = True)# if we don't put ignor index it produces an error
    
    df.to_csv('csv/'+file_name, index = False) # not sure if header should be not false

    return df


def get_all_hrefs(html):
    soup = BeautifulSoup(html,features="lxml")
    anchors = soup.findAll('a', href=re.compile("/a/")) # getting html anchors
    # get all all the hypertext references from the anchors on a page
    hrefs = set() # href stands for hypertext reference 
    for a in anchors:
        href = a.get('href') # get the link "a" destination, href specifies the location of a resource, or location of linked resource
        hrefs.add(href)
    return hrefs


def write_html_text(html, text, directory):
    
    f1 = open( data_dir + "/" + directory  + 'html.txt','w') 
    f1.write( html )
    f1.close()
    f2 = open( data_dir + "/" + directory +  'text.txt','w') 
    f2.write( text )

 
def create_and_get_new_directory():
    dir_name = str(uuid.uuid4())
    full_dir = data_dir + '/' + dir_name + '/'
    if not os.path.isdir(full_dir):
         os.mkdir(full_dir)
    return dir_name


def is_duplicate(df, car_url):
    index = df[df.car_page == car_url].index
    if len(index) > 0: # if there are duplicat urls remove them
       print('duplicate url', car_url)
       return True
    return False
            
            
            
 ###### MAIN PAGE ##################


t = time.localtime()
timestamp = time.strftime('%b-%d-%Y_%H%M', t)
columns = ['date','vin','make','model','price','year','trim','mileage','state','link']
first_run = True
file_name = str(page) +'to' + str(last_page) + timestamp + '.csv' 
print(file_name)
df = pd.DataFrame(columns = ['price', 'directory', 'car_page']) # crating empty df to append to it

for i in range(1,3000): # main pages
    i = i*30
    page = "https://www.autotrader.ca/cars/on/richmond%20hill/?rcp=30&rcs={0}&srt=3&prx=100&prv=Ontario&loc=L4E5A7&hprc=True&wcp=True&sts=New-Used&inMarket=basicSearch".format(i)
    text, html = get_text_html(page) # get html to find all the necessary links 
    hrefs = get_all_hrefs(html) # get hrefs from anchors
    for href in hrefs:
        url = 'https://www.autotrader.ca'   
        car_url = url + href  

        print('********* pNEW CAR PAGE **********',car_url)
        directory = create_and_get_new_directory()
        
        print(directory)
        text, html = get_text_html( car_url ) # get html to find all the necessary links 
        write_html_text( html, text, directory ) # for every page write html and text into pics/car direcoty 
        #unique_id = re.findall('io/[^/]*/',car_url)[0]
        unique_id = re.findall('(?<=/an|/nd|/or|ta/|ia/|ba/|ck/|ec/|io/)[^/]+', car_url)[0] # this takes into consideration if it is Quebec
        print('unique_id:',unique_id)
        if is_duplicate(df, unique_id): continue 
        price  = parse_car_page(html)
        # because there are other photos on a page
        if not int(price) > 0: continue # if there is price than it worse downloading
        print(price)
        price = str(price).replace(',','')                  

        img_hrefs = get_img_links( html, car_url )
        download_pics(img_hrefs, directory)
        car_data = { 'price': price, 'directory': directory, 'car_page': car_url} 
        df = save_to_csv( df, car_data, file_name)
        exit() 

