#!/usr/bin/env python

from Model import Posts
import Util
import pickle

def main():
    count = 0
    documents = []
    for Post in Posts.select().where(Posts.posttypeid == 1):
        count += 1
        documents.append(Util.stripTags(Post.body).replace('\n', ' ').replace('\r', ' '))

    from gensim import corpora, models, similarities
    # TODO preprocessing of text. Maybe remove punctuations.
    # remove common words and tokenize
    stoplist = set('for a of the and to in'.split())
    texts = [[word for word in document.lower().split() if word not in stoplist]
             for document in documents]

    # TODO try without removing words that appear only once
    # remove words that appear only once
    from collections import defaultdict
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if frequency[token] > 1]
             for text in texts]


    dictionary = corpora.Dictionary(texts)
    dictionary.save('questions.dict') # store the dictionary, for future reference

    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('questions.mm', corpus) # store to disk, for later use

    with open("questions.list", 'w') as fout:
        pickle.dump(documents, fout)

if __name__ == "__main__":
    main()
