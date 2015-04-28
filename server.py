import pickle 

from flask import Flask
from flask import request
from flask import jsonify

from project544.predictors.classifier_user_prediction import ClassifierUserPredictor
from project544.predictors.topicmodel_prediction import TopicModelPredictor
from project544.topicmodelling.tm import QuestionTopicModel
from project544.tag_feature_gen import TagFeatureGen
from project544 import config
from project544.topicmodelling.tm import TopicModel

app =  Flask(__name__)
# cfPredictor = None
# cfPredictorTg = None
# tmPredictor = None
qTm = None
# tm = None
# tg = None
predictor = None
fgen = None

def jsonifyUser(user):
    return {
        "id": user.id,
        "accountid": user.accountid,
        "displayname": user.displayname,
        "reputation": user.reputation,
        "upvotes": user.upvotes,
        "downvotes": user.downvotes,
        "profileimageurl": user.profileimageurl,
        "emailhash": user.emailhash
    }


@app.route("/predictUsers", methods=["POST"])
def predictUsers():
    # predictor, fgen = getPredictorFGen(request.form.get("method"))
    document = request.form["document"]
    tags = request.form.get("tags", None)
    tags = [] if tags is None or tags.strip() == "" else tags.split(",")
    n = int(request.form.get("n", 5))
    users = predictor.predictUsers(document, tags, fgen, n)
    users = [jsonifyUser(user) for user in users]
    return jsonify(users = users)

@app.route("/predictUserScore", methods=["POST"])
def predictUserScore():
    # predictor, fgen = getPredictorFGen(request.form.get("method"))
    document = request.form["document"]
    tags = request.form.get("tags", None)
    tags = [] if tags is None or tags.strip() == "" else tags.split(",")
    userIds = [int(userId) for userId in request.form.get("userids", None).split(",")]
    scores = predictor.predictUserScore(document, tags, fgen, userIds)
    return jsonify(scores = dict(zip(userIds, scores)))

@app.route("/findSimilarQuestions", methods=["POST"])
def findSimilarQuestions():
    document = request.form["document"]
    simQuestions = qTm.findSimilarQuestions(document)
    return jsonify(questions = simQuestions)

if __name__ == "__main__":

    fgen = TopicModel()
    file = open(config.USER_PREDICTOR_TM, "r")
    predictor = pickle.load(file)
    file.close()

    # fgen = TagFeatureGen()
    # file = open(config.USER_PREDICTOR_TG, "r")
    # predictor = pickle.load(file)
    # file.close()

    qTm = QuestionTopicModel()
    app.run(debug=True)
