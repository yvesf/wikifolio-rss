import time

from . import model

from ll.xist import xsc
from ll.xist.ns import xml, rss20


def dump(cert, comments):
    """
    :type cert: model.Certificate
    :type comments: list[model.Comment]
    """
    title = "{.name} / {.isin}".format(cert, cert)
    items = []
    for comment in comments:
        items.append(rss20.item(
                rss20.title("Kommentar " + title),
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
