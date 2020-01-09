#to remove stopwords in term synonyms
#to remove genitives
#to process puncutations
import codecs
from time import time
import json
import os
import sys
import re
import string
from global_module import *
from nltk.tag import HunposTagger
from nltk.stem.wordnet import WordNetLemmatizer

print
from nltk.tag.perceptron    import PerceptronTagger

#tagger=HunposTagger('en_wsj.model')
#tagger=PerceptronTagger()
lemmatizer=WordNetLemmatizer()

#to generate string complete-combination of list 1 and list 2
#used in punctuation process and synonym combination
def stringCompleteCombination(list1,list2,sep=' '):
	if len(list1)==0:
		for x in list2:
			yield x
	elif len(list2)==0:
		for x in list1:
			yield x
	else:
		for x in [sep.join([x,y]) for x in list1 for y in list2]:
			yield x

#to generate all the combinations of sentence-splitted parts and punctuation-matched parts for each term
#return value: the list of all the combinations for each term
def punctuationCombination(termPartList,matchPartDict):
	combinationList=[]
	for p in iter(termPartList):
		if p in matchPartDict.iterkeys():
			combinationList=list(stringCompleteCombination(combinationList,matchPartDict[p]))
		else:
			combinationList=list(stringCompleteCombination(combinationList,[p]))
	return combinationList

#to process punctuations in terms
#rule:
#'s & ': removed
#'t: replaced by not 
#<>: replaced by space
#a (b): generating two words a with or without b
#a {b}: generating two words a with or without b
#a [b]: generating two words a with or without b
#a-b: generating ab if num<3 
#a/b: generating a and b
#a-b: generating three words a-b, ab and a b if - number < 3 and generating words a-b and a b if - number =>3(depreciated)
#a/b: generating three words a b, a and b (depreciated)
#a_b: generating a b and a_b (depreciated)
#a, b: generating one word a b (depreciated)
def punctuationProcess(term):
	term=term.replace("'s",'').replace("'t",' not ').replace("'d",' would ').replace("'l",' will ').replace("'",'').replace('&',' and ').replace('|', ' or ')
	term=' '.join([x for x in word_tokenizer(term) if not check_stopwords(x)])
	if len(word_tokenizer(term))==1:
		if check_frequent_words(x):
			term=''
		else:
			pass
	else:
		pass
	newTerms=[]
	oldTerm=term
	
	#'s: removed
	#': removed
	#'t: replaced by not
	#'d: would
	#'l: will
	#&: and
	#|: or

	#oldTerm=oldTerm.replace("'s",'').replace("'t",' not ').replace("'d",' would ').replace("'l",' will ').replace("'",'').replace('&',' and ').replace('|', ' or ')
	#a,/;/:b: generating one word a b

	oldTerm=oldTerm.replace(', ',' ')
	oldTerm=oldTerm.replace('; ',' ')
	oldTerm=oldTerm.replace(': ',' ')
	
	if oldTerm.endswith(','):
		oldTerm=oldTerm[:-1]
	
	oldTerm=oldTerm.replace('; ',' ')
	if oldTerm.endswith(';'):
		oldTerm=oldTerm[:-1]
	
	oldTerm=oldTerm.replace(': ',' ')
	if oldTerm.endswith(':'):
		oldTerm=oldTerm[:-1]
	oldTerm=oldTerm.replace(',',' ')
	oldTerm=oldTerm.replace('/',' ')
	oldTerm=oldTerm.replace(':',' ')
	
	
	##<>: replaced by space
	oldTerm=oldTerm.replace('<',' ').replace('>',' ')
	

