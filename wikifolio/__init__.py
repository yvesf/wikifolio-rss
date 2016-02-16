import logging
import codecs
import time
import urllib.request

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
USER_AGENT = "Mozilla/4.0 (compatible; MSIE 6.0; " \
             "Windows NT 5.1; FSL 7.0.6.01001)"


def make_request(url):
    request = urllib.request.Request(url)
    request.add_header("User-Agent", USER_AGENT)
    return request


def get_id_from_name(name):
    """
    :param name: sanitized name of the certificate (line in url)
    :rtype: Certificate
    """
    request = make_request(model.BASE_URL + name)
    with urllib.request.urlopen(request) as input_raw:
        document = parse(codecs.getreader('utf-8')(input_raw))
        try:
            return model.Certificate(
                    document.find('//input[@id="wikifolio"]').value,
                    document.find('//input[@id="wikifolio-shortdesc"]').value,
                    document.find('//input[@id="wikifolio-isin"]').value,
                    document.find('//div[@data-trader]').get('data-trader'))
        except:
            raise Exception("Failed to find wikifolio infos (id,name,isin) in html page")


def get_comments(cert):
    """
    :type cert: Certificate instance
    """
    logger.info("Fetch comments of {.name}".format(cert))
    request = make_request(COMMENT_URL.format(
            id=cert.id, name=cert.name, timestamp=int(time.time())))
    with urllib.request.urlopen(request) as input_raw:
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
