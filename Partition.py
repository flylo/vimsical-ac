"""
script to break out an xml document into a training and testing set
process:
	training / testing XML docs
	build LDA model on training
	build language model on training
	write SentenceTest() class that takes in a sentence (from XML or Mongo) and
	  extracts the last word, stores the correct spelling, turns it into a 
	  misspelling (edit dist of 1) and attempts to autocorrect
"""

import lxml
from lxml import etree
from random import sample
import pdb
#import transducer

class CreateTrainTest(object):
	"""
	partition an XML doc out into training and testing sets
	"""
	def __init__(self, xml_path, train_size=0.8,
				 out_train='./train.xml', out_test = './test.xml'):
		self.xml_path = xml_path
		self.train_size = train_size
		self.out_train = out_train
		self.out_test = out_test

	def _parseDocument(self, train_vec):
		"""
		parse the XML document subject to integer index constraints in a vector
		FIX - this is a memory hog
		"""
		self.parser = etree.iterparse(self.xml_path, recover=True, tag="TEXT")
		inc = 0

		root_train = etree.Element("root")
		root_test = etree.Element("root")

		for event, element in self.parser:
			if inc in train_vec:
				doc = etree.SubElement(root_train, "TEXT")
				doc.text = element.text
			else:
				doc = etree.SubElement(root_test, "TEXT")
				doc.text = element.text
			inc += 1

		train_corpus = etree.ElementTree(root_train)
		test_corpus = etree.ElementTree(root_test)

		train_corpus.write(self.out_train)
		test_corpus.write(self.out_test)

	def _partitionDocument(self):
		"""blah"""
		#with open(self.xml_path, 'rb') as in_xml:
		
		self.parser = etree.iterparse(self.xml_path, recover=True, tag="TEXT")
		num_nodes = 0
		for event, element in self.parser:
			num_nodes += 1

		# partitioning vectors
		test_size = int(round((1 - self.train_size) * num_nodes))
		test_vec = sample(range(num_nodes), test_size)
		train_vec = [i for i in range(num_nodes) if i not in test_vec]

		self._parseDocument(train_vec)

	def partition(self):
		self._partitionDocument()

if __name__ == "__main__":
	traintest = CreateTrainTest(xml_path='./data/ap.xml',
								out_train='./data/train.xml',
								out_test='./data/test.xml')
	traintest.partition()