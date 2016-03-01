import logging
import codecs
import time
from urllib.request import urlopen, Request

from lxml.html import parse

from . import model

logger = logging.getLogger(__name__)

COMMENT_URL = "https://www.wikifolio.com/dynamic/de/de/invest/" \
              "getpagedmessagesforwikifolio/{name}?Id={id}" \
              "&tv=False" \
              "&id={id}" \
              "&page=1" \
              "&pageSize=5" \
              "&_={timestamp}"
TRADES_URL = "https://www.wikifolio.com/dynamic/de/de/invest/" \
             "getpagedtradesforwikifolio/{name}?id={id}" \
             "&page=1&pageSize=100"
USER_AGENT = "Mozilla/4.0 (compatible; MSIE 6.0; " \
             "Windows NT 5.1; FSL 7.0.6.01001)"


def make_request(url):
    """:rtype: Request"""
    logging.info("Make request: {}".format(url))
    request = Request(url)
    request.add_header("User-Agent", USER_AGENT)
    return request


def get_id_from_name(name):
    """
    :param name: sanitized name of the certificate (line in url)
    :rtype: model.Certificate
    """
    request = make_request(model.BASE_URL + name)
    with urlopen(request) as input_raw:
        document = parse(codecs.getreader('utf-8')(input_raw))
        try:
            return model.Certificate(
                    name,
                    document.find('//input[@id="wikifolio"]').value,
                    document.find('//input[@id="wikifolio-shortdesc"]').value,
                    document.find('//input[@id="wikifolio-isin"]').value,
                    document.find('//div[@data-trader]').get('data-trader'))
        except:
            raise Exception("Failed to find wikifolio infos (id,name,isin) in html page")


def get_comments(cert):
    """:type cert: model.Certificate"""
    logger.info("Fetch comments of {.name}".format(cert))
    request = make_request(COMMENT_URL.format(
            id=cert.guid, name=cert.name, timestamp=int(time.time())))
    with urlopen(request) as input_raw:
        document = parse(codecs.getreader('utf-8')(input_raw))
        comments = document.findall('//div[@class="user-comment"]')
        for div_comment in comments:
            pubDate = div_comment.find('div/time').get('datetime')
            yield model.Comment(
                    time.strptime(pubDate, "%d.%m.%Y %H:%M:%S"),
                    "{trader} <{trader}@localhost>".format(trader=cert.trader),
                    div_comment.find('div[@class="message-item-content"]').text,
                    div_comment.get('id'),
                    cert.make_url())

def get_trades(cert):
    """:type cert: model.Certificate"""
    request = make_request(TRADES_URL.format(name=cert.name, id=cert.guid))
    with urlopen(request) as input_raw:
        document = parse(codecs.getreader('utf-8')(input_raw))
        trade_blocks = document.findall('//table/tr')

        share_name = share_isin = None
        for trade_block in trade_blocks:
            typ = trade_block.find('td[2]').text.strip()
            if typ != "": # not a continuation
                share_name = trade_block.find('td[1]/div/a/span').text.strip()
                share_isin = trade_block.find('td[1]/div/div').text.strip()
            else: # a continuaton, read type from first column
                typ = trade_block.find('td[1]/span').text.strip()
            timestamp = trade_block.find('td[3]/div[2]').text.strip()
            timestamp = timestamp.replace('\xa0', ' ')
            timestamp = time.strptime(timestamp, "%d.%m.%Y %H:%M")
            yield model.Trade(share_name,
                              share_isin,
                              typ,
                              trade_block.find('td[3]/div[1]').text.strip(), #status
                              timestamp,
                              trade_block.find('td[4]').text.strip(), #quote
                              trade_block.find('td[5]').text.strip()) # kurs