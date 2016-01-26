import codecs

class Writer:

    def to_tbl(self, profs):
        if profs is None or len(profs) == 0:
            return
        else:
            with codecs.open('anuga_companies.html', 'w', 'utf-8') as cp:
                count = 0
                cp.write('''<html><body>
                <table style="border:1px solid" rules="all"  align="center" cellpadding='5';>
                <tr>''')
                for c in profs:
                    if count % 4 == 0 and count != 0:
                        cp.write('</tr><tr>')
                    cp.write('''<td width="25%">'''+c+'</td>')
                    count += 1
                    print('|**Writting: ', count, '...')
                cp.write('</tr></table></body></html>')
