#Automatic Metadata Extraction from scientific documents
#
#Author: Sreehari <f2013126@goa.bits-pilani.ac.in>
#
"""
This script extracts the title and author-names from scientific documents.

TITLE EXTRACTION:

Title extraction is based on a font-analysis method.
The extraction involves checking font specifications of xml files,
and extraction of relevant text followed by a guessing correctness.
A guess that extraction has failed means that extraction is tried with a new set of ids.


AUTHOR EXTRACTION:

Author extraction is partially dependant on the title extraction and mostly works based on specialised 
regular expressions and filtering functions written specifically to extract authors from scientific documents.
First, the relevant portion of the text is extracted and then a line by line processing is done.
Filtering ensures the relevant line(s) is extracted following which further filters are called.
Further filtering involves removal of extra characters and extraction of individual names.

Changes can be made to the following to improve the filtering:
	-> matchCommonWords [] - a list that helps remove lines containing the description
							of author workplaces, university names, dept. details, etc.
	-> regular expressions to extract individual names inside the printFinalSetOfAuthors() function, 
		the case where a long string (greater than 30 characters in length) is extracted.

ABSTRACT EXTRACTION:

First, the portion of the text file containing the abstract section is detected by 
looking for the relevant words or looking for a new paragraph of text after reading 
a certain minimum number of bytes from the beginning of the abstract section.

In case of Elsevier journals, a special filter is implemented to remove extra text found 
at the beginning and at the end of the extracted portion.

In addition to these, a filter to clean up the initial portion is defined, 
which makes sure only the relevant text following the abstract is printed, 
without printing any additional unnecessary characters.


KEYWORD EXTRACTION:

First, the portion of the text file containing the keywords or index terms are located.
All relevant text, after extraction, is cleaned up so that only relevant text 
and delimiters are printed.


JOURNAL NAME EXTRACTION:

Implemented by looking for key phrases like Journal or Journal of and
extracting and processing the text both preceding and succeeding the matched text,
in the case of non-elsevier journals. 

For most new elsevier journals, as in the case of volume extraction,
journal names are found in the header portion just before the first instance
of the word elsevier is found. So, journal names, in this case are extracted
by extraction of the line just preceding the matched line. 

Once the basic extraction is done, filtering is done to 
remove unnecessary text from the extracted portion, which could
include the information on Volume, Issue, etc.(if present)


DATE EXTRACTION:

Date is being extracted directly from the pdfs metadata. This metadata 
information can be obtained easily using the linux - pdfinfo command. 
Currently, creation date is being used to obtain the required date.

The problem associated with extraction of date directly from the pdfs 
text is that, both month and year of publishing, are not always present 
within the pdf text, and the pdf metadata information proves to be a 
more reliable source of information than extraction from the text. 


VOLUME, ISSUE AND PAGE NUMBER EXTRACTION:

For extraction of information regarding the volume and issue number of the journal, 
first,we differentiate between elsevier published documents and other documents.


For non-elsevier journals, we try the extraction using two different methods. 
First we directly find a match for keywords like Vol. / Volume and match 
the text following it.

The above method does not work(as in the case of elsevier journals) 
when the specific keywords are not stated and instead the information
is only implied via. the header. So, we use a generic regex, followed by
some processing, on the header part of the file, to find the same, if it exists.

We use a special regex, in case of elsevier journals, in order to 
specifically look at the header portion for a certain pattern common to 
all elsevier journals, which gives the volume, issue, year and relevant pages/page numbers.



"""


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
		title = re.sub("(\s|\.)[\d]$",'',title)										#Remove digits that get appended at the end of the title
		
		
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
			#print "Title couldn't be extracted. Please enter the title"
			return ''
	except:
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
				print ''
				return
		
	slist = s.split('\n')		
	news = ''
	
	try:
		for sent in slist:
			matchCommonWords = re.search('((University)|(Department)|(Group)|(IGCAR)|(Gandhi)|(Indira Gandhi)|(Division)|(Chennai)|(College)|(Engineering)|(Academy)|(Research)|(Centre)|(Organi[s|z]ation)|(Section)|(Head)|(Dept)|(Corporation)|(Nuclear)|(Energy))',sent)
						
			if matchCommonWords is None:
				news = news + sent
				
			else:
				break
		
		return news 		#authorPartOfFile for final processing
		
	except:
		#print "NULL"
		#print ''
		return news

	
def filterIndividualNames(s):
	s = re.split(',',s)
	return s
	
def filterUnwantedChars(authorPartOfFile):
	#Replace and with comma for further filters
	authorPartOfFile = re.sub('\sand\s', ' , ',authorPartOfFile)
	#Filter out unnecessary characters
	authorPartOfFile = re.sub('(\s[a-z]{1,4})|(\*)' , ' ' ,authorPartOfFile)
	#Filter out numbers
	authorPartOfFile = re.sub('\d',' ',authorPartOfFile)
	#Filter out brackets
	authorPartOfFile = re.sub('\(.*\)','',authorPartOfFile)
	
	return authorPartOfFile

