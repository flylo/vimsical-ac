import pymongo
import json
import re
import collections
import pdb
import sys
from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel
from numpy import argmax

class AutoCorrect(object):

  def __init__(self, connect_file, database, model_file):
    self._alphabet = 'abcdefghijklmnopqrstuvwxyz'
    self._dbConnect(connect_file, database)
    with open(model_file, 'rb') as mdlf:
      contents = json.load(mdlf)
      model = contents['model-path']
      dictionary = contents['dictionary-path']
    self.model = LdaModel.load(model)
    self.dictionary = Dictionary.load(dictionary)

  def _dbConnect(self, connect_file, database):
    """
    connect to specified MongoDb database
    requires json document of form:
      {"connect-string": "mongodb://<connect-string-here>"}
    """
    with open(connect_file, 'rb') as cnf:
      connection_string = json.load(cnf)['connect-string']

    try:
      connection = pymongo.MongoClient(connection_string)
    except ValueError:
      print "Connection to remote MongoDB client failed"
    
    try:
      self.db = getattr(connection, database)
    except AttributeError:
      print "Specified database not found in MongoDB Client"
  
  def _edits1(self, word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in self._alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in self._alphabet]
    return set(deletes + transposes + replaces + inserts)
  
  def _known_edits2(self, word):
    return set(e2 for e1 in self._edits1(word) for e2 in self._edits1(e1) if e2 in self._words)
  
  def _known(self, words): return set(w for w in words if w in self._words)
  
  def _correct(self):
    e1_words = self._known(self._edits1(self.word))
    e2_words = self._known_edits2(self.word)

    candidates = self._known([self.word]) or e1_words or e2_words or [self.word]
    # FIX - RETURN MAX USING PYMONGO MAX CURSOR
    return max(candidates, key=self._words.get)

  def _topicPredict(self):
    # FIX = MAKE THIS UPDATE THE DICTIONARY OBJECT
    #  THIS CAN BE EITHER ON DISK OR CACHED DEPENDING ON FINAL ARCH
    sentence = self.sentence.split()
    self.word = sentence[len(sentence) - 1]
    sentence = sentence[:len(sentence) - 1]
    bow = self.dictionary.doc2bow(sentence)
    topic_scores = self.model[bow]
    #pdb.set_trace()
    topic = argmax([topic_scores[i][1] for i in range(len(topic_scores))])
    self.topic = 'topic_' + str(topic)

  def _topicInit(self):
    self._topicPredict()
    collection = getattr(self.db, self.topic)
    word_cursor = collection.find()
    word_dict = {word['word'] : word['score'] for word in word_cursor}
    self._words = word_dict

  def topicCorrect(self, sentence):
    self.sentence = sentence
    self._topicInit()
    return self._correct()

  # def correctWord(self, word):


if __name__ == "__main__":
  input_sentence = sys.argv[1]
  connect_file='./connect-string.json'
  database='vimsical'
  model_file = './model-config.json'
  ac = AutoCorrect(connect_file, database, model_file)
  print ac.topicCorrect(input_sentence)
  #ac._topicPredict('hi there')
  #pdb.set_trace()


  ## THESE SHOULD BE IN THE MONGO DB  
  # def words(text): return re.findall('[a-z]+', text.lower()) 
  
  # def train(features):
  #     model = collections.defaultdict(lambda: 1)
  #     for f in features:
  #         model[f] += 1
  #     return model
  
  # NWORDS = train(words(file('big.txt').read()))