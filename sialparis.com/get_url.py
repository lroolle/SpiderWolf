import requests, re, codecs
from bs4 import BeautifulSoup as bs

class GetUrl:
    def re_url(self, urlpattern):
        return re.compile(urlpattern)

    def get_pages(self, pageurl, startp=1, endp=256):
        pages = []
        for p in range(startp, endp+1):
            pages.append(pageurl+str(p))
        return pages

    def get_comp(self, page):
        compurls = list()
        print('| Requesting: %s' % page)
        try:
            pr = requests.get(page, auth=('user', 'pass'))
            soup = bs(pr.text, 'html.parser')
            comphtm = soup.find_all(href=self.re_url(r'^/Exhibitors-list-SIAL-2014/Exhibitors-list/\w+'))
            for a in comphtm:
                compurls.append('https://www.sialparis.com'+a.get('href'))
            return compurls
        except Exception as e:
            print('| ERROR: ', e)
            with codecs.open('.\files\page_url', 'r+', 'utf-8') as pp:
                pp.read()
                pp.write(page+'\n')

    def get_content(self, url):

        print('| Get: %s' % url)
        try:
            r = requests.get(url, auth=('user', 'pass'))
            sp = bs(r.text, 'html.parser')
            content_htm = sp.find('div', class_='exhibitor-content')
            return str(content_htm)
        except Exception as e:
            print('| ERROR: ', e)
            with codecs.open('.\files\comp_url', 'r+', 'utf-8') as cp:
                cp.read()
                cp.write(url+'\n')
        # print(r)

        # For the sake of encryption email address

        # comp_name = content_htm.find('h2').get_text()
        # comp_tel = content_htm.find('div', class_='tel').get_text().strip().replace('\n',' ')
        # comp_web = content_htm.find_all('a', class_='a_tooltip', target='_blank')[1].get('href')
        # comp_mail = re.compile(r"[\w\.\-]+@[\w\.\-]+")
