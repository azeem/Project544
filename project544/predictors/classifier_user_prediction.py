from sklearn.linear_model import Perceptron
import numpy
import pickle

from .. import config
from ..base import UserPredictorBase
from ..model import Posts, Users

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

        allClasses = numpy.array([user.id for user in Users.select()])

        featureMatrix = []
        classList = []
        for i, answer in enumerate(query):
            if answer.owneruserid is None:
                continue
            print("Generating feature vector for id {0}".format(answer.id))
            qa = answer.parentid.body + answer.body
            # feature = fgen.GetDocumentModel(qa, config.ANSWER_MODEL)
            featureVector = fgen.getDocumentFeatures(qa)
            featureMatrix.append([tup[1] for tup in sorted(featureVector, key=lambda x:x[0])])
            classList.append(answer.owneruserid.id)
            if len(featureMatrix) == self.batchSize or i == count-1:
                print("Partial fitting classifier".format(answer.id))
                X = numpy.array(featureMatrix)
                Y = numpy.array(classList)
                self.cf.partial_fit(X, Y, classes=allClasses)
                featureMatrix = []
                classList = []

    def predictUsers(self, body, tags, fgen, n = 3):
        # featureVector = fgen.GetDocumentModel(body, config.ANSWER_MODEL)
        featureVector = fgen.getDocumentFeatures(body)
        X = numpy.array([[tup[1] for tup in sorted(featureVector, key=lambda x:x[0])]])
        userIds = [int(self.cf.classes_[index]) for index, score in sorted(enumerate(self.cf.decision_function(X)[0]), key=lambda x:x[1])][:n]
        return Users.select().where(Users.id << userIds)

    def predictUserScore(self, body, tags, fgen, users):
        featureVector = fgen.getDocumentFeatures(body)
        X = numpy.array([[tup[1] for tup in sorted(featureVector, key=lambda x:x[0])]])
        scores = [score for index, score in enumerate(self.cf.decision_function(X)[0]) if int(self.cf.classes_[index]) in users]
        return scores

def testLearn():
    from project544.topicmodelling.tm import TopicModel
    tm = TopicModel()
    up = ClassifierUserPredictor()
    up.learn(tm, postLimit=10)
    file = open(config.USER_PREDICTOR, "w")
    pickle.dump(up, file)

def testPredict():
    file = open(config.USER_PREDICTOR, "r")
    up = pickle.load(file)
    file.close()
    from project544.topicmodelling.tm import TopicModel
    tm = TopicModel()

    query = Posts.select().where((Posts.posttypeid == 1) & (Posts.id > 3000)).limit(5)
    for question in query:
        users = up.predictUsers(question.body, None, tm)
        print([user.displayname for user in users])

    query = Posts.select().where((Posts.posttypeid == 1) & (Posts.id > 3000)).limit(5)
    for question in query:
        users = [answer.owneruserid for answer in Posts.select().where(Posts.parentid == question.id)]
        userIds = [user.id for user in users]
        scores = up.predictUserScore(question.body, None, tm, userIds)
        print("\n".join("{0}({1})".format(user.displayname, score) for user, score in zip(users, scores)))

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Invalid arguments")
    else:
        if sys.argv[1] == "learn":
            testLearn()
        else:
            testPredict()

