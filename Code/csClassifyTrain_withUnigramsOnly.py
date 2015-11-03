import os
import traceback
import re


import nltk
import nltk.classify.util
from nltk.corpus import stopwords
from nltk.classify import NaiveBayesClassifier

#To filter out common english words
from nltk.corpus import stopwords

#To save and load the classifier
import pickle

from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()
	

list_common_cs = ['comput', 'problem', 'system', 'softwar', 'non','servic', 'comput', 'analysi', 'data', 'algorithm', 'approach', 'method', 'reliabl', 'alloc', 'qualiti']
commonCompScienceWords = set(list_common_cs)	

stopset = []
for word in stopwords.words('english'):
	stopset.append(ps.stem(word))
stopset = set(stopset)

	
	
commonCompScienceWords = set()
#To get dict of words present in the document
def get_bag_of_words(words):
	return dict( [ (word, True) for word in words if word not in stopset if word not in commonCompScienceWords] )	#EDIT 2
  
def get_Bigrams(w):
	bi = []
	
	#EDIT 3
	w = list(set(w)-stopset)
	w = list(set(w)-commonCompScienceWords)
	
	for i in nltk.bigrams(w):
		bi.append((''.join(i)))
	return bi
	
ml_feats = []
ai_feats = []	
nlp_feats = []
cloud_feats = []  
grid_feats = []
expertSystems_feats = []
networks_feats = []
threed_feats = []
hpc_feats = [] 
secur_feats = []
simul_feats = []
data_feats = []
wsn_feats = []
km_feats = []

def getTextFromFile(tfile):
	f = open(tfile,"r")
	s = f.read()
	#s = s.decode("utf-8")
	s = s.lower()
	#s = re.sub('[\d]|,|\.|:|-' , ' ',s)
	s = re.sub('[\W]+',' ',s)
	s = s.split()
	s = stemText(s)
	return s
	

def stemText(s):
	ps = PorterStemmer()
	stemmedText = []
	for word in s:
		stemmedText.append(ps.stem(word))
		
	return stemmedText
	
	

		
for tfile in os.listdir('.'):
	if tfile[-18:]=='EXPERT_SYSTEMS.txt':
		try:
			s = getTextFromFile(tfile)
			expertSystems_bag = get_bag_of_words(s)
			expertSystems_feats.append((expertSystems_bag, 'EXPERT_SYSTEMS'))

		except:
			print traceback.format_exc()
	
	elif tfile[-12:]=='NETWORKS.txt':
		try:
			s = getTextFromFile(tfile)
			networks_bag = get_bag_of_words(s)
			networks_feats.append((networks_bag , 'NETWORKS'))

		except:
			print traceback.format_exc()
			
	elif tfile[-15:]=='SIMULATIONS.txt':
		try:
			s = getTextFromFile(tfile)			
			simul_bag = get_bag_of_words(s)
			simul_feats.append((simul_bag, 'SIMULATIONS'))
		except:
			print traceback.format_exc()	

	elif tfile[-7:]=='HPC.txt':
		try:
			s = getTextFromFile(tfile)
			hpc_bag = get_bag_of_words(s)
			hpc_feats.append((hpc_bag, 'HPC'))

		except:
			print traceback.format_exc()

	elif tfile[-12:]=='SECURITY.txt':
		try:
			s = getTextFromFile(tfile)
			secur_bag = get_bag_of_words(s)
			secur_feats.append((secur_bag , 'SECURITY'))
		except:
			print traceback.format_exc()
			
	elif tfile[-18:]=='DATAMANAGEMENT.txt':
		try:
			s = getTextFromFile(tfile)
			data_bag = get_bag_of_words(s)
			data_feats.append((data_bag , 'DATAMANAGEMENT'))
		except:
			print traceback.format_exc()
		
	elif tfile[-7:]=='WSN.txt':
		try:
			s = getTextFromFile(tfile)
			wsn_bag = get_bag_of_words(s)
			wsn_feats.append((wsn_bag , 'WSN'))
		except:
			print traceback.format_exc()
			
	elif tfile[-6:]=='KM.txt':
		try:
			s = getTextFromFile(tfile)
			km_bag = get_bag_of_words(s)
			km_feats.append((km_bag , 'KNOWLEDGE_MANAGEMENT'))
		except:
			print traceback.format_exc()
	
	else:
		pass

expertSystems_len = len(expertSystems_feats)*5/6
networks_len = len(networks_feats)*5/6
threed_len = len(threed_feats)*5/6
cloud_len = len(cloud_feats)*5/6
grid_len = len(grid_feats)*5/6
hpc_len = len(hpc_feats)*5/6
data_len = len(data_feats)*5/6
secur_len = len(secur_feats)*5/6
simul_len = len(simul_feats)*5/6
wsn_len = len(wsn_feats)*5/6
km_len = len(km_feats)*5/6

trainingset = expertSystems_feats[:expertSystems_len] + networks_feats[:networks_len] + hpc_feats[:hpc_len] + secur_feats[:secur_len] + simul_feats[:simul_len] + data_feats[:data_len] + wsn_feats[:wsn_len] + km_feats[:km_len]
testset  = expertSystems_feats[expertSystems_len:] + networks_feats[networks_len:]   + hpc_feats[hpc_len:]  + secur_feats[secur_len:] + simul_feats[simul_len:] + data_feats[data_len:] + wsn_feats[wsn_len:] + km_feats[km_len:]


print "\n\nTraining the ComputerScience Document classifier using a Naive Bayes Classifier..."
classifier = NaiveBayesClassifier.train(trainingset)

print '\n\nAccuracy of the ComputerScience Document classifier: ', nltk.classify.util.accuracy(classifier,testset)*100, "%"

print "\n\nSaving the current classifier for future usage...\n\n "

f = open('cs_classifier.pickle','wb')
pickle.dump(classifier,f)
f.close()

