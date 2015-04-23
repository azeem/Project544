import pickle
from ..base import UserPredictorBase
from .. import config
from ..model import Users
from gensim import similarities


class TopicModelPredictor(UserPredictorBase):
    def __init__(self, indexfile=config.USER_INDEX):
        self.index = similarities.MatrixSimilarity.load(indexfile)

    def predictUsers(self, body, tags, fgen, n=3):
        featureVector = fgen.getDocumentFeatures(body)
        sims = self.index[featureVector]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        userlist = pickle.load(config.USERS_LIST)
        userIds= [userlist[sim[0]] for sim in sims[:n]]
        return Users.select().where(Users.id << userIds)
