from gensim import corpora, models, similarities
from .. import config
import tm_util
import tm_content

class TopicModelGen:

    def __init__(self):

        stoplist = open(config.STOPLIST, 'r')
        self.stoplist = set([word.rstrip('\n') for word in stoplist])
        stoplist.close()

        self.dictionary = None

    def createDictionary(self, dictionaryfile=config.DICTIONARY):
        documents = []

        questionlist = tm_content.getQuestions()
        documents.extend(questionlist)
        answerlist = tm_content.getAnswers()
        documents.extend(answerlist)

        texts = tm_util.preprocessDocs(documents, self.stoplist)

        dictionary = corpora.Dictionary(texts)
        dictionary.save(dictionaryfile)

    def loadDictionary(self, dictionaryfile=config.DICTIONARY):
        self.dictionary = corpora.Dictionary.load(dictionaryfile)



    def createCorpus(self, postlist, corpusfile):
        if(self.dictionary == None):
            self.loadDictionary()
        texts = tm_util.preprocessDocs(postlist, self.stoplist)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(corpusfile, corpus)

    def createQuestionCorpus(self, questioncorpusfile=config.QUESTIONS):
        questionlist = tm_content.getQuestions()
        self.createCorpus(questionlist, questioncorpusfile)

    def createAnswerCorpus(self, answercorpusfile=config.ANSWERS):
        answerlist = tm_content.GetAnswers()
        self.createCorpus(answerlist, answercorpusfile)

    def createCombinedCorpus(self, combinedcorpusfile=config.COMBINED):
        questionlist = tm_content.getQuestions()
        answerlist = tm_content.getAnswers()
        combinedlist = questionlist + answerlist
        self.createCorpus(combinedlist, combinedcorpusfile)



    def createTopicModel(self, method, corpus, modelfile, indexfile):
        if(self.dictionary == None):
            self.loadDictionary()
        if(method=='lda_mallet'):
            model = models.wrappers.LdaMallet(config.MALLET_PATH, corpus, id2word=self.dictionary, num_topics=config.NUM_TOPICS_LDA)
        elif(method=='lda'):
            model = models.LdaModel(corpus, ld2word=self.dictionary, num_topics=config.NUM_TOPICS_LDA)
        index = similarities.MatrixSimilarity(model[corpus])
        model.save(modelfile)
        index.save(indexfile)

    def createQuestionTopicModel(self, method=config.TOPICMODEL_METHOD, corpusfile=config.QUESTIONS, modelfile=config.QUESTION_MODEL, indexfile=config.QUESTION_INDEX):
        corpus = corpora.MmCorpus(corpusfile)
        self.createTopicModel(method, corpus, modelfile, indexfile)

    def createAnswerTopicModel(self, method=config.TOPICMODEL_METHOD, corpusfile=config.ANSWERS, modelfile=config.ANSWER_MODEL, indexfile=config.ANSWER_INDEX):
        corpus = corpora.MmCorpus(corpusfile)
        self.createTopicModel(method, corpus, modelfile, indexfile)

    def createCombinedTopicModel(self, method=config.TOPICMODEL_METHOD, corpusfile=config.COMBINED, modelfile=config.COMBINED_MODEL, indexfile=config.COMBINED_INDEX):
        corpus = corpora.MmCorpus(corpusfile)
        self.createTopicModel(method, corpus, modelfile, indexfile)

    def createUserTopicModel(self, corpusfile=config.USERS, modelfile=config.USER_MODEL, indexfile=config.USER_INDEX):
        if(self.dictionary == None):
            self.loadDictionary()
        corpus = corpora.MmCorpus(corpusfile)
        model = models.LsiModel(corpus, id2word=self.dictionary, num_topics=config.NUM_TOPICS_LDA)
        index = similarities.MatrixSimilarity(model[corpus])
        model.save(modelfile)
        index.save(indexfile)
