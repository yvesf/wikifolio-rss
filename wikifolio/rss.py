from . import model

import time
import typing

from ll.xist import xsc
from ll.xist.ns import xml, rss20


def dump_comments(cert: model.Certificate, comments: typing.Iterable[model.Comment]):
    title = "{.name} / {.isin}".format(cert, cert)
    items = []
    for comment in comments:
        items.append(rss20.item(
            rss20.title("Kommentar: " + title),
            rss20.author(comment.author),
            rss20.pubDate(time.strftime("%a, %d %b %Y %T %z",
                                        comment.pubDate)),
            rss20.guid(comment.guid),
            rss20.link(comment.link),
            rss20.description(comment.description)
        ))
    return xsc.Frag(xml.XML(),
                    rss20.rss(rss20.channel(
                        rss20.title(title),
                        *items
                    ))).string('utf-8')


def dump_trades(cert: model.Certificate, trades: typing.Iterable[model.Trade]):
    title = "{.name} / {.isin}".format(cert, cert)
    items = []
    for trade in trades:
        trade_title = trade.typ + " " + str(trade.volume) + "@" + str(trade.quote) + " " + trade.share_name
        description = trade.typ + " " + str(trade.volume) + "@" + str(trade.quote) + " " + trade.share_name
        description += " ( " + trade.share_isin + " ) "

        items.append(rss20.item(
            rss20.title(trade_title),
            rss20.author(cert.name),
            rss20.pubDate(trade.timestamp.strftime("%a, %d %b %Y %T %z")),
            rss20.guid(trade.timestamp.strftime("%a, %d %b %Y %T %z")),
            rss20.link(cert.make_url()),
            rss20.description(description)
        ))
    return xsc.Frag(xml.XML(),
                    rss20.rss(rss20.channel(
                        rss20.title(title),
                        *items
                    ))).string('utf-8')
