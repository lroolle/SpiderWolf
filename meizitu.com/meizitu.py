import requests
import os
import re
import time
from time import strftime, gmtime
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
from functools import partial


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/47.0.2526.106 Safari/537.36'}
root_url = 'http://www.meizitu.com'
# set start and end pages
sdt = 1
end = 3


def request(url):
    if url is None:
        return
    else:
        print('| Requesting: %s ' % url)
        try:
            response = requests.get(url, auth=('user', 'pass'), headers=headers)
            # response.encoding('utf-8')
            response.encoding = 'gb2312'
            return response.text
        except Exception as e:
            print('| Request Error:', e)


def get_albs(sdt, end):
    albs = list()
    # http://www.meizitu.com/a/5028.html
    with open('albums', 'r') as ap:
        r = ap.read()
        albums = re.compile(r'http://www.meizitu.com/\w+/\d+.html').findall(r)
        # print(albums)
    for i in range(sdt, end+1):
        url = root_url+'/a/'+str(i)+'.html'
        # print(url in albums)
        if url not in albums:
            albs.append(url)
        else:
            print('|Exists:', url)
    return albs


def get_img(page):
    img_urls = list()
    r_text = request(page)
    soup = bs(r_text, 'html.parser')
    # <div class="postmeta  clearfix">
    title_div = soup.find('div', class_="postmeta  clearfix")
    title_nm = title_div.find('h2').get_text()
    while ' ' or '|' or '*'in title_nm:
        title_nm = re.sub(' ', '', title_nm)
        title_nm = re.sub(r'\|', '', title_nm)
        title_nm = re.sub(r'\*', '', title_nm)
    # http://www.meizitu.com/a/5028.html
    title_num = re.sub(r'http://www.meizitu.com/a/', '', page)
    title_num = re.sub(r'.html', '', title_num)
    title = title_num+'_'+title_nm
    print('| Title:', title)
    # <div class="postContent">
    img_div = soup.find('div', class_="postContent")
    img_tag = img_div.find_all('img')
    # info = img_div.get_text()
    for i in img_tag:
        img_urls.append(i.get('src'))
    return img_urls, title


def __down_img(img_url, title):
    if not re.match(r'^http://\w+.meizitu.com/wp-content/uploads/\w+/\d+/\d+/', img_url):
        return
    # "http://pic.meizitu.com/wp-content/uploads/2016a/01/09/01.jpg"
    print('| Downloading: ', img_url)
    reponse = requests.get(img_url, auth=('user', 'pass'), headers=headers, stream=True, timeout=60)
    image = reponse.content
    image_name = re.sub(r'^http://\w+.meizitu.com/wp-content/uploads/\w+/\d+/\d+/', '', img_url)
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
        print('| Save Error:', e)
        print('| Retrying :', img_url)
        __down_img(img_url, title)
        print('| Tried best.......')


def time_format(sec):
    tm = gmtime(sec)
    if sec >= 3600:
        h = int(strftime('%H', tm))
        m = int(strftime('%M', tm))
        if m == 0:
            return '%d hour' % h
        else:
            return '%d hour %d minutes'%(h,m)
    elif sec >= 60:
        s = int(strftime('%S', tm))
        m = int(strftime('%M', tm))
        if s == 0:
            return '%d minutes' % m
        else:
            return '%d minutes %d seconds' % (m, s)
    else:
        s = int(strftime('%S', tm))
        return '%d seconds' % s


def timer(sec):
    tm = time_format(sec)
    print('| Spend %s' % tm)


def timer_rem(tm, count, leth):
        if len(tm) <= 10:

            re_tm = tm[len(tm)-1] - tm[0]
            re_tm = (re_tm / count)*(leth - count)
        else:
            re_tm = tm[len(tm)-1] - tm[len(tm)-10]
            re_tm = (re_tm / 10)*(leth - count)

        tm = time_format(re_tm)
        print('| TIME: remaining about %s\n'%tm)


if __name__ == '__main__':
    st = time.time()
    if not os.path.exists('.\\albums'):
        open('albums','w')
    with Pool(8) as pool:
        albs = get_albs(sdt, end)
        count = 0
        tm = [time.time()]
        for i in albs:
            try:
                count += 1
                print('Album %d/%d %s' % (count, len(albs), i))
                img_urls, title = get_img(i)
                down_img = pool.map(partial(download_img, title=title), img_urls)
                with open('albums', 'r+') as pp:
                    pp.read()
                    pp.write(i + '\n')
            except Exception as e:
                try:  # maybe better ways to retry...
                    print('|Error', e)
                    print('|Retrying:', i)
                    count += 1
                    print('Album %d/%d %s' % (count, len(albs), i))
                    img_urls, title = get_img(i)
                    down_img = pool.map(partial(download_img, title=title), img_urls)
                    with open('albums', 'r+') as pp:
                        pp.read()
                        pp.write(i+'\n')
                except Exception as e:
                    print('Tried best...', e)

            tm.append(time.time())
            timer_rem(tm, count, len(albs))


    et = time.time()
    timer(et-st)








