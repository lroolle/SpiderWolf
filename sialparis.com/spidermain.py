import get_url
import time
import codecs
from multiprocessing import Pool


class SpiderMain:
    def __init__(self):
        self.rooturl = 'https://www.sialparis.com'
        self.pageurl = 'https://www.sialparis.com/Exhibitors-list-SIAL-2014/Exhibitors-list/(page)/'
        self.urlpattern = r'^/Exhibitors-list-SIAL-2014/Exhibitors-list/\w+'
        self.stp = 1
        self.edp = 256


def main():
    S = SpiderMain()
    G = get_url.GetUrl()
    pages = G.get_pages(S.pageurl, S.stp, S.edp)
    
    with Pool(8) as pool:

        compurls = pool.map(G.get_comp, pages)

        compurl = []
        for i in compurls:
            for j in i:
                compurl.append(j)
        compfiles = pool.map(G.get_content, compurl)
        count = 0
        with codecs.open('companies.html', 'w', 'utf-8') as cp:
            cp.write('''<html><body>
            <table style="border:1px solid" rules="all"  align="center" cellpadding='5';>
            <tr>''')
            for cf in compfiles:
                if count % 4 == 0 and count != 0:
                    cp.write('</tr><tr>')
                cp.write('''<td width="25%">'''+cf+'</td>')
                count += 1
                print(count, '...')
            cp.write('</tr></table></body></html>')

if __name__ == '__main__':
    st = time.time()
    main()
    et = time.time()
    print(et-st)
