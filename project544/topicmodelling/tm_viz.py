import os
from tm import TopicModel
from .. import config
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class TopicModelViz:

    def __init__(self, modelfile=config.CURRENT_MODEL):
        self.topicmodel = TopicModel()

        self.terms = []
        for i in range(config.NUM_TOPICS_LDA):
            temp = self.topicmodel.model.show_topic(i, 50)
            terms = []
            for term in temp:
                terms.append(term)
            self.terms.append(terms)

    def terms_to_wordcounts(self, terms, multiplier=1000):
        return " ".join([" ".join(int(multiplier*i[0]) * [i[1]]) for i in terms])

    def genWordCloud(self, index):
        wordcloud = WordCloud().generate(self.terms_to_wordcounts(self.terms[index]))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig(os.path.join(config.VISUALIZATION_FOLDER,"wordcloud_"+str(index)))
        plt.close()

    def genWordClouds(self):
        for i in range(config.NUM_TOPICS_LDA):
            self.genWordCloud(i)

    def genTopicProportion(self, question):
        topic_prop = self.topicmodel.getDocumentFeatures(question)
        plt.scatter(*zip(*topic_prop))
        plt.savefig(os.path.join(config.VISUALIZATION_FOLDER,"doc_scatterplot"))
        plt.close()

    def genUserTopicProportion(self, userid):
        topic_prop = self.topicmodel.getUserFeatures(userid)
        plt.scatter(*zip(*topic_prop))
        plt.savefig(os.path.join(config.VISUALIZATION_FOLDER,"user" + str(userid) + "_scatterplot"))
        plt.close()