def printFinalSetOfAuthors(authorPartOfFile):	

	for names in authorPartOfFile: 
		if len(names) > 3 and len(names)<=30:
			names = re.sub('[^A-Za-z\s\.]+', '', names)
			print names,', ',	
		
		if len(names) > 30:
		
			#Run through some sort of filter or any other method to get author names embedded in this text
			try:
				matchcaps = re.search('[A-Z]{2,}([A-Z]{1}\.(.*))',names)			#Searching for text following an All-Caps text(mostly title)
				
				try:
					commaPresence = re.search(',', matchcaps.groups(0)[0])
					if commaPresence is not None:
						for n in re.split(',', matchcaps.groups(0)[0]):
							n = re.sub('[^A-Za-z\s\.]+', '', n)
							print n,', ',	
					else:
						for n in matchcaps.groups(0)[0].split():
							n = re.sub('[^A-Za-z\s\.]+', '', n)
							print n,', ',	
					continue
				
				except:
					pass
			
			except:
				#print "Inside tough block"
				try:
					matchcaps = re.search('([A-Z][a-z]+\s[A-Z][a-z]+)\s', names)
					print matchcaps.groups(),', ',	
					
				except:
					#print "Author extraction hit a wall. Please rescue with your own efforts"
					print ''
				

def filter1(s):
	s = re.sub('[^A-Za-z&\s]',' ',s)
	return s
	
def filter2(s):
	s = re.sub('Vol(.*)|Volume(.*)',' ',s)
	return s
	
def extractJournal(s):
	try:
		if re.search('elsevier',s) is not None:
			print "Elsevier: ", 
			matchE = re.search('\n?(.*)\n(.*)(elsevier)',s,re.MULTILINE)
			jnl = filter1(matchE.groups(0)[0])
			print jnl
			
		else:
			
			try:
				matchJ = re.search('(\n?(.*)([J|j]ournal [O|o]f)(.*)\n\n)|(\n?(.*)([J|j]ournal)(.*)\n\n)|(\n?(.*)([J|j]ournal)(.*)\n)', s,re.MULTILINE)

				jnl = filter1(s[matchJ.start():matchJ.end()])
				jnl = filter2(jnl)
				
				wordsInJnl = jnl.split()	
				
				if len(wordsInJnl) > 15:		#To check if wrong extraction is done or Extracted from doc's text by mistake
					print "" 
				else:
					print jnl
			except:
				print ""
				#print(traceback.format_exc())
				
	
	except:
		print ''

def doiFilter(s):
	try:
		matchDoi = re.search('(:)|(/)',s)
		s = s[matchDoi.end():]
	except:
		print ''
	return s
	
	
def extractISSN(s):
	try:

		matchISSN = re.search('(.*)((ISSN)|(ISBN))(.*)\n?',s,re.MULTILINE)
		
		if matchISSN is None:						# Guess possible ISSN/ISBN
			try:
				#print "Guessing possible ISSN/ISBN"
				matchI = re.search('\D([\d]{4}-[\d]{4})\D',s1)		
				if matchI is not None:
						print matchI.group()
			except:
				print ""
				
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
		print ""
		
def extractDoi(s):
	try:
		#Extract Volume/Issue/PP of Journal(Only meant for journals)
		volExtract(s)
		print " ; ",
	
		#Extract DOI if available
		matchE = re.search('\n?(.*)(doi)(.*)\n?|\n?(.*)([D|d]igital [O|o]bject [I|i]dentifier)(.*)\n?|\n?(.*)(DOI)(.*)\n?',s,re.MULTILINE)
		
		if matchE is not None:
			print doiFilter(matchE.groups(0)[2])		#Print DOI if found
		
		#Extract ISSN/ISBN if available
		else:
			extractISSN(s)								

	except:
		print ''

def volExtract(s):
	try:
	
		#Do differently for elsevier files
		if re.search('elsevier',s) is not None:
			#ELSEVIER CASE:
			
			t = s[:700]
	
			for sent in t.split('\n'):
				matchPP = re.search("\d{1,3}\s\(\d{4}\)\s",sent)
				if matchPP is not None:
					#Printing all details
					vol = re.sub('[A-Za-z]',' ',sent)
					while vol[0] == ' ':
						vol = vol[1:]
					print vol,
					
					break
			
		else:
			#Try normal method
			try:
				matchV = re.search("Vol\.|Volume",s)
				matchEndOfLine = re.search('\n',s[matchV.start():])
				print s[matchV.start():matchEndOfLine.start()+matchV.start()],
				
			except:
				#No info
				try:
					t = s[:700]
					for sent in t.split('\n'):
						matchY = re.search("\(\d{4}\)",sent)
						if matchY is not None:
							sent = re.sub('[A-Za-z]','',sent[:matchY.start()]) + sent[matchY.start():]
							print sent,
							break
									
				except:
					print "",
	
	
	except:
		print "",
		
		
