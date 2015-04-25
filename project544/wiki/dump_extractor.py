import mwparserfromhell as mwp
import random
import re
import xml.sax
from xml.sax import ContentHandler

INTERESTING_CATEGORIES = (
    "Marvel_Comics_superheroes",
    "Marvel_Comics_characters",
    "DC_Comics_superheroes",
    "DC_Comics_characters",
    "Harry_Potter_characters",
    "Star_Trek",
    "Star_Trek_characters"
)

class WikiContentHandler(ContentHandler):
    def __init__(self, part = None):
        self.tagStack = []
        self.part = part
        self.page = {}
        self.skip = False
        
    def _checkTags(self, *tags):
        for i, tag in enumerate(tags):
            tagInStack = self.tagStack[-(i+1)]
            if (isinstance(tag, tuple) and tagInStack not in tag) or (not isinstance(tag, tuple) and tag != tagInStack):
                return False
        return True

    def startElement(self, name, attrs):
        self.tagStack.append(name)
        if not self.skip and self._checkTags("page", "mediawiki") and self.part is not None:
            self.skip = random.randint(0, self.part-1) != 0

    def endElement(self, name):
        if self._checkTags("page", "mediawiki"):
            if self.skip:
                self.skip = False
            else:
                for key in self.page.keys():
                    self.page[key] = "".join(self.page[key])
                self.processWikiPage(self.page)
                self.page = {}
        self.tagStack.pop()

    def characters(self, content):
        if self.skip:
            return
        if self._checkTags(("title", "id", "ns"), "page") or self._checkTags("text", "revision"):
            key = self.tagStack[-1]
            if key not in self.page:
                self.page[key] = [content]
            else:
                self.page[key].append(content)

    def processWikiPage(self, page):
        if "text" not in page or page["text"].strip() == "":
            return
        tree = mwp.parse(page["text"])
        categories = [re.match(r"^Category\:(.*)", link.title.strip_code()).group(1) for link in tree.filter_wikilinks() if link.title.startswith("Category:")]
        isInteresting = False
        for category in categories:
            if category in INTERESTING_CATEGORIES:
                isInteresting = True

        if isInteresting:
            print(page)
            
        # print("\n".join([u"{0}({1})".format(heading.title, heading.level) for heading in tree.filter_headings()]))
        # print("\n".join([u"{0}".format(template.name) for template in tree.filter_templates()]))

def process(xmlFile):
    # for page in getWikiPages(xmlFile):
    #     if page.get("title", None) == "Autism":
    #         print(page)
    #         print(mwp.parse(page["text"]))
    #         return
    contentHandler = WikiContentHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(contentHandler)
    parser.parse(open(xmlFile, "r"))

if __name__ == "__main__":
    import sys
    from itertools import islice
    if len(sys.argv) != 2:
        print("Invalid arguments")
    else:
        process(sys.argv[1])
