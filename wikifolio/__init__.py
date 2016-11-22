import typing
import logging
import codecs
import time
import datetime
from urllib.request import urlopen, Request

from lxml.html import parse

from . import model

logger = logging.getLogger(__name__)

COMMENT_URL = "https://www.wikifolio.com/dynamic/de/de/invest/" \
              "getpagedmessagesforwikifolio/{name}?Id={id}" \
              "&tv=False" \
              "&id={id}" \
              "&page=1" \
              "&pageSize=15" \
              "&_={timestamp}"
TRADES_URL = "https://www.wikifolio.com/dynamic/de/de/invest/" \
             "getpagedtradesforwikifolio/{name}?id={id}" \
             "&page=1&pageSize=100"
USER_AGENT = "Mozilla/4.0 (compatible; MSIE 6.0; " \
             "Windows NT 5.1; FSL 7.0.6.01001)"


def make_request(url) -> Request:
    logging.info("Make request: {}".format(url))
    request = Request(url)
    request.add_header("User-Agent", USER_AGENT)
    return request


def get_id_from_name(name: str) -> model.Certificate:
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


def get_comments(cert: model.Certificate) -> typing.Iterable[model.Comment]:
    logger.info("Fetch comments of {.name}".format(cert))
    request = make_request(COMMENT_URL.format(
        id=cert.guid, name=cert.name, timestamp=int(time.time())))
    with urlopen(request) as input_raw:
        document = parse(codecs.getreader('utf-8')(input_raw))
        comments = document.findall('//div[@class="user-comment"]')
        for div_comment in comments:
            pub_date = div_comment.find('div/time').get('datetime')
            yield model.Comment(
                time.strptime(pub_date, "%d.%m.%Y %H:%M:%S"),
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

        share_name = share_isin = kurs = None
        trades = []
        for trade_block in trade_blocks:
            try:
                typ = trade_block.find('td[2]').text.strip()
                if typ != "" and trade_block.find('td[1]/div/a/span') is not None:  # not a continuation
                    share_name = trade_block.find('td[1]/div/a/span').text.strip()
                    share_isin = trade_block.find('td[1]/div/div').text.strip()
                else:  # a continuaton, read type from first column
                    typ = trade_block.find('td[1]/span').text.strip()
                if trade_block.find('td[4]').text and trade_block.find('td[4]').text.strip() != "":
                    kurs = trade_block.find('td[4]').text.strip().replace('.', '').replace(',', '.')
                volume = trade_block.find('td[5]').text.strip().replace('.', '').replace(',', '.')
                timestamp = trade_block.find('td[3]/div[2]').text.strip()
                timestamp = timestamp.replace('\xa0', ' ')
                timestamp = datetime.datetime.strptime(timestamp, "%d.%m.%Y %H:%M")
                status = trade_block.find('td[3]/div[1]').text.strip()
                if status != model.Trade.STATUS_AUSGEFUEHRT:
                    continue  # skip pending ones

                trades.append(model.Trade(
                    share_name, share_isin, typ, status, timestamp, float(kurs), float(volume)
                ))
            except:
                raise Exception("failed to decode trade")  # to do: where?

        return trades