def keywExtract(s):
	try: 
		matchK = re.search('(Keywords)(.*)|(Index Terms)(.*)|([K|k]ey [W|w]ords)',s)
		
		matchKE = re.search("\n\n",s[matchK.start():])
		
		kwords = s[matchK.start():matchK.start()+matchKE.start()]
		if kwords[0] == 'K':
			kwords = kwords[9:]
		else:
			kwords = kwords[14:]
		
		#Cleaning up kwords
		while re.search('[A-Z|[a-z]',kwords[0]) is None:
			kwords = kwords[1:]
		
		#Not printing as php processing requires all output delimited by commas
		#print kwords
		
		nkwords = kwords
		
		if re.search(',|;',kwords) is None:
			#Modifying the output for php processing. Appending a delimiter where there is none
			nkwords = re.sub('\n',', ',kwords)
		else:
			nkwords = re.sub('\n',' ',kwords)
			
		print "\n\n",nkwords
		
	except:
		return
		
		

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
			print ""
		
		i += 1
	
	swords = newa.split()
	matchRealAbs = re.search(swords[0],abstract)
	abstract = abstract[matchRealAbs.start():] 
	
	return abstract

def finalCleanup(abs):		#To cleanup the final elsevier line that gets appended to the extract
	try:
		matchElsevier = re.search('\n(.*)[E|e]lsevier(.*)\n?',abs,re.MULTILINE)
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
		#No abstract detected
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
		
		cleanAbstract = cleanFirstPart(cleanAbstract)
		
		cleanAbstract, noOfReplacements2 = re.subn('\n\n',' ',cleanAbstract)	
		
		if noOfReplacements2 > 2:
			#Text extracted could include sections outside of the abstract. 
			print ''
			
		cleanAbstract = finalCleanup(cleanAbstract)
		cleanAbstract = re.sub('\n',' ',cleanAbstract)
		print cleanAbstract
		
	except:
		#print "NULL"	
		print abstract
		
def getFullMonth(month):
    return {
		
		'Jan': 'January',
		'Feb': 'February',
		'Mar': 'March',
		'Apr': 'April',
		'May' : 'May',
		'Jun' : 'June',
		'Jul' : 'July',
		'Aug' : 'August',
		'Sep' : 'September',
		'Oct' : 'October',
		'Nov' : 'November',
		'Dec' : 'December',
		
    }[month]
	
def extractDate(pdf):
	cmd = "pdfinfo " + pdf
	cmdout = commands.getoutput(cmd)
	date1 = ''
	date = []
	try:
		c_date = re.search('CreationDate:',cmdout)
		m_date = re.search('ModDate:',cmdout)
		date1 = cmdout[c_date.start():m_date.start()]
		date = date1.split()
		
		month = str(date[2])
		nmonth = month
		nmonth = getFullMonth(month)
		
		date2 = nmonth + ',' + str(date[5])
		print date2
		
	except:
		print ''		
		
authorList = []
finalSetOfAuthors = {}
authorPartOfFile = ''
tfile = ''
pfile = ''
title = ''

#ASSUMPTION
#Name of xnl file is passed as the first argument to the script from php
#sys.argv[1] has the common name of both converted files (text and xml)


xmlfile = sys.argv[1] + ".xml"



f = file(xmlfile,'r+')				#READ XML FILE
f.truncate(8500)					#Alter this value if xml files do not contain the title within the first ( 8500 ) bytes; Try 7000, 10000, etc., for best results
sx = f.read()			

try:
	#TITLE EXTRACTION FROM XML FILE:
	print "\nTITLE:\n"
	title = Extract(sx)
	print title
	
	
	#AUTHOR EXTRACTION FROM TEXT FILE
	tfile = xmlfile[:-4]+'.txt' 		
	tf = open(tfile,"r+")
	tf.truncate(10000)				#Alter this value if text file does not contain the title within the first ( 3000 ) bytes; 
	s = tf.read()				
	
	authorPartOfFile = extractAuthorPartOfFile(title,sx,s)
	
	print "\nAUTHORS:\n"
	if authorPartOfFile == '':
		print ''
	else:
		authorPartOfFile = filterUnwantedChars(authorPartOfFile)
		authorList = filterIndividualNames(authorPartOfFile)
		printFinalSetOfAuthors(authorList)
		print '\n\n'
	
	
except:
	print ''

	
try:
	print "JOURNAL:"
	extractJournal(s)
	print "\n\n"
except:
	print ''
#Extract doi
try:
	print "DOI/ISSN:"
	extractDoi(s)
	print "\n\n"
except:	
	print ''
#Extract Abstract
try:
	print "ABSTRACT:"
	getAbstract(s)
	print "\n\n"
except:
	print ''
#Extract keywords
try:
	print "KEYWORDS:"
	keywExtract(s)
	print "\n\n"
except:
	print ''

#Extract publishing date
try:
	print "DATE:"
	pdf = sys.argv[1] + ".pdf"
	extractDate(pdf)
	print "\n\n"
except:
	print ''
print '\n'	
