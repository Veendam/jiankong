# -*- coding:utf-8 -*-
#!/usr/bin/python

import base64
import json
import os
import requests
import time
import sys

from datetime import date, timedelta, datetime
from io import BytesIO
from PIL import Image, ImageDraw
from qiniu import Auth, BucketManager, CdnManager, put_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dingtalkchatbot.chatbot as cb 
from msg import get_msg1, get_msg2, get_msg3


# print 中文 避免出现编码问题
# reload(sys)
# sys.setdefaultencoding('utf8')


class MyError(Exception):
    def __init__(self, message, driver):
        self.message = message
        driver.close()
        driver.quit()
    def __str__(self):
        return 'ChromeDriver closed.\n' + self.message


crop_box = [(25, 223, 1350, 528), (25, 260, 1350, 565)]


def upload_file(ak, sk, png_files, upload=True):
    BASEURL = "http://p7d7ismcm.bkt.clouddn.com"
    QINIU = Auth(ak, sk)
    BUCKET = 'report'
    fig_urls = []
    for p in png_files:
        if upload:
            key = os.path.basename(p)
            token = QINIU.upload_token(BUCKET, key)
            ret, info = put_file(token, key, p)
            fig_url = os.path.join(BASEURL, key)
        else:
            fig_url = "https://cn.bing.com/az/hprichbg/rb/WoodPartridge_ZH-CN11771370571_1920x1080.jpg&quot"
        fig_urls.append(fig_url)
        print(fig_url)
    return fig_urls


# 删除上传的文件
def del_fig(ak, sk, png_files, fig_urls, delete=True):
    BASEURL = "http://p7d7ismcm.bkt.clouddn.com"
    QINIU = Auth(ak, sk)
    BUCKET = 'report'
    bucket = BucketManager(QINIU)
    if delete:
        for k in png_files:
            key = os.path.basename(k)
            ret, info = bucket.delete(BUCKET, key)
            if ret == {}:
                rep = 'Figure has been deleted.'

            else:
                rep = 'Error when deleting figure.'
                print(k, rep)
        # refresh cdn cache
        cdn_manager = CdnManager(QINIU)
        refresh_url_result = cdn_manager.refresh_urls(fig_urls)
        if refresh_url_result[0]['error'] == u'success':
            print('CDN has been refreshed')
    return


# split figure when it is too big
def fig_split(im_set, prefix):
    # 一张图里6个截图
    figs_per_png = 6 
    step = range(0, len(im_set), figs_per_png)
    png_files = []
    
    for i,j in enumerate(step):
        tmp_im_set = im_set[j:(j+figs_per_png)]
        total_height = sum(im.size[1] for im in tmp_im_set) 
        total_height = total_height + 5 * len(tmp_im_set) -5
        total_width = tmp_im_set[0].size[0]
        new_im  = Image.new('RGB', (total_width, total_height), (228, 150, 150))
        
        h_offset = 0
        for im in tmp_im_set:
            new_im.paste(im, (0, h_offset))
            h_offset += im.size[1] + 5

        png_filename = prefix.replace('.png', '_%s.png' % i)
        png_files.append(png_filename)
        new_im.save(png_filename)
    return png_files


# 发送数据到群中
def send_report(msg, url):
    headers = {"Content-Type": "application/json"}
    data = {'msgtype':'markdown',
        'markdown':{'title':u'每日报表',
            'text':msg}}
    xiaoding = cb.DingtalkChatbot(url)
    # r = requests.post(url, data=json.dumps(data), headers=headers)
    # requests.post(url,)
    msg = msg.replace('\\','/')
    print(msg)
    xiaoding.send_markdown(title= '每日报表',
                       text=msg)
    return 'heheda'



