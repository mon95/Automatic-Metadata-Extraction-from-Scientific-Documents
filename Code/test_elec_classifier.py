import pickle
import os

import traceback
import re

import nltk
import traceback
import re

from nltk.corpus import stopwords



from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()	
stopset = set(stopwords.words('english'))

#stopset = set(stopwords.words('english'))
# list_common_cs = ['computer','problem','systems','software','service','computing','analysis','data','problem','system','algorithm','approach','method','reliability','allocation','quality']
# commonCompScienceWords = set(list_common_cs)		#EDIT 1

 
list_common_cs = ['comput', 'problem', 'system', 'softwar', 'non','servic', 'comput', 'analysi', 'data', 'algorithm', 'approach', 'method', 'reliabl', 'alloc', 'qualiti']
commonCompScienceWords = set(list_common_cs)	

stopset = []
for word in stopwords.words('english'):
	stopset.append(ps.stem(word))
stopset = set(stopset)

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
		
	
def getTextFromFile(tfile):
	f = open(tfile,"r")
	s = f.read()
	#s = s.decode("utf-8	")
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
	
	

def get_bag_of_words1(words):
	return dict( [ (word, True) for word in words ] )
	
	
f = open('electronics_and cs_classifier.pickle')
classifier = pickle.load(f)
f.close()	


for file1 in os.listdir('.'):
	if file1[-8:] == 'TEST.txt':
		try:
			f = open(file1,"r")
			s = f.read()
			s = s.split()
			
			print "Performing Auto Tagging on ", file1[:-4]
			print "..."
			print "..."
			print '\n\n',
			
			
			mainTopic = classifier.classify(get_bag_of_words1(s))
			
			#print classifier.show_most_informative_features(10)
			#print '\n\n'
			
			# dist = classifier.prob_classify(get_bag_of_words1(s))
			# for label in dist.samples():
				# print("%s: %f" % (label, dist.prob(label)))
				
				
			#print "MAIN CATEGORY: ", 
			print mainTopic,">>",
			#print '\n\n'
			
			if mainTopic == 'ComputerScience':
				#print "Now, we tag the document further\n\n"
				f = open('cs_classifier.pickle')
				classifierCS = pickle.load(f)
				f.close()
				
				d = get_bag_of_words(s)
				
				subTopic1 = classifierCS.classify(d)
				
				
				print subTopic1,
				print '\n\n'
				
				# print classifier.show_most_informative_features(30)
				# print '\n\n'
				
				#dist = classifier.prob_classify(get_bag_of_words(s))
				
				dist = classifierCS.prob_classify(get_bag_of_words(d))
								
				for label in dist.samples():
					print("%s: %f" % (label, dist.prob(label)))
				print 
				print s
				#print get_Bigrams(s)
				
				#print "MAIN SUB-CATEGORY: ", 
				# print subTopic1,
				# print '\n\n'
			
			
				
				
				
			else:
				print "Please do tag the document!\n\n"
				
				
			
		except:
			print traceback.format_exc()
			
		