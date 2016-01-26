from bs4 import BeautifulSoup as bs
import re


class SpiderPar:

    def _url_re(self, pattern):
        return re.compile(pattern)

    def get_url(self, root_url, html_text, pattern):
        urls = list()
        soup = bs(html_text, 'html.parser')
        url_soup = soup.find_all(href=self._url_re(pattern))
        for u in url_soup:
            url = u.get('href')
            url = url.replace('amp;', '')
            fullurl = root_url + url
            urls.append(fullurl)

        return urls

    def get_prof(self, html_text, pattern):
        soup = bs(html_text, 'html_parser')
        prof_soup = soup.find('div', style='float:rightwidth:230px;')
        prof_html = str(prof_soup)
        return prof_html