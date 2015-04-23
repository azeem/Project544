from sklearn.linear_model import Perceptron
import numpy 
import pickle

import Config
from Gensim import Gensim
from Model import Posts, Users

class UserPredictor(object):
    def __init__(self, classifier=None):
        if classifier is None:
            classifier = Perceptron()
        self.cf = classifier
        
    def learn(self, fgen, fdimSize, postLimit=None):
        query = Posts.select().where(Posts.posttypeid == 2)
        if postLimit is not None:
            query = query.limit(postLimit)
        count = query.count()

        print("Topic modelling Posts")
        X = numpy.zeros((count, fdimSize))
        Y = numpy.zeros((count,))
        for i, answer in enumerate(query):
            if answer.owneruserid is None:
                continue
            print("Generating feature vector for id {0}".format(answer.id))
            qa = answer.parentid.body + answer.body
            feature = fgen.GetDocumentModel(qa, modelfile=Config.ANSWER_MODEL)
            for topic, value in feature:
                X[i][topic] = value
            Y[i] = answer.owneruserid.id

        print("Learning Model")
        self.cf.fit(X, Y)
        self.useridIndex = Y

    def predictUsers(self, body, fgen, fdimSize, n = 3):
        X = numpy.zeros((1, fdimSize))
        feature = fgen.GetDocumentModel(body, modelfile=Config.ANSWER_MODEL)
        for topic, value in feature:
            X[0][topic] = value
        userIds = [int(self.useridIndex[index]) for index, score in sorted(enumerate(self.cf.decision_function(X)[0]), key=lambda x:x[1])][:n]
        return Users.select().where(Users.id << userIds)

def testLearn():
    gensim = Gensim()
    up = UserPredictor()
    up.learn(gensim, Config.num_topics_lda)
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


if __name__ == "__main__":
    testLearn()
    # testPredict()
