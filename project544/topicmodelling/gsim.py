import pickle
from collections import defaultdict
from gensim import corpora, models, similarities
from nltk.tokenize import word_tokenize
from .. import util
from .. import config
from ..model import Posts,Users

class Gensim:

    def __init__(self):

        stoplist = open(config.STOPLIST, 'r')
        self.stoplist = set([word.rstrip('\n') for word in stoplist])
        stoplist.close()

        self.dictionary = None
        self.questionmodel = None
        self.answermodel = None
        self.combinedmodel = None
        self.usermodel = None

    def PreprocessPostContent(self, post):
        return util.stripTags(post).replace('\n', ' ').replace('\r', ' ')

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

    def GetUserAnswers(self, userid):
        doccount = 0
        aggregate = ''

        for Post in Posts.select().where((Posts.owneruserid==userid) & (Posts.posttypeid==2)):
            doccount+=1
            aggregate = aggregate + ' ' + Post.body

        return aggregate

    def CreateDictionaryFromPosts(self, dictionaryfile=config.DICTIONARY):
        documents = []
        questionlist = self.GetQuestions()
        documents.extend(questionlist)
        answerlist = self.GetAnswers()
        documents.extend(answerlist)

        texts = self.PreprocessDocuments(documents)

        dictionary = corpora.Dictionary(texts)
        dictionary.save(dictionaryfile)

    def LoadDictionary(self, dictionaryfile=config.DICTIONARY):
        self.dictionary = corpora.Dictionary.load(dictionaryfile)

    def CreateQuestionCorpus(self, questioncorpusfile=config.QUESTIONS):

        if(self.dictionary == None):
            self.LoadDictionary()

        questions = self.GetQuestions()
        texts = self.PreprocessDocuments(questions)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(questioncorpusfile, corpus)

        with open(config.QUESTION_LIST, 'w') as fout:
            pickle.dump(questions, fout)

    def CreateAnswerCorpus(self, answercorpusfile=config.ANSWERS):

        if(self.dictionary == None):
            self.LoadDictionary()

        answers = self.GetAnswers()
        texts = self.PreprocessDocuments(answers)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(answercorpusfile, corpus)

        with open(config.ANSWER_LIST, 'w') as fout:
            pickle.dump(answers, fout)

    def CreateCombinedCorpus(self, corpusfile=config.COMBINED):

        if(self.dictionary == None):
            self.LoadDictionary()

        questions = self.GetQuestions()
        answers = self.GetAnswers()
        combined = questions + answers
        texts = self.PreprocessDocuments(combined)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(corpusfile, corpus)

    def CreateTopicModel(self, method, corpus):
        model = None

        if(method=='lda_mallet'):
            model = models.wrappers.LdaMallet(config.MALLET_PATH, corpus, id2word=self.dictionary, num_topics=config.NUM_TOPICS_LDA)
        elif(method=='lda'):
            model = models.LdaModel(corpus, ld2word=self.dictionary, num_topics=config.NUM_TOPICS_LDA)

        return model

    def CreateQuestionTopicModel(self, method=config.TOPICMODEL_METHOD, corpusfile=config.QUESTIONS, modelfile=config.QUESTION_MODEL, indexfile=config.QUESTION_INDEX):
        if(self.dictionary==None):
            self.LoadDictionary()

        corpus = corpora.MmCorpus(corpusfile)
        model = self.CreateTopicModel(method, corpus)
        index = similarities.MatrixSimilarity(model[corpus])

        model.save(modelfile)
        index.save(indexfile)

    def CreateAnswerTopicModel(self, method=config.TOPICMODEL_METHOD, corpusfile=config.ANSWERS, modelfile=config.ANSWER_MODEL, indexfile=config.ANSWER_INDEX):
        if(self.dictionary==None):
            self.LoadDictionary()

        corpus = corpora.MmCorpus(corpusfile)
        model = self.CreateTopicModel(method, corpus)
        index = similarities.MatrixSimilarity(model[corpus])

        model.save(modelfile)
        index.save(indexfile)

    def CreateCombinedTopicModel(self, method=config.TOPICMODEL_METHOD, corpusfile=config.COMBINED, modelfile=config.COMBINED_MODEL, indexfile=config.COMBINED_INDEX):
        if(self.dictionary==None):
            self.LoadDictionary()

        corpus = corpora.MmCorpus(corpusfile)
        model = self.CreateTopicModel(method, corpus)
        index = similarities.MatrixSimilarity(model[corpus])

        model.save(modelfile)
        index.save(indexfile)

    def LoadModel(self,modelfile):
        if(config.TOPICMODEL_METHOD=='lda_mallet'):
            model = models.wrappers.LdaMallet.load(modelfile)
        elif(config.TOPICMODEL_METHOD=='lda'):
            model = models.LdaModel.load(modelfile)

        return model

    def GetDocumentModel(self, document, model):
        if(self.dictionary == None):
            self.LoadDictionary()

        document_model = None
        if(document!=None and len(document)>1):
            documenttext = self.PreprocessDocuments([self.PreprocessPostContent(document)])
            document_bow = self.dictionary.doc2bow(documenttext[0])
            document_model = model[document_bow]

        return document_model

    def GetQuestionDocumentModel(self, document, modelfile=config.QUESTION_MODEL):
        if(self.dictionary == None):
            self.LoadDictionary()

        if(self.questionmodel==None):
            self.questionmodel = self.LoadModel(modelfile)

        document_model = self.GetDocumentModel(document, self.questionmodel)
        return document_model

    def GetAnswerDocumentModel(self, document, modelfile=config.ANSWER_MODEL):
        if(self.dictionary == None):
            self.LoadDictionary()

        if(self.answermodel==None):
            self.answermodel = self.LoadModel(modelfile)

        document_model = self.GetDocumentModel(document, self.answermodel)
        return document_model

    def GetCombinedDocumentModel(self, document, modelfile=config.COMBINED_MODEL):
        if(self.dictionary == None):
            self.LoadDictionary()

        if(self.combinedmodel==None):
            self.combinedmodel = self.LoadModel(modelfile)

        document_model = self.GetDocumentModel(document, self.combinedmodel)
        return document_model

    def GetUserTopicDistribution(self, userid):
        if(self.dictionary == None):
            self.LoadDictionary()

        document = self.GetUserAnswers(userid)
        user_topicdist = self.GetCombinedDocumentModel(document)
        return user_topicdist

    def CreateUserTopicCorpus(self, userfile=config.USERS):
        usercorpus = []

        index = 0
        for User in Users.select().limit(100):
            user_topicmodel = self.GetUserTopicDistribution(User.id)
            if(user_topicmodel!=None):
                User.usercorpusid = index
                usercorpus.append(user_topicmodel)
                index = index + 1
                User.save()

        corpora.MmCorpus.serialize(userfile, usercorpus)

    def CreateUserTopicModel(self, corpusfile=config.USERS, modelfile=config.USER_MODEL, indexfile=config.USER_INDEX):
        if(self.dictionary == None):
            self.LoadDictionary()

        corpus = corpora.MmCorpus(corpusfile)
        model = models.LsiModel(corpus, id2word=self.dictionary, num_topics=config.NUM_TOPICS_LDA)
        index = similarities.MatrixSimilarity(model[corpus])

        model.save(modelfile)
        index.save(indexfile)

    def FindSimilarQuestions(self, question, method=config.TOPICMODEL_METHOD, modelfile=config.QUESTION_MODEL, indexfile=config.QUESTION_INDEX):
        question_model = self.GetQuestionDocumentModel(question, method, modelfile)
        index = similarities.MatrixSimilarity.load(indexfile)
        sims = index[question_model]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        with open(config.QUESTION_LIST, 'r') as fin:
            documents = pickle.load(fin)

        i = 0
        for sim in sims:
            i = i + 1
            print(str(sim[1]) + '\t' + str(sim[0]) + '\t' + documents[sim[0]].encode('utf-8'))

            if(i > 5):
                break

    def FindSimilarAnswers(self, question, method=config.TOPICMODEL_METHOD, modelfile=config.ANSWER_MODEL, indexfile=config.ANSWER_INDEX):
        question_model = self.GetAnswerDocumentModel(question, method, modelfile)
        index = similarities.MatrixSimilarity.load(indexfile)
        sims = index[question_model]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        with open(config.ANSWER_LIST, 'r') as fin:
            documents = pickle.load(fin)

        i = 0
        for sim in sims:
            i = i + 1
            print(str(sim[1]) + '\t' + str(sim[0]) + '\t' + documents[sim[0]].encode('utf-8'))
            if(i > 5):
                break

    def FindExperts(self, question, modelfile=config.USER_MODEL, indexfile=config.USER_INDEX):
        query_model = self.GetCombinedDocumentModel(question)
        index = similarities.MatrixSimilarity.load(indexfile)
        sims = index[query_model]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        i = 0
        for sim in sims:
            i = i + 1
            user = [user for user in Users.select().where(Users.usercorpusid==sim[0])][0]
            print user.displayname+', ' + user.location +', ' + str(user.age)
            if(i > 5):
                break
