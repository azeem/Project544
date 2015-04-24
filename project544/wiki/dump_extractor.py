import re
import xml.etree.ElementTree as etree

def getWikiPages(xmlFiles):
    if not isinstance(xmlFiles, list):
        xmlFiles = [xmlFiles]

    for xmlFile in xmlFiles:
        page = {}
        for event, elem in etree.iterparse(xmlFile, events=("start", "end")):
            tagName = re.match(r"\{.*\}(.*)", elem.tag).group(1)

            if event == "start":
                if tagName == "title":
                    page["label"] = elem.text
                elif tagName == "redirect":
                    page["title"] = elem.attrib["title"]
                elif tagName == "text":
                    page["text"] = elem.text
            elif event == "end" and tagName == "page":
                yield page
                page = {}

if __name__ == "__main__":
    import sys
    from itertools import islice
    if len(sys.argv) != 2:
        print("Invalid arguments")
    else:
        file = open(sys.argv[1], "rb")
        print("\n\n".join(repr(s) for s in list(islice(getWikiPages(sys.argv[1]), 0, 200))))
