import bs4
from bs4 import BeautifulSoup
import nltk
from nltk import sent_tokenize, word_tokenize, pos_tag_sents, pos_tag
from nltk.corpus import conll2000

from SimpleChunkParser import SimpleChunkParser

def stripTags(html):
    return BeautifulSoup(html).getText()

def htmlSentTokenize(html, containerTags = ("ul", "li", "ol", "[document]")):
    textList = []
    def recur(node):
        if isinstance(node, bs4.NavigableString):
            textList.append(node.string)
        elif  isinstance(node, bs4.Tag) and node.name not in containerTags:
            textList.append(node.getText())
        else:
            for child in node.children:
                recur(child)
    soup = bs4.BeautifulSoup(html)
    recur(soup)
    return [
        sent
        for text in textList if len(text.strip()) > 0
        for sent in sent_tokenize(text)
    ]


def isCandidateChunk(chunk):
    if not isinstance(chunk, nltk.Tree):
        return False

    if chunk.label() != "NP":
        return False

    for word, pos in chunk:
        if pos.startswith("NN"):
            return True

    return False

chunker = None

def getNounPhrases(html):
    global chunker
    if chunker is None:
        trainingChunkedSents = conll2000.chunked_sents("train.txt")#, chunk_types=['NP'])
        chunker = SimpleChunkParser(trainingChunkedSents)

    return [
        " ".join(word for word, pos in chunk)
        for sent in htmlSentTokenize(html)
        for chunk in chunker.parse(pos_tag(word_tokenize(sent)))
        if isCandidateChunk(chunk)
    ]