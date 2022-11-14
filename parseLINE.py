# -*- coding: utf-8 -*-
import MySQLdb
import time
import sys
import re
from datetime import date, timedelta,datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import os

weburl = sys.argv[1]
anvato_id = sys.argv[2]

conn = MySQLdb.connect(host="localhost",user="", passwd="", db="", charset="utf8")

regex1 = re.compile(r'\d+/\d+/\d+')

option = webdriver.ChromeOptions()
lambda_options = [
        '--autoplay-policy=user-gesture-required',
        '--disable-background-networking',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-breakpad',
        '--disable-client-side-phishing-detection',
        '--disable-component-update',
        '--disable-default-apps',
        '--disable-dev-shm-usage',
        '--disable-domain-reliability',
        '--disable-extensions',
        '--disable-features=AudioServiceOutOfProcess',
        '--disable-hang-monitor',
        '--disable-ipc-flooding-protection',
        '--disable-notifications',
        '--disable-offer-store-unmasked-wallet-cards',
        '--disable-popup-blocking',
        '--disable-print-preview',
        '--disable-prompt-on-repost',
        '--disable-renderer-backgrounding',
        '--disable-setuid-sandbox',
        '--disable-speech-api',
        '--disable-sync',
        '--disk-cache-size=33554432',
        '--hide-scrollbars',
        '--ignore-gpu-blacklist',
        '--ignore-certificate-errors',
        '--metrics-recording-only',
        '--mute-audio',
        '--no-default-browser-check',
        '--no-first-run',
        '--no-pings',
        '--no-sandbox',
        '--no-zygote',
        '--password-store=basic',
        '--use-gl=swiftshader',
        '--use-mock-keychain',
        '--single-process',
        '--headless']

for argument in lambda_options:
    option.add_argument(argument)

driver = webdriver.Chrome(options=option)
driver.set_page_load_timeout(10)
try:
	print(weburl)
	driver.get(weburl)
	time.sleep(2)
	pageSource = driver.page_source
	driver.close()
	os.system("pkill chrome")
	soup = BeautifulSoup(pageSource, 'lxml')
	meta = soup.find(attrs={"name":"news_keywords"})['content']
	keywords = meta.split(',')
	category = keywords[len(keywords)-1].strip()
	title = soup.findAll("h1",{"class":"header"})
	print(title)
	title = soup.findAll("h1",{"class":"header"})[0].string.strip()
	print(title)
	pdate_str = soup.findAll("span",{"class":"entityPublishInfo-meta-info"})[0].string
	pdate_ary = pdate_str.split('發布於')
	if '分鐘前' in pdate_str:
		publish_date = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
	elif '小時前' in pdate_str:
		hour = int(pdate_ary[1].replace('小時前', '').strip())
		publish_date = (datetime.now()-timedelta(hours=hour)).strftime("%Y-%m-%d %H:%M:%S")
	elif '天前' in pdate_str:
		day = int(pdate_ary[1].replace('天前', '').strip())
		publish_date = (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d %H:%M:%S")
	else:
		year = datetime.now().year
		publish_date = str(year) + '-' + pdate_ary[1].replace('月', '-').replace('日', ' ').strip()
	isID = regex1.search(pdate_str)
	if isID:
		chars = pdate_str.split(' ')
		thedate = chars[2].split('/')
		thetime = chars[1].replace(',','').replace('.',':')
		publish_date = thedate[2] + '-' + thedate[1] + '-' + thedate[0] + ' ' + thetime
	print(publish_date)
	views = soup.findAll("span",{"class":"text--fNarrow"})[0].string.replace('觀看次數','').replace(',','').strip()
	likes = soup.findAll("span",{"class":"interactiveLike-count"})[0].string.strip()
	comments = soup.findAll("span",{"class":"interactiveComment-count"})[0].string.replace('留言','').strip()
	sql = "UPDATE stories SET story_name_line = %s, line_category = %s , publish_datetime = %s , line_views = %s , line_likes = %s , line_comments = %s  WHERE anvato_id = %s"
	cursor = conn.cursor()
	cursor.execute(sql, (
		title, category, publish_date, views, likes, comments, anvato_id))
	conn.commit()
	cursor.close()
except Exception as e:
	print('except' + weburl)
	print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
	print(e)


conn.close()
