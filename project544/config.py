import os

MALLET_PATH         = os.path.join(os.getenv("MALLET_HOME"), "bin/mallet")
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
COMBINED            = "./out/combined.mm"
COMBINED_MODEL      = "./out/combined.lda"
COMBINED_INDEX      = "./out/combined.index"
CURRENT_MODEL       = COMBINED_MODEL
CURRENT_INDEX       = COMBINED_INDEX
USERS               = "./out/users.mm"
USERS_LIST           = "./out/users.list"
USER_MODEL          = "./out/users.lsi"
USER_INDEX          = "./out/users.index"
USER_PREDICTOR      = "./out/userpredictor.mm"
TOPICMODEL_METHOD   = "lda_mallet"
NUM_TOPICS_LDA      = 100
