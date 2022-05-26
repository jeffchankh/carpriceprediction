# -*- coding: utf-8 -*-
import time
import re
import random
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import csv
import requests
import os
import datetime
import sys, getopt



def downloadfile(src, localfile, hdrs):
    r = requests.get(src, headers=hdrs)
#    print(r.status_code)
#    print(r.content[:100])

    with open(localfile, 'wb') as fh:
        fh.write(r.content)

    
def collect_details(driver, writer, f, hdrs):
    
    
    time.sleep(random.randint(1, 2))       #sleep few seconds to ensure the html is properly loaded
    
    txts=driver.find_elements_by_class_name('formt')        #forml = label, formt = text (i.e. the data)
    replytxt=driver.find_elements_by_class_name('msg')
    tmptxt = ''
    tmpreply = ''
    for i in range(len(replytxt)):
        tmptxt = replytxt[i].text.replace('\n','')
        tmpreply = tmpreply + tmptxt
    
    try:
        cid = txts[0]
        cidbuffer = cid.text
        ctype = txts[1]
        cbrand = txts[2]
        cmdl = txts[3]
        cseat = txts[4]
        cengine = txts[5]
        cgear = txts[6]
        cyear = txts[7]
        ccmt = txts[8]
        cprice = txts[9]
        cmodtime = txts[11]
        curl = txts[12]
    except IndexError:
        return
    
    #print(ccmt.text)
    if open('handled.lst', 'r').read().find(cidbuffer) == -1:
        print([cid.text,ctype.text,cbrand.text,cmdl.text,cseat.text,cengine.text,cgear.text,cyear.text,ccmt.text+tmpreply,cprice.text,cmodtime.text,curl.text]
              )
        writer.writerow([cid.text,ctype.text,cbrand.text,cmdl.text,cseat.text,cengine.text,cgear.text,cyear.text,ccmt.text+tmpreply,cprice.text,cmodtime.text,curl.text])
        f.flush()
             
    if not os.path.isfile(cidbuffer+'_low.jpg') :            
        #save the low resolution pic
        ele=driver.find_element_by_xpath('/html/body/table[6]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table[3]/tbody/tr/td/table/tbody/tr[1]/td[3]/table[1]/tbody/tr/td/table/tbody/tr/td/a/img')
        remoteurl=ele.get_attribute('src')
        localfile=cidbuffer+'_low.jpg'
        print('Trying to save ' + remoteurl + ' to ' + localfile)
        downloadfile(remoteurl, localfile, hdrs)
    
    if not os.path.isfile(cidbuffer+'_high.jpg') :
        #save the high resolution pic
        #driver.execute_script("return openPic('sell', 492420271, 5, 1, 'ca78fff8', '', '', 'w');")
        #https://dj1jklak2e.28car.com/pic_pop.php?h_cat=sell&h_vid=504430683&h_cnt=5&h_idx=1&h_pic_pth=060443d4&h_pic_dat=20220312201550&h_width=900&h_height=680&h_site=w&h_bak=
        #https://djlfajk23a.28car.com/data/image/sell/2101000/2101779/060443d4/2101779_b.jpg?20220312201550
        ele=driver.find_element_by_xpath('/html/body/table[6]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table[3]/tbody/tr/td/table/tbody/tr[1]/td[3]/table[1]/tbody/tr/td/table/tbody/tr/td/a')
        ele.click()
        
        time.sleep(random.randint(1,2))
        driver.switch_to_window(driver.window_handles[1])
        time.sleep(random.randint(1,2))
        try:
            ele=driver.find_element_by_id('h_tch_pic_org').find_element_by_xpath('./img')
            remoteurl=ele.get_attribute('src')
            localfile=cidbuffer+'_high.jpg'
            print('Trying to save ' + remoteurl + ' to ' + localfile)
            downloadfile(remoteurl, localfile, hdrs)
        except NoSuchElementException:
            print('No photo for this car')        
        driver.close();
        driver.switch_to_window(driver.window_handles[0])
      
def main(argv):

    pgno=-1    

    options, remainder = getopt.getopt(sys.argv[1:], 's:v', ['stagepage=', 
                                                         'verbose'
                                                         ])
    print('OPTIONS   :', options)

    for opt, arg in options:
        if opt in ('-s', '--startpage'):
            pgno = arg
        elif opt in ('-v', '--verbose'):
            verbose = True

    if pgno==-1:
        pgno=1
    
    # Define the parameter
    workdir='/Users/admin/DSBS/STAT5102/Project'
    #workdir='c:\\webscrapping'
    headers = {'User-Agent': 'Mozilla/5.0'}
#    startup_url='https://dj1jklak2e.28car.com/sell_lst.php?h_sort=11&h_f_ty=1&h_f_tr=1&h_f_yr=15&h_f_do=2&h_page='+str(pgno)
    startup_url='https://dj1jklak2e.28car.com/sell_lst.php?h_sort=11&h_f_ty=1&h_f_tr=2&h_f_yr=15&h_f_do=2&h_page='+str(pgno)
    records_per_page=20
    # end of Define the parameter
    
    driver = webdriver.Chrome()  
#    driver = webdriver.Chrome(executable_path='C:\\webscrapping\\chromedriver')  # Optional argument, if not specified will search path.
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : workdir}
    chrome_options.add_experimental_option('prefs', prefs)
    
    driver.get(startup_url);
    #directory = os.chdir(workdir)
    os.chdir(workdir)
    
    time.sleep(random.randint(2, 4)) # Let the user actually see something!
    
    now = datetime.datetime.now()
    ts=now.strftime("%Y%m%d%H%M%S")
    
    with open('cardata'+ts+'.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"')
    
        while True:
            for i in range(records_per_page):
                
                pageSource = driver.find_element_by_id('rw_' + str(i))
            
                print('**')
                cid = pageSource.get_attribute('title')[-8:]
                print(cid)
                print('**')
                if os.path.isfile(cid+'_low.jpg') and os.path.isfile(cid+'_high.jpg') and open('handled.lst', 'r').read().find(cid) != -1:
                    print("skipping the logic as the files exist")
                    time.sleep(random.randint(1,2))
                    continue
            
                iHTML=pageSource.get_attribute('innerHTML')
                cmds = re.findall('(goDsp.*\'n\'.*)\"',iHTML)
                for cmd in cmds:
                    driver.execute_script("return "+cmd+";")
                    collect_details(driver, writer, f, headers)
                    time.sleep(random.randint(2, 3))        #randomly pick a sleeping time between 2 and 3 sec
                    driver.back()
                    time.sleep(random.randint(1, 3))
    
            try:
                btn = driver.find_element_by_id('btn_nxt')
                btn.click()
            except NoSuchElementException:
                break
            
        f.close()
    
    time.sleep(random.randint(2, 4))
    driver.quit()
    
if __name__ == "__main__":
   main(sys.argv[1:])
    
    
    
    
    
