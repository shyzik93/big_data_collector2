import lxml.html as html
from lxml.html.clean import Cleaner
from . import saver_base

class SaverSQL(saver_base.SaverSQL):

    def __init__(self, mtables, path_to_save):

        saver_base.SaverSQL.__init__(self, mtables, path_to_save)
        self.cleaner_cls = Cleaner(
            scripts=True,
            javascript=True,
            style=True,
            comments=True,
            inline_style=True,
            links=True,
            forms=True,
            meta=True,
            page_structure=False,
            kill_tags=['header', 'h1', 'noscript', 'h4', 'footer', 'nav']
        )

    def cleaner(self, d, selectors):

        for selector in selectors:
            els = d.cssselect(selector)
            for el in els:
                el.getparent().remove(el)

    def open(self, url_index):
        d = saver_base.SaverSQL.open(self, url_index)
        return html.document_fromstring(d)

    def save(self, req, url, selectors=None):

        if req.headers['Content-Type'].startswith("text/"):
            content = req.text
        else:
            content = req.content

        document = html.document_fromstring(content)
        title = document.cssselect('title')[0].text_content()

        document = self.cleaner_cls.clean_html(document)
        if selectors: self.cleaner(document, selectors)

        document.make_links_absolute(base_url=url)

        index = saver_base.SaverSQL.save(self, html.tostring(document, encoding='unicode'), url, title)

        return index, document