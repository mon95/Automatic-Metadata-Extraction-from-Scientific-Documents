import re
import os
import commands
import sys
import traceback

from subprocess import call


def ExtractTitle(s,rind,i):
	try:
		title = ''
		
		#Find all text with selected font id(rind[i])
		matchTitle = re.findall(r'font='+str(rind[i])+'>(.*?)</',s)
		

		#Extract out title from the match. Avoid appending portions unknowingly coming under Abstract/ Introduction section.
		for i in range(len(matchTitle)):
			if re.search('[I|i]ntroduction|INTRODUCTION|[A|a][B|b][S|s][T|t][R|r][A|a][C|c][T|t]|[K|k][E|e][Y|y][W|w][O|o][R|r][D|d][S|s]', matchTitle[i]) is None:
				title += (matchTitle[i] + ' ')
				
			else:
				break
		
		#Title is highly likely to be wrong if more than 40 words are present or symbols like @ is found
		isCorrect = True
		if len(title.split())>40 or re.search('@' ,title) is not None:		
			isCorrect = False

		#Process the extracted title to give clean output	
		title = re.sub('<(.*?)>','',title)											#Remove html tags
		title = re.sub("(\s|\.)[\d]$",'',title)										#Remove digits that get appended at the end of the title.
		
		
		if len(title)>25 and isCorrect == True:
			return title
            
		else: 
			#If title length is less than 25 characters in length, 
			#It is highly likely that title extraction may have failed.
			#This assumption helps in making an intelligent guess, which helps in extracting text which is more likely to be the title
			return ''
			
	except:
		#When the text with relevant font ids is not found in the part of the file that is being parsed 
		return '' 
		
        
def Extract(s):
	try:
		
		#Remove all double quotes for further regex processing
		#Retain <,> for easy extraction
		s = re.sub('\"','',s)
		
		id =[]
		sz = []

		match = re.findall(r'fontspec id=([0-9]+) size=([0-9]+)', s) 	#findall returns a list of match objects. 0 and 1 indicate groups
		for i in range(len(match)):
			id.append(int(match[i][0]))
			sz.append(int(match[i][1]))	
		
		m = max(sz)
		m1 = max(set(sz)-{m})

		rind = []
		rind2 = []
		for i in range(len(id)):
			if sz[i]==m:
				rind.append(id[i])		#List of max font size ids
			if sz[i]==m1:
				rind2.append(id[i])		#Second list of max font size(2) ids
				
		
		i = 0						#to keep track of the font id index currently used
		j = 0			


		res = ExtractTitle(s,rind,i)    #res has the title or empty string
		
		while res == '':
			
			if i+1 < len(rind):
				i+=1
				res = ExtractTitle(s,rind,i)
				
			else:
				if j < len(rind2):	
					res = ExtractTitle(s,rind2,j)
					j+=1
					
				else:
					break

		if res != '':
			return res
		else:
			print "Title couldn't be extracted. Please enter the title"
			return ''
	except:
		print "Title extraction failed. Please enter the title"
		return ''
		
def extractAuthorPartOfFile(title, sx, s):

	titleWords = title.split()
		
	try:
		matchTE = re.search(titleWords[-1],s)
		s = s[matchTE.start()+len(titleWords[-1]) :]
		matchAbsBeg = re.search('([A|a][B|b][S|s][T|t][R|r][A|a][C|c][T|t])|([A|a]\s?[B|b]\s?[S|s]\s?[T|t]\s?[R|r]\s?[A|a]\s?[C|c]\s?[T|t])|(INTRODUCTION)|([I|i]ntroduction)',s)
		s = s[: matchAbsBeg.start()]
		
	except:
		
		try:
			matchAbsBeg = re.search('([A|a][B|b][S|s][T|t][R|r][A|a][C|c][T|t])|([A|a]\s?[B|b]\s?[S|s]\s?[T|t]\s?[R|r]\s?[A|a]\s?[C|c]\s?[T|t])|(INTRODUCTION)|([I|i]ntroduction)',s)
			s = s[: matchAbsBeg.start()]
			
		except:
			
			try:
				matchOther = re.search('([A-Za-z0-9]@[A-Za-z0-9]\.[A-Za-z0-9])|(a r t i c l e i n f o)|(IGCAR)|(Indira)|(Division)',s)
				s = s[:matchOther.start()]
				
				
			except:
				#print "ExtractFn failed"
				return
		
	slist = s.split('\n')		
	news = ''
	
	try:
		for sent in slist:
			matchCommonWords = re.search('((University)|(Department)|(Group)|(IGCAR)|(Gandhi)|(Indira Gandhi)|(Division)|(Chennai)|(College)|(Engineering)|(Academy)|(Centre)|(Research)|(Corporation)|(Section))',sent)
						
			if matchCommonWords is None:
				news = news + sent
				
			else:
				break
		
		return news 		#authorPartOfFile for final processing
		
	except:
		print "Something went wrong inside the filtering loop!!!"	
		return news

	