#if term contains too many punctuations(at least 5), just remove them and skip
	if reduce(lambda x,y:x+y,map(lambda z:oldTerm.count(z),list(string.punctuation)))>=4:
		for p in list(string.punctuation):
			oldTerm=oldTerm.replace(p,' ')
		yield oldTerm
		
	else:
	#umlaut processing
	#for german
		newTerms.append(oldTerm.replace('\xc3\xa4','ae'))
		newTerms.append(oldTerm.replace('\xc3\xb6','oe'))
		newTerms.append(oldTerm.replace('\xc3\xbc','ue'))
		newTerms.append(oldTerm.replace('\xc3\x9f','ss'))
		
	
	
	#a (b): generating two words a with or without b
		tempList,newTerms=newTerms,[]
		pattern=re.compile("\s?(\(.+?\))\s?")
		for term in iter(tempList):
			if term.find('(')>-1 and term.find(')')>-1:
				matchPartList=pattern.findall(term)
				termPartList=[x for x in pattern.split(term) if len(x)>0]
				matchPartDict=dict()
				for p in iter(matchPartList):
					#matchPartDict[p]=[p[1:-1],'']
					matchPartDict[p]=[p[1:-1]]
				newTerms.extend([x for x in punctuationCombination(termPartList,matchPartDict) if len(x.split())>1])
			else:
				newTerms.append(term)
	
	#a {b}: generating two words a with or without b
		tempList,newTerms=newTerms,[]
		pattern=re.compile("\s?(\{.+?\})\s?")
		for term in iter(tempList):
			if term.find('{')>-1 and term.find('}')>-1:
				matchPartList=pattern.findall(term)
				termPartList=[x for x in pattern.split(term) if len(x)>0]
				matchPartDict=dict()
				for p in iter(matchPartList):
					#matchPartDict[p]=[p[1:-1],'']
					matchPartDict[p]=[p[1:-1]]
				newTerms.extend([x for x in punctuationCombination(termPartList,matchPartDict) if len(x.split())>1])
			else:
				newTerms.append(term)
	
	#a [b]: generating two words a with or without b
		tempList,newTerms=newTerms,[]
		pattern=re.compile("\s?(\[.+?\])\s?")
		for term in iter(tempList):
			if term.find('[')>-1 and term.find(']')>-1:
				matchPartList=pattern.findall(term)
				termPartList=[x for x in pattern.split(term) if len(x)>0]
				matchPartDict=dict()
				for p in iter(matchPartList):
					#matchPartDict[p]=[p[1:-1],'']
					matchPartDict[p]=[p[1:-1]]
				newTerms.extend([x for x in punctuationCombination(termPartList,matchPartDict) if len(x.split())>1])
			else:
				newTerms.append(term)
	
	##	a-b: generating three words a-b, ab and a b
	#	tempList,newTerms=newTerms,[]
	#	pattern=re.compile("\s?([^\s]+?\-[^\s^\-]+)\s?")
	#	for term in iter(tempList):
	#		if term.find('-')>-1:
	#			matchPartList=pattern.findall(term)
	#			print matchPartList
	#			termPartList=[x for x in pattern.split(term) if len(x)>0]
	#			matchPartDict=dict()
	#			for p in iter(matchPartList):
	#				matchPartDict[p]=[]
	#				matchPartDict[p].append(p)
	#				matchPartDict[p].append(''.join(p.split('-')))
	#				matchPartDict[p].append(' '.join(p.split('-')))
	#			newTerms+=punctuationCombination(termPartList,matchPartDict)
	#		else:
	#			newTerms.append(term)
	
#	#a-b: generating three words a-b, ab and a b if - number < 3 and generating words a-b and a b if - number =>3
#		tempList,newTerms=newTerms,[]
#		for term in iter(tempList):
#			if term.count('-')<3 and term.count('-')>0:
#				s=term.split('-')[:1]
#				for x in term.split('-')[1:]:
#					s=list(stringCompleteCombination(s,map(lambda y:y+x,['-','',' ']),sep=''))
#				newTerms.extend(s)
#			elif term.count('-')>=3:
#				newTerms.extend([term,term.replace('-',' ')])
#	#			s=term.split('-')[:1]
#	#			for x in term.split('-')[1:]:
#	#				s=list(stringCompleteCombination(s,map(lambda y:y+x,['-',' ']),sep=''))
#	#			newTerms.extend(s)
#			else:
#				newTerms.append(term)
				
	#a-b: generating three words a-b, ab and a b if - number < 3 and generating words a-b and a b if - number =>3
		tempList,newTerms=newTerms,[]
		for term in iter(tempList):
			if term.count('-')<3 and term.count('-')>0:
				s=term.split('-')[:1]
				for x in term.split('-')[1:]:
					s=list(stringCompleteCombination(s,map(lambda y:y+x,[' ','']),sep=''))
				newTerms.extend(s)
			elif term.count('-')>=3:
				newTerms.extend([term.replace('-',' ')])
				
	#			s=term.split('-')[:1]
	#			for x in term.split('-')[1:]:
	#				s=list(stringCompleteCombination(s,map(lambda y:y+x,['-',' ']),sep=''))
	#			newTerms.extend(s)
			else:
				newTerms.append(term)
				
