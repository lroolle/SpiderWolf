import requests
import re
import time
from time import strftime, gmtime
from multiprocessing import Pool
import codecs
from bs4 import BeautifulSoup as bs


# VPN
proxies = {
                    "http": "http://127.0.0.1:8580",
                    "https": "http://127.0.0.1:8580",
        }
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/47.0.2526.106 Safari/537.36'}
root_url = 'http://www.anuga.com'
comp_pattern = r'/anuga/exhibitor-search/search/index.php\?fw_goto=aussteller/details&&kid='
prf_pattren = '''<div style="float:right;width:230px;">'''


def url_re(pattern):
    return re.compile(pattern)


def get_pages(sdt=1, end=367):
    pages = list()
    for p in range(sdt, end):
        page = ('''http://www.anuga.com/anuga/exhibitor-search/search/index.php?'''
        '''fw_goto=aussteller/blaettern&&start={num}'''.format(num=(p-1)*20)+'''&paginatevalues=%5B%5D''')
        pages.append(page)
    return pages


def connect(url):
    if url is None:
        return
    else:
        print('|***Requesting: %s ' % url)
        try:
            response = requests.get(url, auth=('user', 'pass'), headers=headers, proxies=proxies)
            if response.text is None or response.text == '':
                print('|Reponse Error', url)
                return
            return response.text
        except Exception as e:
            print('|***Errrrr:', e)


def get_compurls(page):
    if page is None:
        return
    try:
        compurls = set()
        print('|*Page: %s' % page)
        html = connect(page)
        html = html.replace('amp;', '')
        soup = bs(html, 'html.parser')
        soup_re = soup.find_all(href=url_re(comp_pattern))
        for s in soup_re:
            compurls.add(s.get('href'))
    except Exception as e:
        print(e)
    return compurls


def get_compurl(compurls):
    if len(compurls) == 0:
        return
    compurl = []
    for i in compurls:
        for j in i:
            compurl.append(root_url+j)
    return compurl


def get_prof(compurl):
    if compurl is None:
        return
    try:
        print('|**Company %s'%compurl)
        html_comp = connect(compurl)
        soup_c = bs(html_comp, 'html.parser')
        # <div style="float:right;width:230px;">
        prof_soup1 = soup_c.find('div', style="float:right;width:230px;")
        if prof_soup1 is None or prof_soup1 == '':
            print('|WARNING:', compurl)
        # <div style="border:solid 1px #E7E7E7;">
        prof_soup2 = soup_c.find('div', style="border:solid 1px #E7E7E7;")
        if prof_soup2 is None or prof_soup2 == '':
            print('|WARNING:', compurl)
        prof_soup = str(prof_soup1)+str(prof_soup2)
        if prof_soup is None:
            print('|...................', compurl)
            return
    except Exception as e:
        print(e)
    return prof_soup


def to_tbl(profs):
    if profs is None or len(profs) == 0:
        return
    else:
        with codecs.open('anuga_companies.html', 'w', 'utf-8') as cp:
            count = 0
            cp.write('''<html><meta charset="utf-8"> <body>
            <table style="border:1px solid" rules="all"  align="center" cellpadding='5';>
            <h1> Anuga Exhibitors List_All </h1>
            <h2> From: <a href="http://www.anuga.com/anuga/exhibitor-search/search/index.php"> Anuga Exhibitor Search </a> </h2>
            <tr>''')
            for c in profs:
                if c is None or c == '':
                    continue
                if count % 4 == 0 and count != 0 or len(c) < 5:
                    cp.write('</tr><tr>')
                cp.write('''<td width="25%" align="left">'''+c+'</td>')
                count += 1
                print('|**Writting: ', count, '...')
            cp.write('</tr></table></body></html>')


if __name__ == '__main__':
    pages = get_pages(1, 367)
    with Pool(8) as pool:
        compurls = pool.map(get_compurls, pages)
        compurl = get_compurl(compurls)
        profs = pool.map(get_prof, compurl)
        to_tbl(profs)









