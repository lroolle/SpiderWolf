#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import re
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
from functools import partial


HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/47.0.2526.106 Safari/537.36'}
ROOT_URL = 'http://www.zngirls.com'
# Max retries
MAX_RETRIES = 3

# File for keeping saved albums url to avoid download again
SAVED = '.\\saved'
# Directory to save image
IMG_DIR = '.\\Images\\'

# Albums to download>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  =_=
# 'http://www.zngirls.com/girl/\d+/album/'
alb_pages = [
            ]

# Gallery to download
# 'http://www.zngirls.com/gallery/(gallery name).html'
# Gallery name, for example:
gallery_names = ['dachidu'
                ]
# For example in gallery 'dachidu', 25 pages in total, you want the first 10 pages.
gal_pgnum = 1


def request(url):
    if url is None:
        print('>>> No url to request !~')
        return
    else:
        print('| Requesting: %s ' % url)
        tries = 0
        while tries < MAX_RETRIES:
            try:
                response = requests.get(url, auth=('user', 'pass'), headers=HEADERS)
                return response
            except Exception as e:
                print('>>> Request Error:', e)
                tries += 1
                print('| Request retrying %d/%d >>> %s' % (tries, MAX_RETRIES, url))


# get start pages of each albums
def get_sdt(alb_page):
    sdt_pages = set()
    r = request(alb_page)
    if r is None or r.status_code != 200:
        print('>>> Request album page %s failed' % alb_page)
        return

    soup = bs(r.text, 'html.parser')
    # <div class_="post_entry">
    soup_alb = soup.find('div', class_="post_entry")
    # <a href="/g/17781/" class="galleryli_link">
    # <a class="igalleryli_link" href="/g/16880/">\
    soup_albs = soup_alb.find_all('a', href=re.compile(r'^/g/\d+/'))

    if not os.path.exists(SAVED):
        open(SAVED, 'w')
    with open(SAVED, 'r') as pp:
        pages_saved = pp.read()
        pages = re.compile(r'http://www.zngirls.com/g/\d+/').findall(pages_saved)
        # print(pages)

    for s in soup_albs:
        sdt_url = ROOT_URL + s.get('href')
        if sdt_url not in pages:
            sdt_pages.add(sdt_url)
        else:
            print('| Album Existed: ', sdt_url)
    return sdt_pages


# get all pages of each albums
def get_pages(sdt_page):
    pages = []
    r = request(sdt_page)
    if r is None or r.status_code != 200:
        print('>>> Request start page %s failed' % sdt_page)
        return

    soup = bs(r.text, 'html.parser')
    # <span style="color: #DB0909">

    title_num = re.sub(r'\D+', '', sdt_page)
    title_text = soup.find('title').get_text()
    title = title_text + '_' + title_num

    img_num = soup.find('span', style="color: #DB0909").get_text()
    img_num = int(re.compile(r'\d+').findall(img_num)[0])
    if img_num % 5 == 0:
        page_num = int(img_num/5)
    else:
        page_num = int(img_num/5) + 1
    for p in range(1, page_num+1):
        pages.append(sdt_page+str(p)+'.html')
    return title, pages


# get all image url of the album on every page
def get_imgurl(page):
    img_urls = list()
    r = request(page)
    if not r.status_code == 200:
        print('>>> Request page %s failed'%page)
        return
    r_text = r.text
    soup = bs(r_text, 'html.parser')
    # <div class="gallery_wrapper">
    img_div = soup.find('div', class_="gallery_wrapper")
    img_tag = img_div.find_all('img')
    for i in img_tag:
        img_urls.append(i.get('src'))
    return img_urls


def download_img(img_url):
    print('| Downloading: ', img_url)
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(img_url, auth=('user', 'pass'), headers=HEADERS, stream=True, timeout=120)
            return response
        except Exception as e:
            print('>>> Download image %s failed' % img_url, e)
            retries += 1
            print('| Download retrying %d/%d >>> %s' % (retries, MAX_RETRIES, img_url))


def save_img(img_url, tt):
    r = download_img(img_url)
    if r is None or r.status_code != 200:
        print('>>> Save image failed %s' % img_url)
        return 0
    image_num = re.sub(r'^http://\w+.zngirls.com/gallery/\d+/\d+/', '', img_url)
    if not os.path.exists(IMG_DIR):
        os.mkdir(IMG_DIR)
    if not os.path.exists(IMG_DIR+tt):
        os.mkdir(IMG_DIR + tt)
    with open(IMG_DIR+tt + '\\'+image_num, 'wb') as img:
            img.write(r.content)
    return 1


def get_gallerypages(gn, dpn):
    gal_pages = []
    for i in range(1, dpn+1):
        gal_pages.append('http://www.zngirls.com/gallery/'+gn+'/'+str(i)+'.html')
    return gal_pages


def get_post_pages(gallery_name):
    post_pages = alb_pages
    for gn in gallery_name:
        gal_pages = get_gallerypages(gn, gal_pgnum)
        for g in gal_pages:
            post_pages.append(g)
    return post_pages


def is_nested(nested_lst):
    for i in nested_lst:
        if isinstance(i, (list, set, tuple)):
            return True
    return False


def unnest(nested_lst):
    while is_nested(nested_lst):
        for i in range(len(nested_lst)-1, -1,-1):
            if not isinstance(nested_lst[i], (list, set, tuple)):
                continue
            for j in nested_lst[i]:
                nested_lst.append(j)
            nested_lst.pop(i)
    return nested_lst


if __name__ == '__main__':
    post_pages = get_post_pages(gallery_names)
    with Pool(4) as pool:  # Pool(8) causes too much requests fail
        sdt_page = pool.map(get_sdt, post_pages)

        sdt_pages = unnest(sdt_page)
        print('|>>>>>>> %d Albums to download >>>>>>>' % len(sdt_pages))
        #except Exception as e:
        #   print('>>> Get sdt page error:', e)
        count = 0
        for sdt_page in sdt_pages:
            img_urls_set = []
            title, pages = get_pages(sdt_page)
            img_urls = pool.map(get_imgurl, pages)
            img_urls_set = unnest(img_urls)
            count += 1
            print('| Album %d/%d: ' % (count, len(sdt_pages)), title)
            print('|>>>>>>> %d images to download >>>>>>>>>>' % len(img_urls_set))
            downloaded_img_num = []
            downloaded_img_num = pool.map(partial(save_img, tt=title), img_urls_set)
            with open(SAVED, 'r+') as pp:
                pp.read()
                pp.write(sdt_page+'\n')
            print('|> Saved %d Images' % sum(downloaded_img_num))
            if count == 1:
                print('oOkailubasaonian!!')

    print('|> Downloaded %d Albums' % len(sdt_pages))
