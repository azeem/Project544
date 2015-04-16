from nltk import ChunkParserI, TrigramTagger
from nltk.chunk import tree2conlltags, conlltags2tree

class SimpleChunkParser(ChunkParserI):
    def __init__(self, trainingChunkedSents):
        trainingData = [
            [(posTag, bioTag) for word, posTag, bioTag in tree2conlltags(chunkedSent)]
            for chunkedSent in trainingChunkedSents 
        ]
        self.tagger = TrigramTagger(trainingData)

    def parse(self, sent):
        posTags = [posTag for (word, posTag) in sent]
        bioTags = [bioTag for (posTag, bioTag) in self.tagger.tag(posTags)]
        chunkedSent = [(word, posTag, bioTag) for ((word, posTag), bioTag) in zip(sent, bioTags)]
        return conlltags2tree(chunkedSent)
