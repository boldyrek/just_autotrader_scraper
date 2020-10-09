import re 
def get_kms(html):
    kilometers = re.findall('Kilometres","value":"([\d,]*)',html)
    #kilometers_clean = kilometers.remove(',') 
    if len(kilometers) == 0:
        return None
    kms_clean = kilometers[0].replace(',','')
    if kms_clean == 0: return -1 # we don't consider cars with 0 kms because we can not differentiate them
    return int(kms_clean)

def get_year(html):
    year = re.findall('year":"([\d]*)',html)
    #kilometers_clean = kilometers.remove(',') 
    if len(year) == 0:
        return None
    return year[0]

def get_make_model(html):  
    
    make_model = re.findall('title":"\d* ([\w-]*) ([\w-]*)', html)
    if len(make_model) == 0:
        return (None, None)
    return make_model[0]

def get_unique_id(car_url):
    unique_id = re.findall('(?<=/an|/nd|/or|ta/|ia/|ba/|ck/|ec/|io/)[^/]+', car_url)[0] # this 
    return unique_id



def get_car_price( html ):
    #print(html)
    #price = re.findall('.*\$[. ]*(\d*\,\d*)', html, re.MULTILINE)
    price = re.findall('ce":"(\d*)', html, re.MULTILINE)
    if len(price) == 0:
        price = 0
        return price
    #price = re.findall('987', html, re.MULTILINE)
    else: return int(str(price[1]).replace(',','')) 
    