#	#	a/b: generating three words a/b, a and b
#		tempList,newTerms=newTerms,[]
#		pattern=re.compile("\s?([^\s]+?/[^\s]+)\s?")
#		for term in tempList:
#			if term.find('/')>-1:
#				matchPartList=pattern.findall(term)
#				termPartList=[x for x in pattern.split(term) if len(x)>0]
#				matchPartDict=dict()
#				for p in iter(matchPartList):
#					matchPartDict[p]=[' '.join(p.split('/'))]
#					matchPartDict[p].extend(p.split('/'))
#				newTerms.extend(punctuationCombination(termPartList,matchPartDict))
#			else:
#				newTerms.append(term)

	#	a/b: generating three words a/b, a and b
		tempList,newTerms=newTerms,[]
		pattern=re.compile("\s?([^\s]+?/[^\s]+)\s?")
		for term in tempList:
			if term.find('/')>-1:
				matchPartList=pattern.findall(term)
				termPartList=[x for x in pattern.split(term) if len(x)>0]
				matchPartDict=dict()
				for p in iter(matchPartList):
					matchPartDict[p]=[' '.join(p.split('/'))]
					#matchPartDict[p].extend(p.split('/'))
				newTerms.extend([x for x in punctuationCombination(termPartList,matchPartDict) if len(x.split())>1])
			else:
				newTerms.append(term)

	
#	#	a_b: generating a b and a_b
#		tempList,newTerms=newTerms,[]
#		pattern=re.compile("\s?([^\s]+?\_[^\s]+)\s?")
#		for term in tempList:
#			if term.find('_')>-1:
#				matchPartList=pattern.findall(term)
#				termPartList=[x for x in pattern.split(term) if len(x)>0]
#				matchPartDict=dict()
#				for p in matchPartList:
#					matchPartDict[p]=[p,p.replace('_',' ')]
#					#matchPartDict[p]=[p.replace('_',' ')]
#				newTerms.extend(punctuationCombination(termPartList,matchPartDict))
#			else:
#				newTerms.append(term)
		
	#	a_b: generating a b and a_b
		tempList,newTerms=newTerms,[]
		pattern=re.compile("\s?([^\s]+?\_[^\s]+)\s?")
		for term in tempList:
			if term.find('_')>-1:
				matchPartList=pattern.findall(term)
				termPartList=[x for x in pattern.split(term) if len(x)>0]
				matchPartDict=dict()
				for p in matchPartList:
					matchPartDict[p]=[p.replace('_',' ')]
					#matchPartDict[p]=[p.replace('_',' ')]
				newTerms.extend([x for x in punctuationCombination(termPartList,matchPartDict) if len(x.split())>1])
			else:
				newTerms.append(term)

		newTerms=[x.strip(' ') for x in newTerms]
		newTerms=[x.replace('/','') for x in newTerms]
		newTerms=sorted(set(newTerms),key=newTerms.index)
		for i in xrange(0,len(newTerms)):
			for p in string.punctuation:
				newTerms[i]=newTerms[i].replace(p,' ')
		for term in iter(newTerms):
			yield unicode(term).translate(unicode2ascii)
	
def nlp_process(term):
	old_term=' '+term+' '
	old_term=old_term.replace("'s",'').replace("'t",' not ').replace("'d",' would ').replace("'l",' will ').replace("'",'').replace('&',' and ').replace('|', ' or ')
	old_term=' '.join([x for x in word_tokenizer(old_term) if not check_stopwords(x)])
	if len(old_term)==0:
		return []
	elif len(word_tokenizer(old_term))==1 and check_frequent_words(old_term) and check_stopwords(old_term):
		return []
	else:
		pass
	if sum(map(lambda x:old_term.count(x),string.punctuation))>punctuation_count_cutoff or sum(map(lambda x:old_term.count(x),string.punctuation))/len(old_term)>punctuation_percent_cutoff:
		return []
	else:
		pass
	new_terms=[]
	new_terms.append(old_term.replace('\xc3\xa4','ae'))
	new_terms.append(old_term.replace('\xc3\xb6','oe'))
	new_terms.append(old_term.replace('\xc3\xbc','ue'))
	new_terms.append(old_term.replace('\xc3\x9f','ss'))
        new_terms=[x for x in new_terms if len(word_tokenizer(x))>1 or (len(word_tokenizer(x))==1 and not check_stopwords(x) and not check_frequent_words(x))]
	#if sum(map(old_term.count,string.punctuation))<=4:
		#temp_term=old_term
		#for x in string.punctuation:
			#temp_term=temp_term.replace(x,'')
		#new_terms.append(temp_term)
	for i in xrange(0,len(new_terms)):
		for x in string.punctuation:
			if x!='-':
				new_terms[i]=new_terms[i].replace(x,' ')
	for i in xrange(0,len(new_terms)):
		new_terms[i]=' '.join(new_terms[i].replace(' -',' ').replace('- ',' ').replace(' - ',' ').split())
	new_terms.extend([x.replace('-','') for x in new_terms])
	analyzer1=AnalyzerForNLP()
	analyzer2=AnalyzerForAnalysis()
	new_terms=[' '.join([t.text for t in analyzer1(unicode(x))]) for x in new_terms]
	new_terms=sorted(set(new_terms),key=new_terms.index)
	return new_terms


