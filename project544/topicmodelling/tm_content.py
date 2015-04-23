from ..model import Posts
import tm_util

def getQuestions():
    questionlist = []

    for Post in Posts.select().where(Posts.posttypeid==1):
        post = Post.title + ' ' + Post.body
        postcontent = tm_util.preprocessPost(post)
        questionlist.append(postcontent)

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
