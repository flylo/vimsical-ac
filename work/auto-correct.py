import pymongo
import json
import re
import collections
import pdb

class AutoCorrect(object):

  def __init__(self, connect_file, database):

    self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
    self._dbConnect(connect_file, database)
    self._words = self.db.topic_0.distinct("word")

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
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)
  
  def _known_edits2(self, word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in self._words)
  
  def _known(self, words): return set(w for w in words if w in self._words)
  
  def _correct(self, word):
    e1_words = self.known(self._edits1(word))
    e2_words = self._known_edits2(word)

    candidates = known([word]) or e1_words or e2_words or [word]
    # FIX - RETURN MAX USING PYMONGO MAX CURSOR
    return max(candidates, key=NWORDS.get)

  # def correctWord(self, word):


if __name__ == "__main__":
  connect_file='./connect-string.json'
  database='vimsical'
  ac = AutoCorrect(connect_file, database)
  pdb.set_trace()


  ## THESE SHOULD BE IN THE MONGO DB  
  # def words(text): return re.findall('[a-z]+', text.lower()) 
  
  # def train(features):
  #     model = collections.defaultdict(lambda: 1)
  #     for f in features:
  #         model[f] += 1
  #     return model
  
  # NWORDS = train(words(file('big.txt').read()))