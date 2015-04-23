import pickle
import Config
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora, models, similarities
dictionary = corpora.Dictionary.load('questions.dict')
corpus = corpora.MmCorpus('questions.mm')
#print(corpus)

tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
corpus_tfidf = tfidf[corpus]

query = "Templates no longer showing in Lightroom"
query_bow = dictionary.doc2bow(query.lower().split())
query_tfidf = tfidf[query_bow]

option = 2
if option == 1:
    lsi = models.LsiModel.load('model.lsi')
    query_model = lsi[query_tfidf]
    index = similarities.MatrixSimilarity.load('questions_lsi.index')
elif option == 2:
    #Calculating model again as was getting errors on loading
    rp = models.RpModel(corpus_tfidf, id2word=dictionary, num_topics=Config.num_topics_rp)
    query_model = rp[query_tfidf]
    index = similarities.MatrixSimilarity.load('questions_rp.index')
else:
    lda = models.LdaModel.load('model.lda')
    query_model = lda[query_bow]
    index = similarities.MatrixSimilarity.load('questions_lda.index')


sims = index[query_model] # perform a similarity query against the corpus
#print(list(enumerate(sims))) # print (document_number, document_similarity) 2-tuples

sims = sorted(enumerate(sims), key=lambda item: -item[1])

with open('questions.list', 'r') as fin:
    documents = pickle.load(fin)

for sim in sims:
    print(str(sim[1]) + '\t' + str(sim[0]) + '\t' + documents[sim[0]].encode('utf-8'))
