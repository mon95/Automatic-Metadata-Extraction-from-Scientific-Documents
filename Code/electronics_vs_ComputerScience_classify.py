import os
import traceback
import re

import nltk
import nltk.classify.util
from nltk.corpus import stopwords


from nltk.classify import NaiveBayesClassifier


#To save and load the classifier
import pickle


#To get dict of words present in the document
def get_bag_of_words(words):
	return dict( [ (word, True) for word in words ] )
  
electronic_feats = []  
cs_feats = []

#get Electronic pdfs	
for tfile in os.listdir('.'):
	if tfile[-10:]=='OUTPUT.txt' :
		try:
			f = open(tfile,"r")
			s = f.read()
			s = re.sub('[\d]|,|\.' , ' ',s)
			s = s.split()
			electronic_bag = get_bag_of_words(s)
			electronic_feats.append((electronic_bag, 'Electronics'))
		except:
			print traceback.format_exc()
	
	elif tfile[-3:]=='txt':
		try:
			f = open(tfile,"r")
			s = f.read()
			s = re.sub('[\d]|,|\.' , ' ',s)
			s = s.split()
			cs_bag = get_bag_of_words(s)
			cs_feats.append((cs_bag, 'ComputerScience'))
		except:
			print traceback.format_exc()
			
	else:
		pass
		

elec_len = len(electronic_feats)*3/4
cs_len = len(cs_feats)*3/4

trainingset = electronic_feats[:elec_len] + cs_feats[:cs_len]
testset  = electronic_feats[elec_len:] + cs_feats[cs_len:]


print "\n\nTraining the ELECTRONICS vs ComputerScience Document classifier using a Naive Bayes Classifier..."
classifier = NaiveBayesClassifier.train(trainingset)
print '\n\nAccuracy of the ELECTRONICS vs ComputerScience Document classifier: ', nltk.classify.util.accuracy(classifier,testset)*100, "%"

print "\n\nSaving the current classifier for future usage...\n\n "
f = open('electronics_and cs_classifier.pickle','wb')
pickle.dump(classifier,f)
f.close()