# 用户账户登录
def login(username, pwd, url="https://signin.aliyun.com/login.htm", headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    #options.add_argument('--verbose')
    #service_log_path = "/tmp/chromedriver.log"
    options.add_argument('--window-size=1380x1080')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    time.sleep(1)
    input_name = driver.find_element_by_id('user_principal_name')

    input_name.send_keys(username)
    driver.find_element_by_id('J_FormNext').click()
    time.sleep(1)
    input_pwd = driver.find_element_by_id('password_ims')

    input_pwd.send_keys(pwd)
    time.sleep(1)
    driver.find_element_by_css_selector('input.fm-button.submit-btn').click()
    return driver


def daily_report(ak, sk, username, pwd, pull_url, push_url, msg_fun, grids,  wait=60, upload=True, delete=True, headless=True):
    """
    对分享链接进行截图
    crop size h305 w1325
    """
    tables_per_fig = 6

    driver = login(username, pwd, headless=headless)
    driver.get(pull_url)

    print(datetime.today().strftime('%Y-%m-%d-%H-%M-%S'))
    waiter = WebDriverWait(driver, wait)

    # data table tabs
    element = waiter.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='table-title']/parent::div/div[contains(@class, 'switchtainer')]")))
    # find tab             
    li = driver.find_elements_by_css_selector('li.qbi-tab-item')

    # all data tables
    msg_grids = driver.find_elements_by_xpath("//div[@class='table-title']/parent::div")
      
    # 统计每个tab有多少个表格
    grids_view = []
    for i,j in enumerate(li):
        j.click()        
        #print i, len([x for x in msg_grids if x.location['y']>0])
        grids_view.append(len([x for x in msg_grids if x.location['y']>0]))
    print("Tables in each tab_grid: ",grids_view)
        
    text = (date.today() - timedelta(1)).strftime('%Y')   
    im_set = []
    for tab, table in grids:
        li[tab-1].click()
        idx = sum(grids_view[:(tab-1)]) + table
        
        time_count = 0
        #print tab, table, text, idx
        while time_count < wait:
            if text not in msg_grids[idx-1].text:
                #print time_count, msg_grids[idx-1].text[:20]
                time.sleep(5)
            else:                
                break
            time_count += 5
            
        else: 
            if text not in msg_grids[idx-1].text:
                #print msg_grids[idx-1].text
                driver.get_screenshot_as_file('error.png')
                raise MyError(u'Tab%s,Table%s 规定时间内网页加载不完全' % (tab, table), driver)
            
        #print driver.find_element_by_xpath(xpath).text[:20]
        msg_grids[idx-1].location_once_scrolled_into_view
        
        #filename = 'file%s_%s.png' % (tab, table)
        #driver.get_screenshot_as_file(filename)
        screenshot = driver.get_screenshot_as_base64()
        screenshot = Image.open(BytesIO(base64.b64decode(screenshot)))
        
        target_grid = msg_grids[idx-1]
        y_loc = target_grid.location['y']
        screenshot_buttom = screenshot.size[1]
        if screenshot_buttom < y_loc-2 + 305:
            y_loc_buttom = screenshot_buttom
        else:
            y_loc_buttom = y_loc-2 + 305          
            
        im = screenshot.crop((25, y_loc-2, 1350, y_loc_buttom))   
        im_set.append(im)     
        #im.save(filename)

    im_file = "%s_%s.png" % (msg_fun.__name__, datetime.today().strftime('%Y-%m-%d-%H-%M-%S'))

    png_files = fig_split(im_set, im_file)

    # upload report.png, and get link.
    fig_urls = upload_file(ak, sk, png_files, upload=upload)
    # get push message
    msg = msg_fun(msg_grids, li, fig_urls, grids_view)
    # print(msg)
    # send data to dingding
    r = send_report(msg, push_url)
    # wait a moment and delete the png files hosted online.
    time.sleep(5)
    del_fig(ak, sk, png_files, fig_urls, delete=delete)
    return



def daily_report_BLD(ak, sk, username, pwd, pull_url, push_url, msg_fun, grids,  wait=60, upload=True, delete=True, headless=True):
    """
    对分享链接进行截图
    crop size h305 w1325
    """
    tables_per_fig = 6

    driver = login(username, pwd, headless=headless)
    driver.get(pull_url)

    print(datetime.today().strftime('%Y-%m-%d-%H-%M-%S'))
    waiter = WebDriverWait(driver, wait)

    # data table tabs
    element = waiter.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='table-title']/parent::div/div[contains(@class, 'switchtainer')]")))
    # find tab             
    li = driver.find_elements_by_css_selector('li.qbi-tab-item')

    # all data tables
    msg_grids = driver.find_elements_by_xpath("//div[@class='table-title']/parent::div")
      
    # 统计每个tab有多少个表格
    grids_view = []
    for i,j in enumerate(li):
        j.click()        
        #print i, len([x for x in msg_grids if x.location['y']>0])
        grids_view.append(len([x for x in msg_grids if x.location['y']>0]))
    print("Tables in each tab_grid: ",grids_view)
        
    text = (date.today() - timedelta(1)).strftime('%Y')   
    im_set = []
    for tab, table in grids:
        li[tab-1].click()
        idx = sum(grids_view[:(tab-1)]) + table
        
        time_count = 0
        #print tab, table, text, idx
        while time_count < wait:
            if text not in msg_grids[idx-1].text:
                #print time_count, msg_grids[idx-1].text[:20]
                time.sleep(5)
            else:                
                break
            time_count += 5
            
        else: 
            if text not in msg_grids[idx-1].text:
                #print msg_grids[idx-1].text
                driver.get_screenshot_as_file('error.png')
                raise MyError(u'Tab%s,Table%s 规定时间内网页加载不完全' % (tab, table), driver)
            
        #print driver.find_element_by_xpath(xpath).text[:20]
        msg_grids[idx-1].location_once_scrolled_into_view
        
        #filename = 'file%s_%s.png' % (tab, table)
        #driver.get_screenshot_as_file(filename)
        screenshot = driver.get_screenshot_as_base64()
        screenshot = Image.open(BytesIO(base64.b64decode(screenshot)))
        
        target_grid = msg_grids[idx-1]
        y_loc = target_grid.location['y']
        screenshot_buttom = screenshot.size[1]
        if screenshot_buttom < y_loc-2 + 305:
            y_loc_buttom = screenshot_buttom
        else:
            y_loc_buttom = y_loc-2 + 305          
            
        im = screenshot.crop((25, y_loc-2, 1350, y_loc_buttom))   
        im_set.append(im)     
        #im.save(filename)

    im_file = "%s_%s.png" % (msg_fun.__name__, datetime.today().strftime('%Y-%m-%d-%H-%M-%S'))

    png_files = fig_split(im_set, im_file)

    # upload report.png, and get link.
    fig_urls = upload_file(ak, sk, png_files, upload=upload)
    # get push message
    msg = msg_fun(msg_grids, li, fig_urls, grids_view)
    # print(msg)
    # send data to dingding
    r = send_report(msg, push_url)
    # wait a moment and delete the png files hosted online.
    time.sleep(5)
    del_fig(ak, sk, png_files, fig_urls, delete=delete)
    return


if __name__ == "__main__":
    with open('config.json') as handle:
        qiniu_conf = json.load(handle)['qiniu']
    ak = qiniu_conf['AK']
    sk = qiniu_conf['SK']

    
