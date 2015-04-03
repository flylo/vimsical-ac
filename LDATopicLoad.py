import lda
import numpy as np
from numpy import genfromtxt
import lxml
from lxml import etree
from nltk.corpus import stopwords
import textmining
from random import sample
import pdb
import gensim
from gensim.models.ldamodel import LdaModel
import pymongo
import json

class CreateDictionary(object):
	"""
	generator to tokenize xml objects
	"""
	def __init__(self, xml_path):
		self.xml_path = xml_path
		self.stopwords = stopwords.words('english')

	def __iter__(self):
		with open(self.xml_path, 'rb') as in_xml:
			corpus = []
			parser = etree.iterparse(in_xml, recover=True, tag="TEXT")
			for event, element in parser:
				# remove stopwords
				corpus_insert = element.text.lower()
				corpus_insert = [word for word in corpus_insert.split()
					if word not in self.stopwords]
				# rejoin and split on sentences
				corpus_insert = " ".join(corpus_insert)
				corpus_insert = corpus_insert.split('.')
				for doc in corpus_insert:
					yield gensim.utils.tokenize(doc, lower=True, errors='ignore')

class CreateCorpus(object):
	"""
	iterable to yield serialized (word_key, count) pairs
	never load corpus into RAM
	"""

	def __init__(self, xml_path):
		print "Generating corpus from XML file..."
		self.xml_path = xml_path
		self.dictionary = gensim.corpora.Dictionary(CreateDictionary(xml_path))

	def __iter__(self):
		for tokens in CreateDictionary(self.xml_path):
			yield self.dictionary.doc2bow(tokens)

class LdaPersistent(object):
	"""
	- save LDA model
	- rank words within topics
	- write ranked words to db
	'object' must be of type CreateCorpus
	"""
	def __init__(self, corpus, num_topics):
		if type(corpus) is not CreateCorpus:
			raise TypeError("Initialization object must be of class CreateCorpus")
		self.corpus = corpus
		self.num_topics = num_topics
		print "Generating LDA Model..."
		self.model = LdaModel(
			self.corpus,
			num_topics=self.num_topics,
			id2word=self.corpus.dictionary)
	
	def saveLda(self, model_file_path, dictionary_file_path):
		"""
		save model object for loading later
		"""
		print "Pickling model object..."
		if model_file_path:
			self.model.save(model_file_path)
		else:
			self.model.save('./lda-model')
		if dictionary_file_path:
			self.corpus.dictionary.save(dictionary_file_path)
		else:
			self.corpus.dictionary.save('./lda-dictionary')

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
		
		# try:
		# 	self.db_collection = getattr(db, collection)
		# except AttributeError:
		# 	print "Specified collection not found in database"

	def _topicCollectionsGen(self):
		"""
		generator function
		warning - this iteratively updates a database connection attribute
		"""
		topn = len(self.corpus.dictionary)
		for topic in xrange(self.num_topics):
			collection_name = 'topic_' + str(topic)
			self._db_collection = getattr(self.db, collection_name)
			for score, word in self.model.show_topic(topicid=topic, topn=topn):
				yield word, score

	def dbInsert(self, connect_file, database):
		"""
		Insert the word and word-score for each topic into MongoDB collection
		Each topic has its own collection that scores each word in the Dictionary
		"""
		print "Loading words and word-ranks into MongoDB..."
		self._dbConnect(connect_file, database)
		for word, score in self._topicCollectionsGen():
			doc = {"word": word, "score": score}
			self._db_collection.insert(doc)
			self._db_collection.create_index("word")
		
		#self.db_collection

	def _wordCollectionsGen(self):
		self._db_collection = getattr(self.db, "word_topic_mappings")
		for word in self.corpus.dictionary.itervalues():
			doc = {}
			doc["word"] = word
			for topic in xrange(self.num_topics):
				collection_name = 'topic_' + str(topic)
				doc[collection_name] = {}
				current_collection = getattr(self.db, collection_name)
				subdoc = {}
				for insert in current_collection.find({"word" : word}):
					subdoc["score"] = insert["score"]
				doc[collection_name] = subdoc
			yield doc

	def dbETL(self):
		print "Loading data into new collection indexed by word..."
		for doc in self._wordCollectionsGen():
			self._db_collection.insert(doc)
		self._db_collection.create_index("word")


if __name__ == '__main__':
	xml_path = './data/train.xml'
	corpus = CreateCorpus(xml_path)
	lda = LdaPersistent(corpus, 20)
	lda.saveLda('./models/lda-model.pkl',
		'./models/lda-dictionary.pkl')
	lda.dbInsert(
		connect_file='./connect-string.json',
		database='vimsical')
	lda.dbETL()
	# pdb.set_trace()



