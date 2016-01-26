import requests
import re
import time
from time import strftime, gmtime
from multiprocessing import Pool
import codecs
from bs4 import BeautifulSoup as bs


proxies = {
                    "http": "http://127.0.0.1:8580",
                    "https": "http://127.0.0.1:8580",
        }
root_url = 'http://www.falstaff.at'
comp_pattern = r'winzer/[a-z-]+\d+.html'


def url_re(pattern):
    return re.compile(pattern)


def get_pages(sdt=1, end=230):
    pages = list()
    for p in range(sdt, end):
        page = ('''http://www.falstaff.at/suche/alle-winzer/seite/%d.html'''%p)
        pages.append(page)
    return pages


def connect(url):
    if url is None:
        return
    else:
        print('|***Requesting: %s ' % url)
        try:
            response = requests.get(url, auth=('user', 'pass'), proxies=proxies)
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
            compurl.append(root_url+'/'+j)
    return compurl


def get_prof(compurl):
    if compurl is None:
        return
    try:
        print('|**Company %s'%compurl)
        html_comp = connect(compurl)
        soup_c = bs(html_comp, 'html.parser')
        # '<div class="tx-faldb-pi1">'
        prof_soup = soup_c.find('div', class_="tx-faldb-pi1")
        if prof_soup is None or prof_soup == '':
            print('|WARNING:', compurl)
    except Exception as e:
        print(e)
    return str(prof_soup)


def to_tbl(profs):
    if profs is None or len(profs) == 0:
        return
    else:
        with codecs.open('falstaff_companies.html', 'w', 'utf-8') as cp:
            count = 0
            cp.write('''<html><meta charset="utf-8"> <body>
            <table style="border:1px solid" rules="all"  align="center" cellpadding='5';>
            <h1> Falstaff Exhibitors List_All </h1>
            <h2> From: <a href="http://www.falstaff.at/suche//alle-winzer/seite/1.html?"> Falstaff.at
            </a> </h2>
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


if __name__ == '__main__':
    st = time.time()
    pages = get_pages()
    with Pool(8) as pool:
        # try:
        compurls = pool.map(get_compurls, pages)
        compurl = get_compurl(compurls)
        print(len(compurl))
        profs = pool.map(get_prof, compurl)
        print(len(profs))
        to_tbl(profs)
        # except Exception as e:
        #     print('|}Error: ', e)
    et = time.time()
    timer(et-st)








