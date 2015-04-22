import Util
import Config
import pickle
from Model import Posts,Users
from collections import defaultdict
from gensim import corpora, models, similarities
from nltk.tokenize import word_tokenize


class Gensim:

    def __init__(self):

        stoplist = open(Config.STOPLIST, 'r')
        self.stoplist = set([word.rstrip('\n') for word in stoplist])
        stoplist.close()

        self.dictionary = None
        self.questionmodel = None
        self.answermodel = None
        self.usermodel = None

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

    def GetUserAnswers(self, userid):
        doccount = 0
        aggregate = ''

        for Post in Posts.select().where((Posts.owneruserid==userid) & (Posts.posttypeid==2)):
            doccount+=1
            aggregate = aggregate + ' ' + Post.body

        return aggregate

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

        if(self.dictionary == None):
            self.LoadDictionary()

        questions = self.GetQuestions()
        texts = self.PreprocessDocuments(questions)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(questioncorpusfile, corpus)

        with open(Config.QUESTION_LIST, 'w') as fout:
            pickle.dump(questions, fout)

    def CreateAnswerCorpus(self, answercorpusfile=Config.ANSWERS):

        if(self.dictionary == None):
            self.LoadDictionary()

        answers = self.GetAnswers()
        texts = self.PreprocessDocuments(answers)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(answercorpusfile, corpus)

        with open(Config.ANSWER_LIST, 'w') as fout:
            pickle.dump(answers, fout)

    def CreateTopicModel(self, method, corpus):
        model = None

        if(method=='lda_mallet'):
            model = models.wrappers.LdaMallet(Config.MALLET_PATH, corpus, id2word=self.dictionary, num_topics=Config.num_topics_lda)
        elif(method=='lda'):
            model = models.LdaModel(corpus, ld2word=self.dictionary, num_topics=Config.num_topics_lda)

        return model

    def CreateQuestionTopicModel(self, method=Config.TOPICMODEL_METHOD, corpusfile=Config.QUESTIONS, modelfile=Config.QUESTION_MODEL, indexfile=Config.QUESTION_INDEX):

        if(self.dictionary==None):
            self.LoadDictionary()

        corpus = corpora.MmCorpus(corpusfile)
        model = self.CreateTopicModel(method, corpus)
        index = similarities.MatrixSimilarity(model[corpus])

        model.save(modelfile)
        index.save(indexfile)

    def CreateAnswerTopicModel(self, method=Config.TOPICMODEL_METHOD, corpusfile=Config.ANSWERS, modelfile=Config.ANSWER_MODEL, indexfile=Config.ANSWER_INDEX):

        if(self.dictionary==None):
            self.LoadDictionary()

        corpus = corpora.MmCorpus(corpusfile)
        model = self.CreateTopicModel(method, corpus)
        index = similarities.MatrixSimilarity(model[corpus])

        model.save(modelfile)
        index.save(indexfile)

    def LoadModel(self,modelfile):
        if(Config.TOPICMODEL_METHOD=='lda_mallet'):
            model = models.wrappers.LdaMallet.load(modelfile)
        elif(Config.TOPICMODEL_METHOD=='lda'):
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

    def GetQuestionDocumentModel(self, document, modelfile=Config.QUESTION_MODEL):
        if(self.dictionary == None):
            self.LoadDictionary()

        if(self.questionmodel==None):
            self.questionmodel = self.LoadModel(modelfile)

        document_model = self.GetDocumentModel(document, self.questionmodel)
        return document_model

    def GetAnswerDocumentModel(self, document, modelfile=Config.ANSWER_MODEL):
        if(self.dictionary == None):
            self.LoadDictionary()

        if(self.answermodel==None):
            self.answermodel = self.LoadModel(modelfile)

        document_model = self.GetDocumentModel(document, self.answermodel)
        return document_model

    def GetUserTopicDistribution(self, userid):

        if(self.dictionary == None):
            self.LoadDictionary()

        document = self.GetUserAnswers(userid)
        user_topicdist = self.GetQuestionDocumentModel(document)
        return user_topicdist

    def CreateUserTopicCorpus(self, userfile=Config.USERS):
        usercorpus = []

        index = 0
        for User in Users.select().limit(1000):
            user_topicmodel = self.GetUserTopicDistribution(User.id)
            if(user_topicmodel!=None):
                User.usercorpusid = index
                usercorpus.append(user_topicmodel)
                index = index + 1
                User.save()

        corpora.MmCorpus.serialize(userfile, usercorpus)

    def CreateUserTopicModel(self, corpusfile=Config.USERS, modelfile=Config.USER_MODEL, indexfile=Config.USER_INDEX):

        if(self.dictionary == None):
            self.LoadDictionary()

        corpus = corpora.MmCorpus(corpusfile)
        model = models.LsiModel(corpus, id2word=self.dictionary, num_topics=Config.num_topics_lsi)
        index = similarities.MatrixSimilarity(model[corpus])

        model.save(modelfile)
        index.save(indexfile)

    def FindSimilarQuestions(self, question, method=Config.TOPICMODEL_METHOD, modelfile=Config.QUESTION_MODEL, indexfile=Config.QUESTION_INDEX):
        question_model = self.GetQuestionDocumentModel(question, method, modelfile)
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

    def FindSimilarAnswers(self, question, method=Config.TOPICMODEL_METHOD, modelfile=Config.ANSWER_MODEL, indexfile=Config.ANSWER_INDEX):
        question_model = self.GetAnswerDocumentModel(question, method, modelfile)
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

    def FindExperts(self, question, modelfile=Config.USER_MODEL, indexfile=Config.USER_INDEX):
        query_model = self.GetQuestionDocumentModel(question)
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
        # print sims
