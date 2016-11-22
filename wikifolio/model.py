BASE_URL = "https://www.wikifolio.com/de/de/wikifolio/"


class _WithRepr:
    def __repr__(self):
        return "<{} {}".format(type(self).__name__,
                               " ".join(map(lambda kv: "{}={}".format(*kv), self.__dict__.items())))


class Certificate(_WithRepr):
    def __init__(self, name, guid, shortdesc, isin, trader):
        self.name = name
        self.guid = guid
        self.shortdesc = shortdesc
        self.isin = isin
        self.trader = trader

    def make_url(self):
        return BASE_URL + self.name


class Comment(_WithRepr):
    def __init__(self, date, author, text, guid, link):
        self.pubDate = date
        self.author = author
        self.description = text
        self.guid = guid
        self.link = link


class Trade(_WithRepr):
    TYPE_KAUF = 'Quote Kauf'
    TYPE_VERKAUF = 'Quote Verkauf'
    TYPES_KAUF = ('Quote Kauf', 'Limit Kauf', 'Stop-Limit Kauf', 'Rückabwicklung Verkauf')
    TYPES_VERKAUF = ('Quote Verkauf', 'Limit Verkauf', 'Stop-Limit Verkauf', 'Rückabwicklung Kauf')
    STATUS_AUSGEFUEHRT = 'Ausgeführt'

    def __init__(self, share_name, share_isin, typ, status, timestamp, quote, volume):
        self.share_name = share_name
        self.share_isin = share_isin
        self.typ = typ
        self.status = status
        self.timestamp = timestamp
        self.quote = quote
        self.volume = volume
