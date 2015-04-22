import Util
import Config
import pickle

from Model import Posts
from collections import defaultdict
from gensim import corpora, models, similarities
from nltk.tokenize import word_tokenize

class Gensim:

    def __init__(self):

        stoplist = open(Config.STOPLIST, 'r')
        self.stoplist = set([word.rstrip('\n') for word in stoplist])
        stoplist.close()

        self.dictionary = None

    def PreprocessPostContent(self, post):
        return Util.stripTags(post).replace('\n', ' ').replace('\r', ' ')

    def PreprocessDocuments(self, documents):
        texts = [[word for word in word_tokenize(document.lower()) if word not in self.stoplist] for document in documents]

        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1
        texts = [[token for token in text if frequency[token] > 1 and len(token) > 2 ] for text in texts]

        return texts

    def GetQuestions(self):
        questionlist = []

        for Post in Posts.select().where(Posts.posttypeid == 1):
            postcontent = self.PreprocessPostContent(Post.title) + ' ' + self.PreprocessPostContent(Post.body)
            questionlist.append(postcontent)

        return questionlist

    def GetAnswers(self):
        answerlist = []

        for Post in Posts.select().where(Posts.posttypeid==2):
            postcontent = self.PreprocessPostContent(Post.body)
            answerlist.append(postcontent)

        return answerlist

    def GetUserAggregate(self, userid):
        doccount = 0
        aggregate = ''

        for Post in Posts.select().where((Posts.owneruserid==userid) & (Posts.posttypeid==2)):
            postcontent = self.PreprocessPostContent(Post.body)
            doccount+=1
            aggregate = aggregate + ' ' + postcontent

        return aggregate

    def FindUserTopicDistribution(self, userid, method=Config.TOPICMODEL_METHOD, modelfile=Config.QUESTION_MODEL, indexfile=Config.QUESTION_INDEX):

        if(self.dictionary == None):
            self.LoadDictionary()

        useraggregate = self.PreprocessDocuments([self.GetUserAggregate(userid)])
        aggregate_bow = self.dictionary.doc2bow(useraggregate[0])

        if(method=='lda_mallet'):
            lda_model = models.wrappers.LdaMallet.load(modelfile)
            aggregate_model = lda_model[aggregate_bow]
        elif(method=='lda'):
            lda_model = models.LdaModel.load(modelfile)
            aggregate_model = lda_model[aggregate_bow]

        print aggregate_model


    def CreateDictionaryFromPosts(self, dictionaryfile=Config.DICTIONARY):

        documents = []
        questionlist = self.GetQuestions()
        documents.extend(questionlist)
        answerlist = self.GetAnswers()
        documents.extend(answerlist)

        texts = self.PreprocessDocuments(documents)

        dictionary = corpora.Dictionary(texts)
        dictionary.save(dictionaryfile)

    def LoadDictionary(self, dictionaryfile=Config.DICTIONARY):
        self.dictionary = corpora.Dictionary.load(dictionaryfile)

    def CreateQuestionCorpus(self, questioncorpusfile=Config.QUESTIONS):

        documents = self.GetQuestions()
        texts = self.PreprocessDocuments(documents)

        if(self.dictionary == None):
            self.LoadDictionary()

        corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(questioncorpusfile, corpus)

        with open(Config.QUESTION_LIST, 'w') as fout:
            pickle.dump(documents, fout)

    def CreateAnswerCorpus(self, answercorpusfile=Config.ANSWERS):

        documents = self.GetAnswers()
        texts = self.PreprocessDocuments(documents)

        if(self.dictionary == None):
            self.LoadDictionary()

        corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(answercorpusfile, corpus)

        with open(Config.ANSWER_LIST, 'w') as fout:
            pickle.dump(documents, fout)

    def CreateQuestionTopicModel(self, method=Config.TOPICMODEL_METHOD, corpusfile=Config.QUESTIONS, modelfile=Config.QUESTION_MODEL, indexfile=Config.QUESTION_INDEX):

        if(self.dictionary == None):
            self.LoadDictionary()

        corpus = corpora.MmCorpus(corpusfile)

        if(method=='lda_mallet'):
            model = models.wrappers.LdaMallet(Config.MALLET_PATH, corpus, id2word=self.dictionary, num_topics = Config.num_topics_lda)
            index = similarities.MatrixSimilarity(model[corpus])
        elif(method=='lda'):
            model = models.LdaModel(corpus, ld2word=self.dictionary, num_topics=Config.num_topics_lda)
            index = similarities.MatrixSimilarity(model[corpus])
        elif(method=='lsi'):
            tfidf = models.TfidfModel(corpus)
            corpus_tfidf = tfidf[corpus]
            model = models.LsiModel(corpus_tfidf, id2word=self.dictionary, num_topics=Config.num_topics_lsi)
            index = similarities.MatrixSimilarity(model[corpus_tfidf])

        model.save(modelfile)
        index.save(indexfile)

    def GetDocumentModel(self, document, method=Config.TOPICMODEL_METHOD, modelfile=Config.QUESTION_MODEL):

        if(self.dictionary == None):
            self.LoadDictionary()

        documenttext = self.PreprocessDocuments([self.PreprocessPostContent(document)])
        document_bow = self.dictionary.doc2bow(documenttext[0])
        document_model = None

        if(method=='lda_mallet'):
            lda_model = models.wrappers.LdaMallet.load(modelfile)
            document_model = lda_model[document_bow]
        elif(method=='lda'):
            lda_model = models.LdaModel.load(modelfile)
            document_model = lda_model[document_bow]

        return document_model

    def FindSimilarQuestions(self, question, method=Config.TOPICMODEL_METHOD, modelfile=Config.QUESTION_MODEL, indexfile=Config.QUESTION_INDEX):

        question_model = self.GetDocumentModel(question, method, modelfile)
        index = similarities.MatrixSimilarity.load(indexfile)
        sims = index[question_model]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        with open(Config.QUESTION_LIST, 'r') as fin:
            documents = pickle.load(fin)

        i = 0
        for sim in sims:
            i = i + 1
            print(str(sim[1]) + '\t' + str(sim[0]) + '\t' + documents[sim[0]].encode('utf-8'))
            if(i > 5):
                break

    def CreateAnswerTopicModel(self, method=Config.TOPICMODEL_METHOD, corpusfile=Config.ANSWERS, modelfile=Config.ANSWER_MODEL, indexfile=Config.ANSWER_INDEX):

        if(self.dictionary == None):
            self.LoadDictionary()

        corpus = corpora.MmCorpus(corpusfile)

        if(method=='lda_mallet'):
            lda = models.wrappers.LdaMallet(Config.MALLET_PATH, corpus, id2word=self.dictionary, num_topics=Config.num_topics_lda)
            lda.save(modelfile)
            index = similarities.MatrixSimilarity(lda[corpus])
            index.save(indexfile)

    def FindSimilarAnswers(self, question, method=Config.TOPICMODEL_METHOD, modelfile=Config.ANSWER_MODEL, indexfile=Config.ANSWER_INDEX):

        question_model = self.GetDocumentModel(question, method, modelfile)
        index = similarities.MatrixSimilarity.load(indexfile)
        sims = index[question_model]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        with open(Config.ANSWER_LIST, 'r') as fin:
            documents = pickle.load(fin)

        i = 0
        for sim in sims:
            i = i + 1
            print(str(sim[1]) + '\t' + str(sim[0]) + '\t' + documents[sim[0]].encode('utf-8'))
            if(i > 5):
                break