def filterIndividualNames(s):
	try:
		s = re.split(',',s)
		return s
	except:
		pass
		
		
def filterUnwantedChars(authorPartOfFile):
	try:
		#Replace and with comma for further filters
		authorPartOfFile = re.sub('\sand\s', ' , ',authorPartOfFile)
		#Filter out unnecessary characters
		authorPartOfFile = re.sub('(\s[a-z]{1,4})|(\*)' , ' ' ,authorPartOfFile)
		#Filter out numbers
		authorPartOfFile = re.sub('\d',' ',authorPartOfFile)
		#Filter out brackets
		authorPartOfFile = re.sub('\(.*\)','',authorPartOfFile)
	except:
		pass
		
	return authorPartOfFile

def printFinalSetOfAuthors(authorPartOfFile):	
	try:
		
		for names in authorPartOfFile: 
			if len(names) > 3 and len(names)<=30:
				names = re.sub('[^A-Za-z\s\.]+', '', names)
				print names	
			
			if len(names) > 30:
			
				#Run through some sort of filter or any other method to get author names embedded in this text
				try:
					matchcaps = re.search('[A-Z]{2,}([A-Z]{1}\.(.*))',names)			#Searching for text following an All-Caps text(mostly title)
					
					try:
						commaPresence = re.search(',', matchcaps.groups(0)[0])
						if commaPresence is not None:
							for n in re.split(',', matchcaps.groups(0)[0]):
								n = re.sub('[^A-Za-z\s\.]+', '', n)
								print n
						else:
							for n in matchcaps.groups(0)[0].split():
								n = re.sub('[^A-Za-z\s\.]+', '', n)
								print n
						continue
					
					except:
						pass
				
				except:
					#print "Inside tough block"
					try:
						matchcaps = re.search('([A-Z][a-z]+\s[A-Z][a-z]+)\s', names)
						print matchcaps.groups()
						
					except:
						print "Author extraction hit a wall. Please rescue with your own efforts"
					
	except:
		pass
			
def keywExtract(s):
	try: 
		matchK = re.search('(Keywords)(.*)|(Index Terms)(.*)|([K|k]ey [W|w]ords)',s)
		
		matchKE = re.search("\n\n",s[matchK.start():])
		
		kwords = s[matchK.start():matchK.start()+matchKE.start()]
		if kwords[0] == 'K':
			kwords = kwords[9:]
		else:
			kwords = kwords[14:]
		
		#Can use this filter only if key words are capitalised phrases.
		#kwords = cleanFirstPart(kwords)
		#Cleaning up kwords
		while re.search('[A-Z|[a-z]',kwords[0]) is None:
			kwords = kwords[1:]

				
		
		return kwords	
		
	except:
		return ''		

def filter1(s):
	s = re.sub('[^A-Za-z&\s]',' ',s)
	return s
	
def filter2(s):
	s = re.sub('Vol(.*)|Volume(.*)',' ',s)
	return s
	
def extractJournal(s):
	try:
		if re.search('elsevier',s) is not None:
			print "ELSEVIER: ", 
			matchE = re.search('\n?(.*)\n(.*)(elsevier)',s,re.MULTILINE)
			#print "Without filter: ",matchE.groups(0)[0]
			jnl = filter1(matchE.groups(0)[0])
			print jnl
			
		else:
			
			try:
				#|(\n?(.*)?([J|j]ournal)(.*)\n\n) ; "Matched inside else blk", 
				matchJ = re.search('(\n?(.*)([J|j]ournal [O|o]f)(.*)\n\n)|(\n?(.*)([J|j]ournal)(.*)\n\n)|(\n?(.*)([J|j]ournal)(.*)\n)', s,re.MULTILINE)
				#print "Without filter: ", s[matchJ.start():matchJ.end()]
				jnl = filter1(s[matchJ.start():matchJ.end()])
				jnl = filter2(jnl)
				
				wordsInJnl = jnl.split()	
				
				if len(wordsInJnl) > 15:		#To check if wrong extraction is done or Extracted from doc's text by mistake
					print "Internal Document" 
				else:
					print jnl
			except:
				print "Internal Document"
				#print(traceback.format_exc())
				
	
	except:
		print "Journal name couldn't be extracted"
		print(traceback.format_exc())

