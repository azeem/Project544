import pickle 

from flask import Flask
from flask import request
from flask import jsonify

from project544.predictors.classifier_user_prediction import ClassifierUserPredictor
from project544.predictors.topicmodel_prediction import TopicModelPredictor
from project544.topicmodelling.tm import QuestionTopicModel
from project544 import config
from project544.topicmodelling.tm import TopicModel

app =  Flask(__name__)
cfPredictor = None
tmPredictor = None
qTm = None
tm = None

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
    method = request.form.get("method", "classifier")
    document = request.form["document"]
    tags = request.form.get("tags", None)
    if tags is None:
        tags = []
    else:
        tags = tags.split(",")
    n = int(request.form.get("n", 5))
    users = cfPredictor.predictUsers(document, tags, tm, n)
    users = [jsonifyUser(user) for user in users]
    return jsonify(users = users)

@app.route("/predictUserScore", methods=["POST"])
def predictUserScore():
    document = request.form["document"]
    tags = request.form.get("tags", None).split(",")
    if tags is None:
        tags = []
    userIds = [int(userId) for userId in request.form.get("userids", None).split(",")]
    scores = cfPredictor.predictUserScore(document, tags, tm, userIds)
    return jsonify(scores = dict(zip(userIds, scores)))

@app.route("/findSimilarQuestions", methods=["POST"])
def findSimilarQuestions():
    document = request.form["document"]
    simQuestions = qTm.findSimilarQuestions(document)
    return jsonify(questions = simQuestions)

if __name__ == "__main__":
    tm = TopicModel()
    file = open(config.USER_PREDICTOR, "r")
    cfPredictor = pickle.load(file)
    file.close()
    qTm = QuestionTopicModel()
    app.run(debug=True)
