"""
First i want to list all directorires
iterate through each directory
read html file
parse link 
parse price
save to df a link, price and directory
"""

import os 
import re
import pandas as pd

def parse_price(html):

    m = re.search('price":"(\d*)', html, re.MULTILINE)
    price = m.group(1)
    if len(price) == 0:
        price = 0

    return price


def parse_url(html):

    #url = re.findall('https://.*/\d_[\d_]*/',html, re.MULTILINE)
    url = re.findall('https://www\.autotrader.*/\d*_[\d_a-z]*/',html, re.MULTILINE)
    print(url)
    return url[0] 



def is_incedent(html):
    """
    check if they banned me or page timed out
    """
    if 'timed out' in html: return True
    if 'invalid response while acting' in html: return True
    if 'Incapsula incident ID:' in html: return True 

    return False



######################## MAIN ################
#First i want to list all directorires
dirs = os.listdir('../pics2/')
cars_info =[]
for dir in dirs:
    print('*** new car')
    f = open('../pics2/' + dir +'/html.txt','r')
    html = f.read()
    #print(html)
    if is_incedent(html): continue # some of the downloads have been blocked we need not to store this 
    print(dir)    
    url = parse_url(html)
    print(url)
    price = parse_price(html)
    print(price)
    cars_info.append((url,price,dir)) 

df = pd.DataFrame(cars_info, columns=[ 'url' , 'price' , 'dir' ] )
df.to_csv('cars_info.csv')