def doiFilter(s):
	try:
		matchDoi = re.search('(:)|(/)',s)
		s = s[matchDoi.end():]
	except:
		print "Unable to apply filter"
	return s
	
	
def extractISSN(s):
	try:
		# matchISSN = re.search('((ISSN)|(ISBN))(.*)\n?',s,re.MULTILINE)
		# print filterISSN(matchISSN.groups(0)[3])

		matchISSN = re.search('(.*)((ISSN)|(ISBN))(.*)\n?',s,re.MULTILINE)
		
		if matchISSN is None:						# Guess possible ISSN/ISBN
			try:
				#print "Guessing possible ISSN/ISBN"
				matchI = re.search('\D([\d]{4}-[\d]{4})\D',s1)		
				if matchI is not None:
						print matchI.group()
			except:
				print "Null"
				
		else:	
			#print matchISSN.groups()				#Extract Correct ISSN/ISBN
			for s1 in matchISSN.groups():
				if s1 is not None:
					matchI = re.search('([\d]{4}-[\d]{4})',s1)
					if matchI is not None:
						print matchI.group()
				else:
					continue
		
	except:
		print "Null"
		#print(traceback.format_exc())
		
def extractDoi(s):
	try:
		#Extract DOI if available
		matchE = re.search('\n?(.*)(doi)(.*)\n?',s,re.MULTILINE)
		
		if matchE is not None:
			print doiFilter(matchE.groups(0)[2])		#Print DOI if found
		
		#Extract ISSN/ISBN if available
		else:
			extractISSN(s)								

	except:
		print "No useful information could be extracted"
		print(traceback.format_exc())
		
		
def filterElsevierStart(abstract):
	slist = abstract.decode('utf-8').split('\n')
	newa = ''
	
	i = 0
	while i < 10:
		try:
			if len(slist[i]) > 50:	#Remove unnecessary info appended with abstract
				newa = newa + slist[i]
				break
		except:
			print "Problem processing elsevier document"
		
		i += 1
	
	swords = newa.split()
	matchRealAbs = re.search(swords[0],abstract)
	abstract = abstract[matchRealAbs.start():] 
	
	return abstract

def finalCleanup(abs):		#To cleanup the final elsevier line that gets appended to the extract
	try:
		matchElsevier = re.search('\n(.*)[E|e]lsevier(.*)\n?',abs,re.MULTILINE)
		#print "INSIDE FINAL CLEANUP: ", matchElsevier.groups()
		#print "ABSTRACT CLEANED UP FINAL: ", abs[:matchElsevier.start()]
		return abs[:matchElsevier.start()]
	except:
		return abs

def cleanFirstPart(s):
	try:
		while re.search('[A-Z]',s[0]) is None:
			s = s[1:]
	except:
		pass
	return s
	
