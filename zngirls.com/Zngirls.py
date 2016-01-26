#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    First You Would Like to Visit zngirls.com
    And Choose Your Favorite Girls' Albums
    Then Add the Album Url to 'alb_page'
'''


import requests
import os
import re
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
from functools import partial


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/47.0.2526.106 Safari/537.36'}
root_url = 'http://www.zngirls.com'
page_pattern = r'^http://www.zngirls.com/g/\d+/\d+'
alb_pattern = r'^/g/\d+'
# Save Downloaded albums url to avoid download again
saved = '.\\saved'

# Albums to download>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  =_=
alb_pages = ['http://www.zngirls.com/girl/19705/album/',
             ]


def request(url):
    if url is None:
        print('>>> No url to request !~')
        return
    else:
        print('| Requesting: %s ' % url)
        try:
            response = requests.get(url, auth=('user', 'pass'), headers=headers)
            return response
        except Exception as e:
            print('>>> Request Error:', e)


def url_re(pattern):
    return re.compile(pattern)


# get start pages of each albums
def get_sdt(alb_page):
    sdt_pages = set()
    r = request(alb_page)
    if r.status_code == 200:
        r_text = r.text
        soup = bs(r_text, 'html.parser')
        # <div id="photo_list">
        soup_albs = soup.find('div', id="photo_list")
        # <a href="/g/17781/" class="galleryli_link">
        # <a class="igalleryli_link" href="/g/16880/">\
        soup_alb = soup_albs.find_all('a', href=url_re(alb_pattern))

        if not os.path.exists(saved):
            open(saved, 'w')
        with open(saved, 'r') as pp:
            pagesr = pp.read()
            pages = re.compile(r'http://www.zngirls.com/g/\d+/').findall(pagesr)
            # print(pages)
        for s in soup_alb:
            sdt_url = root_url + s.get('href')
            if sdt_url not in pages:
                sdt_pages.add(sdt_url)
            else:
                print('| Exists:', sdt_url)
        return sdt_pages
    else:
        print('>>> Request album page %s failed'%alb_page)

# get all pages of each albums
def get_pages(sdt_page):
    pages = list()
    r = request(sdt_page)
    if r.status_code == 200:
        r_text = r.text
        soup = bs(r_text, 'html.parser')
        # <span style="color: #DB0909">
        img_num = soup.find('span', style="color: #DB0909").get_text()
        title = soup.find('title').get_text()
        img_num = int(re.compile(r'\d+').findall(img_num)[0])
        if img_num % 5 == 0:
            page_num = int(img_num/5)
        else:
            page_num = int(img_num/5) + 1
        for p in range(1, page_num+1):
            pages.append(sdt_page+str(p)+'.html')
        return title, pages
    else:
        print('>>> Request start page %s failed'%sdt_page)


# get all image url of the album on every page
def get_img(page):
    img_urls = list()
    r = request(page)
    if r.status_code == 200:
        r_text = r.text
        soup = bs(r_text, 'html.parser')
        # <div class="gallery_wrapper">
        img_div = soup.find('div', class_="gallery_wrapper")
        img_tag = img_div.find_all('img')
        for i in img_tag:
            img_urls.append(i.get('src'))
        return img_urls
    else:
        print('>>> Request page %s failed'%page)


def __down_img(img_url, title):
    print('| Downloading: ', img_url)
    reponse = requests.get(img_url, auth=('user', 'pass'), headers=headers, stream=True, timeout=120)
    image = reponse.content
    image_name = re.sub(r'^http://\w+.zngirls.com/gallery/\d+/\d+/', '', img_url)
    des_dir = '.\\Images\\'
    if not os.path.exists(des_dir):
        os.mkdir(des_dir)
    if not os.path.exists(des_dir+title):
        os.mkdir(des_dir+title)
    with open(des_dir+title+'\\'+image_name, 'wb') as img:
            img.write(image)


def download_img(img_url, title):
    try:
        __down_img(img_url, title)
    except Exception as e:
        print('>>> Save Error:', e)


if __name__ == '__main__':
    
    with Pool(4) as pool:  # Pool(8) causes too much requests fail
        sdt_pages = set()
        try:
            sdt_page = pool.map(get_sdt, alb_pages)
            for i in sdt_page:
                for j in i:
                    sdt_pages.add(j)
            print('| %d Albums to download' % len(sdt_pages))
        except Exception as e:
            print('>>> Get sdt page error:', e)
        count = 0
        for sdt_page in sdt_pages:
            try:
                img_urlss = set()
                title, pages = get_pages(sdt_page)
                count += 1
                print('| Album %d/%d: ' % (count, len(sdt_pages)), title)
                img_urls = pool.map(get_img, pages)
                for i in img_urls:
                    for j in i:
                        img_urlss.add(j)
                print('>>> %d images to download >>>>>>>'%len(img_urlss))
                down_img = pool.map(partial(download_img, title=title), img_urlss)
                with open(saved, 'r+') as pp:
                    pp.read()
                    pp.write(sdt_page+'\n')
                print('|> Saved %d Images' % len(img_urlss))
                if count == 1:
                    print('oOkailubasaonian!!')
            except Exception as e:
                print('>>>Error ', e)

    print('|> Downloaded %d Albums'%len(sdt_pages))








