

class UrlManager:

    def __init__(self):
        self.new_url = set()
        self.old_url = set()

    def have_newurl(self):
        if self.new_url is None:
            return
        else:
            return len(self.new_url) != 0

    def add_newurl(self, url):
        if url is None:
            return
        if url not in self.new_url and url not in self.old_url:
            self.new_url.add(url)

    def add_newurls(self, urls):
        if urls is None or len(urls) == 0:
            return
        for u in urls:
            self.add_newurl(u)

    def get_new(self):
        new_url = self.new_url.pop()
        self.old_url.add(new_url)
        return new_url