def getAbstract(s):

	#Find the start of abstract section:
	try:

		pattern = re.compile("[A|a][B|b][S|s][T|t][R|r][A|a][C|c][T|t]|[A|a]\s?[B|b]\s?[S|s]\s?[T|t]\s?[R|r]\s?[A|a]\s?[C|c]\s?[T|t]")
		match = pattern.search(s)			#Search returns a match object
		abstract = s[match.start():]
		
	except:
		print "No abstract detected"
		return
		
		
	#Abstract is currently everything till the end of the truncated doc starting from 'Abstract'
	#Find the end of abstract section:
	try:
		pattern1 = re.compile("(Introduction)|(INTRODUCTION)|([K|k]eywords)|([I|i]ndex [T|t]erms)|([K|k]ey []W|w]ords)")
		match1 = pattern1.search(s[match.start():])
		pattern2 = re.compile('\n\n')
		match2 = pattern2.search(s[match.start():])
		if match2.start() < 50:
			abstract = s[match.end() : match1.start()+match.start()]
		else:
			choice = min(match1.start(),match2.start())
			#print match.start(), match1.start(), match2.start(), choice+match.start()
			abstract = s[match.end():choice+match.start()]
			#print abstract
		
		if re.search('[E|e]lsevier',abstract) is not None:
			#Journal is elsevier format. Requires additional filtering
			abstract = filterElsevierStart(abstract)
		else:
			pass
		
	except:
		pass

	
	try:
		cleanAbstract, noOfReplacements = re.subn('\n([\s\d] | [\s] | [\d]) | [\n\n]', ' ',abstract)
		cleanAbstract = re.sub("[A|a][B|b][S|s][T|t][R|r][A|a][C|c][T|t]|[A|a]\s?[B|b]\s?[S|s]\s?[T|t]\s?[R|r]\s?[A|a]\s?[C|c]\s?[T|t]",'',cleanAbstract)
		
		#cleanAbstract = re.sub('\n',' ',cleanAbstract)
		# while re.search('[A-Z]',cleanAbstract[0]) is None:
			# cleanAbstract = cleanAbstract[1:]
		cleanAbstract = cleanFirstPart(cleanAbstract)
		
		cleanAbstract, noOfReplacements2 = re.subn('\n\n',' ',cleanAbstract)	
		
		if noOfReplacements2 > 2:
			print "Text extracted could include sections outside of the abstract. Please remove extra text extracted\n"

		
		return finalCleanup(cleanAbstract)
		
	except:
		print 'Post processing of abstract encountered some error!'
		return abstract
		
authorList = []
finalSetOfAuthors = {}
authorPartOfFile = ''
tfile = ''
pfile = ''
title = ''

import time




#os.chdir('./elsevier_converted/')
i = 0
for file1 in os.listdir('.'):
	
	i = i+1
	if i > 50:
		break
		
	
	
	if file1[-3:] == 'pdf':
		#convert to both xml and text formats
		call(["pdftohtml", "-c", "-i", "-xml", file1 ])
		time.sleep(2)
		call(["pdftotext", file1])
		time.sleep(0.3)
		
		#os.chdir('../')
		file2 = file1[:-4]+'.xml'
		
		outputFile = "../allfiles_w_o_abs/" + file1[:-4] + 'DATAMANAGEMENT'+'.txt'
		of = open(outputFile,"w")
		
		f = file(file2,'r+')
		f.truncate(10000)
		sx = f.read()
		
		print file1+': '
		try:
			#TITLE EXTRACTION FROM XML FILE:
			#print "\nTITLE:\n"
			title = Extract(sx)
			print title
			of.write(title)
			
			#AUTHOR EXTRACTION FROM TEXT FILE
			tfile = file1[:-4]+'.txt' 		
			tf = open(tfile,"r+")
			tf.truncate(10000)			
			s = tf.read()				
			
			authorPartOfFile = extractAuthorPartOfFile(title,sx,s)
			
			print "\nAUTHORS:\n"
			if authorPartOfFile == '':
				#print 'Extraction was unsuccessful\n'
				of.write("Extraction was unsuccessful\n")
			else:
				authorPartOfFile = filterUnwantedChars(authorPartOfFile)
				authorList = filterIndividualNames(authorPartOfFile)
				printFinalSetOfAuthors(authorList)
				#print '\n\n'
			
			
		except:
			#print "Extraction was not possible due to some error. Please enter the author names"
			#print(traceback.format_exc())		
			pass
		#call(["mv", outputFile, "../outputFiles/"])
		
		
		try:
			print "JOURNAL:"
			of.write(extractJournal(s))
			print "\n\n"
		except:
			print(traceback.format_exc())
			print "NULL"
		#Extract doi
		try:
			print "DOI/ISSN:"
			#f1.truncate(8000)
			#s = f1.read()
			extractDoi(s)
			print "\n\n"
		except:	
			print(traceback.format_exc())
			print "NULL"
		#Extract Abstract
		try:
			print "ABSTRACT:"
			#f1.truncate(6000)
			#s = f1.read()
			#of.write(getAbstract(s))
			print "\n\n"
		except:
			print(traceback.format_exc())
			print "No abstract found"
			
		#Extract keywords
		try:
			print "KEYWORDS:"
			of.write(keywExtract(s))
			print "\n\n"
		except:
			print(traceback.format_exc())
			print 'No author entered keywords found'
		
		print '\n'
		
		
		of.close()

		
call(["rm", "-f", "*.png"])
call(["rm", "-f", "*.jpg"])		

