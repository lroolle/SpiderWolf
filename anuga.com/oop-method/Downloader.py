import requests



class Downloader:
    def down_html(self, url):
        proxies = {
                    "http": "http://127.0.0.1:8580",
                    "https": "http://127.0.0.1:8580",
        }

        if url is None:
            return
        else:
            print('|** Requesting: %s ' % url)
            try:
                response = requests.get(url, auth=('user', 'pass'), proxies=proxies)
                return response.text
            except Exception as e:
                print('|***Errrrr:', e)




