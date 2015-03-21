#!/usr/vimsical-ac/vac-env/bin/bash/env python
"""
initial test script to generate possible topics for autocorrect functionality of vimsical text editor
"""

def parseTextXML(filepath, n_sample=200):
	from xml.dom import minidom
	from nltk.corpus import stopwords
	from random import sample
	stop = stopwords.words('english')
	xmldoc = minidom.parse(filepath)
	itemlist = xmldoc.getElementsByTagName('TEXT')
	#corpus = {i : 0 for i in range(len(itemlist))}
	corpus = []
	for s in itemlist:
		corpus_insert = s.childNodes[0].nodeValue.lower()
	        corpus_insert = [word for word in corpus_insert.split() if word not in stop]
		corpus_insert = " ".join(corpus_insert)
		corpus_insert = corpus_insert.split('.')
		for sentence in corpus_insert:
			corpus.append(sentence)
	corp = {k: v for k, v in enumerate(sample(corpus, n_sample))}
	return corp

def writeTDM(corpus, outfile):
	import textmining
	tdm = textmining.TermDocumentMatrix()
	for i in range(len(corpus)):
		tdm.add_doc(corpus[i])
	tdm.write_csv(outfile)

def highMagnitudeFeatures(components, columns):
	import numpy as np
	iter_list = []
	for i in range(len(components)):
		norm_component = components[i] / sum(components[i])
		argsorted_components = np.argsort(norm_component)[::-1]
		cumsum_components = np.cumsum(norm_component[argsorted_components]) > 0.90
		if sum(np.logical_not(cumsum_components)) > 0:
			top_n_features = argsorted_components[0:np.where(cumsum_components)[0][0]]
		else:
			top_n_features = np.array([argsorted_components[0]])
		top_n_features = top_n_features.tolist()
		iter_list.extend(top_n_features)
	feature_counts = np.bincount(iter_list)
	cutoff = np.floor(np.mean(feature_counts) + np.std(feature_counts))
	drop_cols = columns[np.where(feature_counts > cutoff)]
	return drop_cols

def dropTrivialColumns(indata, column_names, drop_cols):
	import numpy as np
	idx = [int(np.where(column_names == drop_cols[i])[0]) for i in range(len(drop_cols))]
	idx_mask = np.ones((1, indata.shape[1]))
	idx_mask[:, idx] = 0
	idx_mask = idx_mask.astype(bool)
	indata = indata[:, idx_mask[0]]
	column_names = column_names[idx_mask[0]]
	return indata, column_names

def loadAndProcessTDM(infile, drop_common_words=False, drop_cols=False, components=False):
	from numpy import genfromtxt
	import numpy as np
	from sklearn.preprocessing import normalize
	indata = genfromtxt(infile,
			    delimiter=',',
			    skip_header=1)
	words = genfromtxt(infile,
			   dtype=str,
			   delimiter=',',
			   skip_footer=len(indata))
	if drop_common_words:
		argsorted_colsums = indata.astype(bool).sum(axis=0).argsort()[::-1]
		n_percent = int(round(len(argsorted_colsums)*drop_common_words))
		drop_idx = argsorted_colsums[:n_percent]
		indata = np.delete(indata, drop_idx.tolist(), 1)
	if drop_cols:
		drop_cols = highMagnitudeFeatures(components, words)
		indata, words = dropTrivialColumns(indata, words, drop_cols)
	indata = normalize(indata.astype(float))
	return indata, words

def matrixFactorization(inmatrix, p_components=False):
	from sklearn.decomposition import PCA
	from sklearn.decomposition import ProjectedGradientNMF
	import pdb
	if p_components:
		p_comp = p_components
	else:
		pca = PCA(n_components=inmatrix.shape[1])
		pca.fit(inmatrix)
		explained_variance = pca.explained_variance_ratio_.cumsum()
		explained_variance = explained_variance[explained_variance <= .9]
		p_comp = len(explained_variance)
	model = ProjectedGradientNMF(n_components=p_comp,
				     init='nndsvd',
				     beta=1,
				     sparseness=None)
	#pdb.set_trace()
	model.fit(inmatrix)
	return model

if __name__ == "__main__":
	import pdb
	from sklearn.externals import joblib
	corpus = parseTextXML('/Users/zpuste/vimsical-ac/data/ap.xml',
			n_sample=5000)
	writeTDM(corpus, outfile='/Users/zpuste/vimsical-ac/data/ap-tdm-1.csv')
	dat, words = loadAndProcessTDM('/Users/zpuste/vimsical-ac/data/ap-tdm-1.csv')
	nmf = matrixFactorization(dat)
	joblib.dump(nmf, '/Users/zpuste/vimsical-ac/data/nmf-model-1.nmf', compress=0)
	joblib.dump(dat, '/Users/zpuste/vimsical-ac/data/data-matrix-1.np', compress=0)
	joblib.dump(words, '/Users/zpuste/vimsical-ac/data/data-words-1.np', compress=0)
	#pdb.set_trace()
	dat2, words2 = loadAndProcessTDM('/Users/zpuste/vimsical-ac/data/ap-tdm-1.csv',
			drop_cols=True, components = nmf.components_)
	del dat, words, nmf
	nmf2 = matrixFactorization(dat2, p_components=20)
	joblib.dump(nmf2, '/Users/zpuste/vimsical-ac/data/nmf-model-2.nmf', compress=0)
	joblib.dump(dat2, '/Users/zpuste/vimsical-ac/data/data-matrix-2.np', compress=0)
	joblib.dump(words2, '/Users/zpuste/vimsical-ac/data/data-words-2.np', compress=0)
	with open('/Users/zpuste/vimsical-ac/output/topics.txt', 'w') as f:
		for i in range(nmf2.components_.shape[0]):
			f.write(str(i))
			f.write(" ".join(words2[nmf2.components_[i].argsort()[0:9]].tolist()))
			f.write('\n')
	
