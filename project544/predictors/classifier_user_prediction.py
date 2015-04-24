from sklearn.linear_model import Perceptron
from sklearn.feature_extraction import FeatureHasher
import numpy
import pickle
import peewee

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

        featureHasher = FeatureHasher(n_features = fgen.getMaxDimSize()+2, input_type = 'pair')
        featureMatrix = []
        classList = []
        for i, answer in enumerate(query):
            if answer.owneruserid is None:
                continue
            print("Generating feature vector for id {0}".format(answer.id))
            # docment features
            featureVector = fgen.getDocumentFeatures(answer.parentid.title + answer.parentid.body + answer.body)
            featureVector = [(str(dim), value) for dim, value in featureVector]
            # additional features
            maxScore = Posts.select(peewee.fn.Max(Posts.score)).where(Posts.parentid == answer.parentid).scalar()
            featureVector.append(("Score", 1 if maxScore == 0 else (answer.score/float(maxScore))))
            featureVector.append(("Accepted", 1 if answer.id == answer.parentid.acceptedanswerid else 0))
            featureMatrix.append(featureVector)
            classList.append(answer.owneruserid.id)
            if len(featureMatrix) == self.batchSize or i == count-1:
                print("Partial fitting classifier".format(answer.id))
                X = featureHasher.transform(featureMatrix)
                Y = numpy.array(classList)
                self.cf.partial_fit(X, Y, classes=allClasses)
                allClasses = None
                featureMatrix = []
                classList = []

    def predictUsers(self, body, tags, fgen, n = 3):
        featureHasher = FeatureHasher(n_features = fgen.getMaxDimSize()+2, input_type = 'pair')
        # document features
        featureVector = [(str(dim), value) for dim, value in fgen.getDocumentFeatures(body)]
        # additional features
        featureVector.append(("Score", 1))
        featureVector.append(("Accepted", 1))

        X = featureHasher.transform([[(str(dim), value) for dim, value in featureVector]])
        userIds = [int(self.cf.classes_[index]) for index, score in sorted(enumerate(self.cf.decision_function(X)[0]), key=lambda x:x[1], reverse=True)][:n]
        print(userIds)
        print(self.cf.predict(X))

        return [Users.get(Users.id == userId) for userId in userIds]

    def predictUserScore(self, body, tags, fgen, users):
        featureHasher = FeatureHasher(n_features = fgen.getMaxDimSize()+2, input_type = 'pair')
        # document features
        featureVector = [(str(dim), value) for dim, value in fgen.getDocumentFeatures(body)]
        # additional features
        featureVector.append(("Score", 1))
        featureVector.append(("Accepted", 1))

        X = featureHasher.transform([[(str(dim), value) for dim, value in featureVector]])
        scores = [score for index, score in enumerate(self.cf.decision_function(X)[0]) if int(self.cf.classes_[index]) in users]
        return scores

def testLearn():
    from project544.topicmodelling.tm import TopicModel
    tm = TopicModel()
    up = ClassifierUserPredictor()
    up.learn(tm)
    file = open(config.USER_PREDICTOR, "w")
    pickle.dump(up, file)

def testPredict():
    from project544.util import stripTags

    file = open(config.USER_PREDICTOR, "r")
    up = pickle.load(file)
    file.close()
    from project544.topicmodelling.tm import TopicModel
    tm = TopicModel()

    query = Posts.select().where((Posts.posttypeid == 1) & (Posts.id > 3000)).limit(5)
    for question in query:
        users = up.predictUsers(question.body, None, tm, n = 10)
        print("Top predictions for Post {0}".format(question.id))
        print("-------------------------")
        print(stripTags(question.title))
        print("")
        print(stripTags(question.body))
        print("-------------------------")
        print([user.displayname for user in users])
        print("")

    query = Posts.select().where((Posts.posttypeid == 1) & (Posts.id > 3000)).limit(5)
    for question in query:
        users = [answer.owneruserid for answer in Posts.select().where(Posts.parentid == question.id)]
        userIds = [user.id for user in users]
        scores = up.predictUserScore(question.body, None, tm, userIds)
        print("User Scores for Post {0}".format(question.id))
        print("\n".join("{0}({1})".format(user.displayname, score) for user, score in zip(users, scores)))
        print("")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Invalid arguments")
    else:
        if sys.argv[1] == "learn":
            testLearn()
        else:
            testPredict()

