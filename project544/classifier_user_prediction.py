from sklearn.linear_model import Perceptron
import numpy 
import pickle

import config
from base import UserPredictorBase
from topicmodelling.gsim import Gensim
from model import Posts, Users

class ClassifierUserPredictor(UserPredictorBase):
    def __init__(self, classifier=None, batchSize=1000):
        if classifier is None:
            classifier = Perceptron()
        self.cf = classifier
        self.batchSize = 1000
        
    def learn(self, fgen, postLimit=None):
        query = Posts.select().where(Posts.posttypeid == 2)
        if postLimit is not None:
            query = query.limit(postLimit)
        count = query.count()

        allClasses = numpy.array(user.id for user in Users.select())

        featureMatrix = []
        classList = []
        for i, answer in enumerate(query):
            if answer.owneruserid is None:
                continue
            print("Generating feature vector for id {0}".format(answer.id))
            qa = answer.parentid.body + answer.body
            feature = fgen.GetDocumentModel(qa, config.ANSWER_MODEL)
            # featureVector = fgen.GetDocumentFeatures(qa)
            featureMatrix.append([tup[1] for tup in sorted(featureVector, key=lambda x:x[0])])
            classList.append(answer.owneruserid.id)
            if len(featureMatrix) == self.batchSize:
                print("Partial fitting classifier".format(answer.id))
                X = numpy.array(featureMatrix)
                Y = numpy.array(classList)
                self.cf.partial_fit(X, Y, classes=allClasses)
                allClasses = None
                featureMatrix = []
                classList = []

    def predictUsers(self, body, tags, fgen, n = 3):
        featureVector = fgen.GetDocumentModel(body, config.ANSWER_MODEL)
        # featureVector = fgen.GetDocumentFeatures(body)
        X = numpy.array([[tup[1] for tup in sorted(featureVector, key=lambda x:x[0])]])
        userIds = [int(self.cf.classes_[index]) for index, score in sorted(enumerate(self.cf.decision_function(X)[0]), key=lambda x:x[1])][:n]
        return Users.select().where(Users.id << userIds)

    def predictUserScore(self, body, tags, fgen, users):
        featureVector = fgen.GetDocumentFeatures(body)
        X = numpy.array([[tup[1] for tup in sorted(featureVector, key=lambda x:x[0])]])
        scores = [score for index, score in enumerate(self.cf.decision_function(X)[0]) if int(self.cf.classes_[index]) in users]
        return scores

def testLearn():
    gensim = Gensim()
    up = ClassifierUserPredictor()
    up.learn(gensim)
    file = open(Config.USER_PREDICTOR, "w")
    pickle.dump(up, file)

def testPredict():
    file = open(Config.USER_PREDICTOR, "r")
    up = pickle.load(file)
    file.close()
    gensim = Gensim()

    query = Posts.select().where((Posts.posttypeid == 1) & (Posts.id > 3000)).limit(5)
    for question in query:
        users = up.predictUsers(question.body, gensim, Config.num_topics_lda)
        print([user.displayname for user in users])

    query = Posts.select().where((Posts.posttypeid == 1) & (Posts.id > 3000)).limit(5)
    for question in query:
        users = Posts.select().where(Posts.parentid == question.id).owneruserid
        userIds = [user.id for user in users]
        scores = up.predictUserScore(question.body, gensim, Config.num_topics_lda)
        print("\n".join("{0}({1})".format(user.displayname, score) for user, score in zip(users)))
