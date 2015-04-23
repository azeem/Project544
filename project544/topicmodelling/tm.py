from gensim import corpora, models, similarities
from ..model import Users
from .. import config
import tm_util
import tm_content

class TopicModel:

    def __init__(self, modelfile=config.CURRENT_MODEL, indexfile=config.CURRENT_INDEX, method=config.TOPICMODEL_METHOD):
        stoplist = open(config.STOPLIST, 'r')
        self.stoplist = set([word.rstrip('\n') for word in stoplist])
        stoplist.close()

        self.dictionary = self.loadDictionary()
        self.model = self.loadTopicModel(modelfile, method)
        self.index = similarities.MatrixSimilarity.load(indexfile)

    def loadDictionary(self, dictionaryfile=config.DICTIONARY):
        return corpora.Dictionary.load(dictionaryfile)

    def loadTopicModel(self, modelfile, method):
        if(method=='lda_mallet'):
            model = models.wrappers.LdaMallet.load(modelfile)
        elif(method=='lda'):
            model = models.LdaModel.load(modelfile)
        return model

    def getDocumentFeatures(self, document):
        document_model = None
        if(document!=None and len(document)>1):
            documenttext = tm_util.preprocessDocs([tm_util.preprocessPost(document)], self.stoplist)
            document_bow = self.dictionary.doc2bow(documenttext[0])
            document_model = self.model[document_bow]
        return document_model

    def getUserFeatures(self, userid):
        userdocument = tm_content.getUserAnswers(userid)
        user_features = self.getDocumentFeatures(userdocument)
        return user_features

    def findSimilarDocs(self, document):
        document_model = self.getDocumentFeatures(document)
        sims = self.index[document_model]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        return sims

    def createUserCorpus(self, userfile=config.USERS):
        usercorpus = []
        for User in Users.select():
            user_features = self.getUserFeatures(User.id)
            if(user_features!=None):
                usercorpus.append(user_features)
        corpora.MmCorpus.serialize(userfile, usercorpus)
