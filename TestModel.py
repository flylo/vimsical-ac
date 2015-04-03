"""
load NorvigAutoCorrect.py and AutoCorrect.py
"""
import AutoCorrect
import NorvigAutoCorrect
import lxml
from lxml import etree
from random import sample
import pdb

class ModelTester(object):

	def __init__(self, test_data):
		self.test_data = test_data
		self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
		
	def edits1(self, word):
		splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
		deletes    = [a + b[1:] for a, b in splits if b]
		transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
		replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
		inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
		return set(deletes + transposes + replaces + inserts)
	
	def edits2(self, word):
		return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

	def _genTestSentence(self):
		"""
		Generator to create a test sentence
			replace the last word in a sentence with a random word
			of edit distance max_edit_distance while caching the
			actual word
		"""
		parser = etree.iterparse(self.test_data, recover=True, tag="TEXT")
		
		if self.max_edit_distance == 1:
			newWords = lambda word: self.edits1(word)
		
		elif self.max_edit_distance == 2:
			newWords = lambda word: self.edits2(word)

		else:
			print "Please specify an edit distance in (1, 2)"

		for event, element in parser:
			document = element.text.lower().split('.')
			for sentence in document:
				sentence_split = sentence.split()
				# skipping all 1 word sentences
				if len(sentence_split) <= 1:
					continue
				word = sentence_split[len(sentence_split) - 1]
				new_word = sample(newWords(word), 1)[0]

				# set last word in sentence to the new word
				sentence_split[len(sentence_split) - 1] = new_word
				#pdb.set_trace()
				sentence = ' '.join(sentence_split)
				yield sentence, word, new_word
	
	def testModels(self, max_edit_distance=1):
		"""
		max_edit_distance must be equal to 1 or 2
		FIX - make this method less shitty
		"""
		self.max_edit_distance = max_edit_distance
		acTEST = AutoCorrect.AutoCorrect(connect_file='./connect-string.json',
										 database='vimsical',
										 model_file='./model-config.json')
		acCONTROL =  NorvigAutoCorrect.NorvigAutoCorrect('./data/train.xml')
		
		actualwords = []
		acTESTwords = []
		acCONTROLwords = []
		correctwordsTEST = []
		correctwordsCONTROL = []

		inc = 0
		for sentence, word, new_word in self._genTestSentence():
			
			if inc == 1000:
				break

			actualwords.append(word)

			wordTEST = acTEST.topicCorrect(sentence)
			wordCONTROL = acCONTROL.correct(sentence)
			
			acTESTwords.append(wordTEST)
			acCONTROLwords.append(wordCONTROL)

			correctwordsTEST.append(word == wordTEST)
			correctwordsCONTROL.append(word == wordCONTROL)

			inc += 1


		print "Test Hit Rate:  "
		print float(sum(correctwordsTEST)) / float(len(correctwordsTEST))
		
		print "Control Hit Rate:  "
		print float(sum(correctwordsCONTROL)) / float(len(correctwordsCONTROL))
		#pdb.set_trace()





if __name__ == "__main__":
	
	mt = ModelTester('./data/test.xml')
	mt.testModels(max_edit_distance=1)

	# sentence = 'the german embassy is going to meet with the presdient'
	# connect_file='./connect-string.json'
 #  	database='vimsical'
 #  	model_file = './model-config.json'
	
	# acTEST = AutoCorrect.AutoCorrect(connect_file, database, model_file)
	
	# print acTEST.topicCorrect(sentence)
	
	# acCONTROL =  NorvigAutoCorrect.NorvigAutoCorrect('./data/train.xml')

	# print acCONTROL.correct(sentence)