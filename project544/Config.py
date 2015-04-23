import path
import os

MALLET_PATH         = path.join(os.getenv("MALLET_HOME"), "bin/mallet")
DATABASE_FILENAME   = "./data/so-dump.db"
STOPLIST            = "./data/stoplist"
DICTIONARY          = "./out/posts.dict"
QUESTIONS           = "./out/questions.mm"
QUESTION_LIST       = "./out/question.list"
QUESTION_MODEL      = "./out/questions.lda"
QUESTION_INDEX      = "./out/questions.index"
ANSWERS             = "./out/answers.mm"
ANSWER_LIST         = "./out/answer.list"
ANSWER_MODEL        = "./out/answers.lda"
ANSWER_INDEX        = "./out/answers.index"
USER_PREDICTOR      = "./out/userpredictor.mm"
TOPICMODEL_METHOD   = "lda_mallet"
NUM_TOPICS_LDA      = 100
