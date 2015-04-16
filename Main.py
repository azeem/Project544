#!/usr/bin/env python

from Model import Posts
import Util
from SimpleChunkParser import SimpleChunkParser

from nltk import sent_tokenize, word_tokenize, pos_tag_sents
from nltk.corpus import conll2000

def main():
    print("Creating Chunk Parser")
    trainingChunkedSents = conll2000.chunked_sents("train.txt")
    chunker = SimpleChunkParser(trainingChunkedSents)

    for post in Posts.select().where(Posts.posttypeid == 2).limit(5):
        print("Post ID: {:d}".format(post.id))
        bodyText = Util.stripTags(post.body)
        sents = pos_tag_sents(word_tokenize(sent) for sent in sent_tokenize(bodyText))
        for sent in sents:
            tree = chunker.parse(sent)
            print(tree)

if __name__ == "__main__":
    main()
