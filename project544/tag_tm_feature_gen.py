from project544.base import FeatureGeneratorBase
from project544.topicmodelling.tm import TopicModel
from project544.tag_feature_gen import TagFeatureGen

class TagTMFeatureGen(FeatureGeneratorBase):
    def __init__(self):
        self.tm = TopicModel()
        self.tg = TagFeatureGen()

    def getAnswerFeatures(self, answer):
        print("Combining features for answer {0}".format(answer.id))
        tmFeatures = self.tm.getAnswerFeatures(answer)
        tgFeatures = [(key+10+self.tm.getMaxDimSize(), value) for key, value in self.tg.getAnswerFeatures(answer)]
        return tmFeatures + tgFeatures

    def getDocumentFeatures(self, document, tags):
        print("Combining features for document")
        tmFeatures = self.tm.getDocumentFeatures(answer, tags)
        tgFeatures = [(key+10+self.tm.getMaxDimSize(), value) for key, value in self.tg.getDocumentFeatures(answer, tags)]
        return tmFeatures + tgFeatures

    def getMaxDimSize(self):
        return (self.tm.getMaxDimSize() + self.tg.getMaxDimSize())

