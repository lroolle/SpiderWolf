import Writer
import UrlManager
import Downloader
import SpiderPar
import codecs


class AnugaSpi:

    def __init__(self):
        self.url = UrlManager.UrlManager()
        self.downloader = Downloader.Downloader()
        self.htmlpar = SpiderPar.SpiderPar()

    def get_urls(self, sdt_page, root_url, page_pattern):
        count = 1
        page_urls = list()
        comp_urls = list()
        page_urls.append(sdt_page)
        self.url.add_newurl(sdt_page)
        while self.url.have_newurl():
            try:
                new_url = self.url.get_new()
                print('|* Count %d'%count)
                html_text = self.downloader.down_html(new_url)
                page_urls = self.htmlpar.get_url(root_url, html_text, page_pattern)
                comp_urls = self.htmlpar.get_url(root_url, html_text, comp_pattern)
                self.url.add_newurls(page_urls)
                page_urls.append(page_urls)
                comp_urls.append(comp_urls)
                count += 1
            except Exception as e:
                print('|****Eroo',e)
                count += 1
            if count > 30:
                break
        return page_urls, comp_urls

    def get_profs(self, page_urls):

        pass



if __name__ == "__main__":

    root_url = "http://www.anuga.com"
    sdt_page = "http://www.anuga.com/anuga/exhibitor-search/search" \
                    "/index.php?fw_goto=aussteller/blaettern&&start=0&paginatevalues=[]"
    # page_pattern = r"/anuga/exhibitor-search/search" \
    #                     r"/index.php?fw_goto=aussteller/blaettern&amp;&amp;start=\d+&amp;paginatevalues=%5B%5D"
    page_pattern = r'/anuga/exhibitor-search/search/index.php\?fw_goto=aussteller/blaettern&&start='

    # comp_pattern = r"/anuga/exhibitor-search/search/index.php\?fw_goto=aussteller/details&amp;&amp;kid=\d+&amp;"\
    #                     r"values=%7B%22stichwort%22%3A%22Enter+search+phrase%2C+i.e.+exhibitor+name%2C+brand%2C+product+group+or+country%22%2C%22start%22%3A0%7D"
    comp_pattern = r'/anuga/exhibitor-search/search/index.php\?fw_goto=aussteller/details&&kid='
    prf_pattren = r'''<div style="float:right;width:230px;">'''
    anuga = AnugaSpi()
    page_urls, comp_urls= anuga.get_urls(sdt_page, root_url, page_pattern)
    print(page_urls)
    print(comp_urls)
    with codecs.open('page_url.txt', 'w', 'utf-8') as up:
        for p in page_urls:
            up.write(str(p)+'\n')
    with codecs.open('comp_url.txt', 'w', 'utf-8') as cp:
        for c in comp_urls:
            cp.write(str(c)+'\n')