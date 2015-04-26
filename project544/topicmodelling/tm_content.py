import pickle
from ..model import Posts
from .. import config
import tm_util

def getQuestions(savetofile=False):
    questionlist = []
    questions = []

    for Post in Posts.select().where(Posts.posttypeid==1):
        post = Post.title + ' ' + Post.body
        postcontent = tm_util.preprocessPost(post)
        questionlist.append(postcontent)
        questions.append(Post.title)

    if(savetofile):
        with open(config.QUESTION_LIST, 'w') as fout:
            pickle.dump(questions, fout)

    return questionlist

def getAnswers():
    answerlist = []

    for Post in Posts.select().where(Posts.posttypeid==2):
        postcontent = tm_util.preprocessPost(Post.body)
        answerlist.append(postcontent)

    return answerlist

def getPosts():
    questions = getQuestions()
    answers = getAnswers()
    combinedlist = questions + answers

    return combinedlist


def getUserAnswers(userid):
    aggregate = ''

    for Post in Posts.select().where((Posts.owneruserid==userid) & (Posts.posttypeid==2)):
        aggregate = aggregate + ' ' + Post.body

    return aggregate
