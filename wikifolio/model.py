BASE_URL = "https://www.wikifolio.com/de/de/wikifolio/"


class Certificate:
    def __init__(self, id, shortdesc, isin, trader):
        self.id = id
        self.name = shortdesc
        self.isin = isin
        self.trader = trader

    def make_url(self):
        return BASE_URL + self.name

    def __repr__(self):
        return "<{} id={} shortdesc=\"{}\" isin={}>".format(
                self.__class__.__name__, self.id, self.name, self.isin)


class Comment:
    def __init__(self, date, author, text, guid, link):
        self.pubDate = date
        self.author = author
        self.description = text
        self.guid = guid
        self.link = link
