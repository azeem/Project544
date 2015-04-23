#!/usr/bin/env python
import Config
import logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def main():
    from gensim import corpora, models, similarities
    dictionary = corpora.Dictionary.load('questions.dict')
    corpus = corpora.MmCorpus('questions.mm')

    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    # TODO fine tune num_topics
    print('Generating lsi model and index')    
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=Config.num_topics_lsi)
    index1 = similarities.MatrixSimilarity(lsi[corpus_tfidf])
    lsi.save('model.lsi')
    index1.save('questions_lsi.index')

    print('Generating rp model and index') 
    random_projection = models.rpmodel.RpModel(corpus_tfidf, id2word=dictionary, num_topics=Config.num_topics_rp)
    index2 = similarities.MatrixSimilarity(random_projection[corpus_tfidf])
    random_projection.save('model.rp')
    index2.save('questions_rp.index')
    
    print('Generating lda model and index') 
    lda = models.LdaModel(corpus, id2word=dictionary, num_topics=Config.num_topics_lda)
    index3 = similarities.MatrixSimilarity(lda[corpus])
    lda.save('model.lda')
    index3.save('questions_lda.index')


 
if __name__ == "__main__":
    main()