time_record=time()

#input parameter: ontology name
ontology_name=sys.argv[1] 

print 'Ontology',ontology_name

#input file: ontology.obo
infile_name=ontology_name+'_term'+json_format
outfile_name=ontology_name+'_nlp'+json_format

infile=open(data_dir+os.path.sep+infile_name,'r')
term_synonyms=json.loads(infile.read())
infile.close()
'''
new_term_synonyms={}
for k in term_synonyms.iterkeys():
	new_term_synonyms[k]=[]
	for s in term_synonyms[k]:
		temp=list(punctuationProcess(s))
		for t in temp:
			tokens=word_tokenizer(t)
			tokens=map(lambda x:''.join(x[:x.index('\'')]) if x.find('\'')>-1 else x,tokens)
			tokens=filter(lambda x:x not in string.punctuation,tokens)
			tokens=filter(lambda x:not x.isspace(),tokens)
			if len(tokens)>0:
				new_term_synonyms[k].append(' '.join(tokens))
			#if len(tokens)==0:
				#pass
	new_term_synonyms[k]=sorted(set(new_term_synonyms[k]),key=new_term_synonyms[k].index)
for k in new_term_synonyms.keys():
	if len(new_term_synonyms[k])==0:
		new_term_synonyms.pop(k)
'''
new_term_synonyms={}
for k in term_synonyms.iterkeys():
	new_term_synonyms[k]=[]
	for v in term_synonyms[k]:
		if k=='geneprot~sash3':
			print [x for x in list(nlp_process(v)) if len(x)>0]
		new_term_synonyms[k].extend([x for x in list(nlp_process(v)) if len(x)>0])
for k in new_term_synonyms.keys():
	if len(new_term_synonyms[k])==0:
		new_term_synonyms.pop(k)
	'''
all_token_pos=set()
for x in new_term_synonyms.values():
	for t in x:
		all_token_pos|=set(tagger.tag(word_tokenizer(t)))
all_token_pos=sorted(all_token_pos)
with open(temp_dir+os.path.sep+ontology_name+'_nlp'+txt_format,'w') as outfile:
	for x in all_token_pos:
		outfile.write('\t'.join(x)+'\n')
	outfile.write('.\t.')
cmd='java -Xmx1G -jar lib/biolemmatizer-core-1.2-jar-with-dependencies.jar -i '+temp_dir+os.path.sep+ontology_name+'_nlp'+txt_format+' -o '+temp_dir+os.path.sep+ontology_name+'_nlp_lemmatized'+txt_format
os.system(cmd)
all_token_pos_lemmatized={}
with open(temp_dir+os.path.sep+ontology_name+'_nlp_lemmatized'+txt_format,'r') as infile:
	for x in infile.readlines():
		k=tuple(x.split()[:2])
		v=x.split()[2]
		if len(set(string.punctuation) & set(k[0]))==0:
			all_token_pos_lemmatized[k]=v
		else:
			all_token_pos_lemmatized[k]=k[0]
for k in new_term_synonyms.keys():
	for i,t in enumerate(new_term_synonyms[k]):
		new_term_synonyms[k][i]=' '.join([all_token_pos_lemmatized[x] for x in tagger.tag(word_tokenizer(t))])
	new_term_synonyms[k]=sorted(set(new_term_synonyms[k]),key=new_term_synonyms[k].index)
	'''
outfile=open(data_dir+os.path.sep+outfile_name,'w')
data=json.dumps(new_term_synonyms,encoding='utf-8',ensure_ascii=False)
outfile.write(data)
outfile.close()
print
print 'Consuming time...'
print time()-time_record
print 

