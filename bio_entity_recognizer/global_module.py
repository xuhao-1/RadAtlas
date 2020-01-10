from __future__ import division
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import numpy as np
import nltk
import string
import os
import json
import itertools
import math
from whoosh.analysis import *
from whoosh.query import *
from whoosh.index import *
from whoosh.fields import *
import cmath
import math
from statistics import variance
import networkx
from Bio.Cluster import *
from scikits.crab import *
import sklearn.cluster as cluster
from pymongo import MongoClient
from collections import OrderedDict
from multiprocessing import Pool,Lock,cpu_count
DEFAULT_MIN_SUBWORD_SIZE=4
DEFAULT_MAX_SUBWORD_SIZE=15

ont_type={
	'caloha':'Anatomy/Cell Type',
	#'cellosaurus':'Cell Line',
	#'cmo':'Clinic',
	'do':'Disease',
	'drugbank':'Drug',
	'ef':'Experimental Factor',
	'proteingene':'Gene/Protein',
	'go':'Function',
	#'hmdb':'Metabolite',
	'hp':'Phenotype',
	#'mop':'Process/Reaction',
	#'mi':'Interaction',
	'mod':'Modification',
	'mpath':'Pathology',
	'reactome':'Pathway',
	#'rnao':'RNA',
        #'se':'Side Effects',
	#'so':'Sequence',
	#'symp':'Symptom',
	#'vario':'Variation'
}
ont_list=sorted(ont_type.keys())
kb_list=sorted('CTD DrugBank GOA Mentha OMIM Reactome'.split())
omics_list=sorted('GXA_Differential'.split())
literature_list=['PubMed']
ont_to_simpleonts={}
ont_to_simpleonts.update(dict(zip(ont_list,['ontology']*len(ont_list))))
ont_to_simpleonts.update(dict(zip(kb_list,['kb']*len(kb_list))))
ont_to_simpleonts.update(dict(zip(omics_list,['omics']*len(omics_list))))
ont_to_simpleonts.update(dict(zip(literature_list,['literature']*len(literature_list))))
simpleonts=['kb','literature','omics','ontology']
simplejumping={
	'ontology,omics':1/2,
	'omics,ontology':1/2,
	'ontology,literature':1/4,
	'literature,ontology':1/4,
	'ontology,kb':1/4,
	'kb,ontology':1/4,
}

def get_simplejumping(x):
	return simplejumping[','.join([ont_to_simpleonts[t] for t in x])]

jumping={}
from itertools import product
#ontology to literature
#literature to ontology
for x in product(ont_list,literature_list):
	jumping[','.join(x[::-1])]=jumping[','.join(x)]=get_simplejumping(x)*1/(len(ont_list)*len(literature_list))
#ontology to omics
#omics to ontology
for x in product(ont_list,omics_list):
	jumping[','.join(x[::-1])]=jumping[','.join(x)]=get_simplejumping(x)*1/(len(ont_list)*len(omics_list))
#ontology to kb
#kb to ontology
for x in product(ont_list,kb_list):
	jumping[','.join(x[::-1])]=jumping[','.join(x)]=get_simplejumping(x)*1/(len(ont_list)*len(kb_list))
ont_depth_cutoff={
	'caloha':0,
	'cellosaurus':0,
	'cmo':0,
	'do':2,
	'drugbank':'0',
	'ef':4,
	'proteingene':0,
	'go':0,
	'hmdb':0,
	'hp':2,
	#'mop':1,
	'mi':3,
	'mod':2,
	'mpath':2,
	'reactome':0,
	#'rnao':0,
	'se':0,
	#'so':2,
	'symp':1,
	#'vario':1,
}

p_cutoff=0.13
npmi_cutoff=0.0
cooccurrence_cutoff=2
ci_cutoff=0.15

query_slop_cutoff=1
phrase_slop_cutoff=1

semantic_dist=4
min_word_size=2
punctuation_percent_cutoff=0.5
punctuation_count_cutoff=8
term_size_cutoff=5

mapping_dir='mapping'
gold_dir='gold'
ontology_dir='ontology'
hin_dir='hin'
lib_dir='lib'
data_dir='data'
temp_dir='temp'
text_dir='text'
pubmed_dir='pubmed'
index_dir='index'
start_year=1983
end_year=2018
search_dir='search'
word_dir='word'
raw_text_dir='raw_text'
gxa_dir='gxa'
assess_dir='assess'
kb_dir='kb'
xml_format='.xml'
owl_format='.owl'
obo_format='.obo'
json_format='.json'
txt_format='.txt'
tsv_format='.tsv'
pkl_format='.pkl'
gz_format='.gz'
npy_format='.npy'
csv_format='.csv'
msh_format='.msh'
connection_string='postgres://root:root@localhost:5432/concept_network'
dsn='http://localhost:7474/db/data/'

child_num=1
#start_year=1946
#end_year=2018
recent_years=10

#infile_name='word_dictionary.json'
#infile=open(lib_dir+os.path.sep+infile_name,'r')
#word_dictionary=json.loads(infile.read())
#infile.close()
#word_dictionary=filter(lambda x:len(x)>=DEFAULT_MIN_SUBWORD_SIZE and len(x)<=DEFAULT_MAX_SUBWORD_SIZE,word_dictionary)

#infile_name='word_mappings.json'
#infile=open(lib_dir+os.path.sep+infile_name,'r')
#word_mappings=json.loads(infile.read())
#infile.close()

#word_synonyms={}
#for x in word_mappings:
	#if word_synonyms.has_key(x[0]) and x[1] not in word_synonyms[x[0]]:
		#word_synonyms[x[0]].append(x[1])
	#elif word_synonyms.has_key(x[0]):
		#pass
	#else:
		#word_synonyms[x[0]]=[x[1]]

infile_name='stopwords.json'
infile=open(lib_dir+os.path.sep+infile_name,'r')
stopwords=json.loads(infile.read())
stopwords_set=set(stopwords)
infile.close()

infile_name='general_words.json'
infile=open(lib_dir+os.path.sep+infile_name,'r')
general_words=json.loads(infile.read())
general_words_set=set(general_words)
infile.close()

def check_stopwords(x):
	return (x.strip() in stopwords_set)

def check_general_words(x):
	return (x.strip() in general_words_set)

infile_name='frequent_words.json'
infile=open(lib_dir+os.path.sep+infile_name,'r')
frequent_words=json.loads(infile.read())
frequent_words_set=set(frequent_words)
infile.close()

import unicodedata
import sys
 
tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P'))
def remove_punctuation(text):
	return unicode(text.strip()).translate(tbl)

def check_frequent_words(x):
	return (remove_punctuation(x).strip() in frequent_words_set or remove_punctuation(x).strip() in stopwords_set or remove_punctuation(x).strip().isdigit() or (remove_punctuation(x).strip().isalpha() and len(remove_punctuation(x).strip())==1))

infile_name='aa_words.json'
infile=open(lib_dir+os.path.sep+infile_name,'r')
aa_words=json.loads(infile.read())
infile.close()

def check_aa_words(x):
	return (x in aa_words)

default_expression=r"((\w+\'*\.*\,*\w*\-*\w*)+|(\w*\'*\.*\,*\w+\-*\w*)+|(\w*\'*\.*\,*\w*\-*\w+)+)+"
#default_expression=r"((\w+\-*\w*)+|(\w*\-*\w+)+)+"

def word_tokenizer(s):
	return nltk.tokenize.WhitespaceTokenizer().tokenize(s)

def load():
	infile_name='unicode2ascii.json'
	infile=open(lib_dir+os.path.sep+infile_name,'r')
	unicode2ascii=json.loads(infile.read())
	infile.close()
	a_list=filter(lambda x:x in string.printable,sorted(unicode2ascii.keys()))
	for a in a_list:
		unicode2ascii.pop(a)
	return unicode2ascii

unicode2ascii=dict(map(lambda x:(ord(x[0]),x[1]),load().items()))
#def unicode2ascii(s):
#	unicode2ascii=load()
#	for u in unicode2ascii.keys():
#		if u in s:
#			a=unicode2ascii[u]
#			s=s.replace(u,a)
#		else:
#			pass
#	return s

class SynonymFilter(Filter):
	def __init__(self,worddict):
		super(SynonymFilter,self).__init__()
		self.worddict=worddict
	def __call__(self,tokens):
		for token in tokens:
			if token.positions:
				yield token
				if self.worddict.has_key(token.text):
					for synonym in self.worddict[token.text]:
						token.text=synonym
						yield token

#def BioTokenizer(expression=default_expression):
#		return RegexTokenizer(expression)

class BioTokenizer(RegexTokenizer):
	def __init__(self,expression=default_expression):
		super(BioTokenizer,self).__init__(expression)
	def __call__(self, value, positions=True, chars=False, keeporiginal=False,
		removestops=True, start_pos=0, start_char=0, tokenize=True,
		mode='', **kwargs):
		for t in super(BioTokenizer,self).__call__(value, positions=True, chars=False, keeporiginal=False,removestops=True, start_pos=0, start_char=0, tokenize=True,mode='', **kwargs):
			if len(t.text)>0:
				yield t

#class UnicodeNormalizationFilter(Filter):
#	def __call__(self,tokens):
#		for t in tokens:
#			t.text=unicode(unicode2ascii(t.text))
#			yield t

#class CompoundWordTokenFilter(CompoundWordFilter):
#	def __init__(self,wordset,keep_compound=True,ignoreChars='-,.'):
#		super(CompoundWordTokenFilter,self).__init__(wordset,keep_compound)
#		self.ignoreChars=ignoreChars
#
#	def subwords(self, s, memo):
#		a=super(CompoundWordTokenFilter,self).subwords(s,memo)
#		#b=super(CompoundWordTokenFilter,self).subwords(re.sub(re.compile('[\\'+'\\'.join(list(self.ignoreChars))+']+'),'',s),memo)
#		b=[]
#		if a:
#			if b:
#				return sorted(set(a+b),key=(a+b).index)
#			else:
#				return a
#		else:
#			if b:
#				return b
#			else:
#				return a

#class CompoundWordTokenFilter(CompoundWordFilter):
#	def __init__(self,wordset,keep_compound=True,ignoreChars='-,.'):
#		super(CompoundWordTokenFilter,self).__init__(wordset,keep_compound)
#		self.ignoreChars=ignoreChars
#
#	def __call__(self,tokens):
#		keep_compound=self.keep_compound
#		wordset=self.wordset
#		for token in tokens:
#			if token.text in wordset:
#				yield token
#			else:
#				wordset=filter(lambda x:x in token.text and x!=token.text,self.wordset)
#				if len(wordset)>0:
#					pattern=re.compile('[\\'+'\\'.join(list(self.ignoreChars))+']+')
#					start=int(math.floor(len(token.text)/max(map(lambda x:len(x),wordset))))
#					end=int(math.ceil(len(token.text)/min(map(lambda x:len(x),wordset))))+1
#					subwords=[]
#					for i in xrange(start,end):
#						subwords.extend(list(itertools.permutations(wordset,i)))
#					subwords=filter(lambda x:''.join(x)==re.sub(pattern,'',token.text),subwords)
#					if keep_compound:
#						yield token
#					if subwords:
#						min_length=min(map(lambda x:len(x),subwords))
#						subwords=filter(lambda x:len(x)==min_length,subwords)[0]
#						for subword in subwords:
#							token.text=subword
#							yield token
#				else:
#					yield token

class BioIntraWordFilter(IntraWordFilter):
	def __init__(self, delims=u("-_'\"()!@#$%^&*[]{}<>\|;:,./?`~=+"),
				 splitwords=True, splitnums=True,
				 mergewords=False, mergenums=False):
		"""
		:param delims: a string of delimiter characters.
		:param splitwords: if True, split at case transitions,
			e.g. `PowerShot` -> `Power`, `Shot`
		:param splitnums: if True, split at letter-number transitions,
			e.g. `SD500` -> `SD`, `500`
		:param mergewords: merge consecutive runs of alphabetic subwords into
			an additional token with the same position as the last subword.
		:param mergenums: merge consecutive runs of numeric subwords into an
			additional token with the same position as the last subword.
		"""

		from whoosh.support.unicode import digits, lowercase, uppercase

		self.delims = re.escape(delims)

		# Expression for text between delimiter characters
		self.between = re.compile(u("[^%s]+") % (self.delims,), re.UNICODE)
		# Expression for removing "'s" from the end of sub-words
		dispat = u("(?<=[%s%s])'[Ss](?=$|[%s])") % (lowercase, uppercase,
													self.delims)
		self.possessive = re.compile(dispat, re.UNICODE)

		# Expression for finding case and letter-number transitions
		lower2upper = u("[%s][%s]") % (lowercase, uppercase)
		letter2digit = u("[%s%s][%s]") % (lowercase, uppercase, digits)
		digit2letter = u("[%s][%s%s]") % (digits, lowercase, uppercase)
		word2word = u("[%s%s%s][%s][%s%s%s]") % (digits,lowercase,uppercase,self.delims,digits,lowercase,uppercase)
		if splitwords and splitnums:
			splitpat = u("(%s|%s|%s)") % (lower2upper, letter2digit,
										  digit2letter)
			self.boundary = re.compile(splitpat, re.UNICODE)
		elif splitwords:
			self.boundary = re.compile(text_type(lower2upper), re.UNICODE)
		elif splitnums:
			numpat = u("(%s|%s)") % (letter2digit, digit2letter)
			self.boundary = re.compile(numpat, re.UNICODE)
		else:
			self.boundary = re.compile(word2word,re.UNICODE)
		self.splitting = splitwords or splitnums
		self.mergewords = mergewords
		self.mergenums = mergenums

	def _split(self, string):
		bound = self.boundary

		# Yields (startchar, endchar) pairs for each indexable substring in
		# the given string, e.g. "WikiWord" -> (0, 4), (4, 8)

		# Whether we're splitting on transitions (case changes, letter -> num,
		# num -> letter, etc.)
		splitting = self.splitting

		# Make a list (dispos, for "dispossessed") of (startchar, endchar)
		# pairs for runs of text between "'s"
		if "'" in string:
			# Split on possessive 's
			dispos = []
			prev = 0
			for match in self.possessive.finditer(string):
				dispos.append((prev, match.start()))
				prev = match.end()
				if prev < len(string):
					dispos.append((prev, len(string)))
		else:
			# Shortcut if there's no apostrophe in the string
			dispos = ((0, len(string)),)

		# For each run between 's
		for sc, ec in dispos:
			# Split on boundary characters
			for part_match in self.between.finditer(string, sc, ec):
				part_start = part_match.start()
				part_end = part_match.end()

				if splitting:
					# The point to start splitting at
					prev = part_start
					# Find transitions (e.g. "iW" or "a0")
					bmatches=[]
					match_start=part_start
					match_end=part_end
					bmatch=bound.search(string,match_start,match_end)
					while bmatch:
						bmatches.append(bmatch)
						match_start=bmatch.start() + 1
						bmatch=bound.search(string,match_start,match_end)

					#for bmatch in bound.finditer(string, part_start, part_end):
					for bmatch in bmatches:
						# The point in the middle of the transition
						pivot = bmatch.start() + 1
						# Yield from the previous match to the transition
						yield (prev, pivot)
						# Make the transition the new starting point
						prev = pivot

					# If there's leftover text at the end, yield it too
					if prev < part_end:
						yield (prev, part_end)
				else:
					# Not splitting on transitions, just yield the part
					yield (part_start, part_end)

	def _merge(self, parts):
		mergewords = self.mergewords
		mergenums = self.mergenums

		# Current type (1=alpah, 2=digit)
		last = 0
		# Where to insert a merged term in the original list
		insertat = 0
		# Buffer for parts to merge
		buf = []
		# Iterate on a copy of the parts list so we can modify the original as
		# we go

		def insert_item(buf, at, newpos):
			newtext = "".join(item[0] for item in buf)
			newsc = buf[0][2]  # start char of first item in buffer
			newec = buf[-1][3]  # end char of last item in buffer
			parts.insert(insertat, (newtext, newpos, newsc, newec))

		for item in list(parts):
			# item = (text, pos, startchar, endchar)
			text = item[0]
			pos = item[1]

			# Set the type of this part
			if text.isalpha():
				this = 1
			elif text.isdigit():
				this = 2
			else:
				this = None

			# Is this the same type as the previous part?
			if (buf and (this == last == 1 and mergewords)
				or (this == last == 2 and mergenums)):
				# This part is the same type as the previous. Add it to the
				# buffer of parts to merge.
				buf.append(item)
			else:
				# This part is different than the previous.
				if len(buf) > 1:
					# If the buffer has at least two parts in it, merge them
					# and add them to the original list of parts.
					insert_item(buf, insertat, pos - 1)
					#insert_item(buf, insertat, pos)
					insertat += 1
				# Reset the buffer
				buf = [item]
				last = this
			insertat += 1

		# If there are parts left in the buffer at the end, merge them and add
		# them to the original list.
		if len(buf) > 1:
			insert_item(buf, len(parts), pos)

	def __call__(self, tokens):
		mergewords = self.mergewords
		mergenums = self.mergenums

		# This filter renumbers tokens as it expands them. New position
		# counter.
		newpos = None
		for t in tokens:
			text = t.text

			# If this is the first token we've seen, use it to set the new
			# position counter
			if newpos is None:
				if t.positions:
					newpos = t.pos
				else:
					# Token doesn't have positions, just use 0
					newpos = 0
			if ((text.isalpha() and (text.islower() or text.isupper()))
				or text.isdigit()):
				# Short-circuit the common cases of no delimiters, no case
				# transitions, only digits, etc.
				t.pos = newpos
				yield t
				newpos += 1
			else:
				# Split the token text on delimiters, word and/or number
				# boundaries into a list of (text, pos, startchar, endchar)
				# tuples
				ranges = self._split(text)
				parts = [(text[sc:ec], i + newpos, sc, ec)
						 for i, (sc, ec) in enumerate(ranges)]
                                #parts = [(text[sc:ec], newpos, sc, ec)
                                                 #for i, (sc, ec) in enumerate(ranges)]
				# Did the split yield more than one part?
				if len(parts) > 1:
					# If the options are set, merge consecutive runs of all-
					# letters and/or all-numbers.
					if mergewords or mergenums:
						self._merge(parts)

				# Yield tokens for the parts
				chars = t.chars
				if chars:
					base = t.startchar
				for text, pos, startchar, endchar in parts:
					t.text = text
					t.pos = pos
					if t.chars:
						t.startchar = base + startchar
						t.endchar = base + endchar
					yield t
				if parts:
					# Set the new position counter based on the last part
					newpos = parts[-1][1] + 1

class BioPassFilter(Filter):
	def __call__(self,tokens):
		newpos=0
		for t in tokens:
			text=t.text
			for p in string.punctuation:
				text=text.replace(p,' ')
			for x in text.split():
				t.text=x
				if t.positions:
					yield t
				else:
					t.pos=newpos
					yield t
			newpos+=1

def AnalyzerForIndex(stopset=stopwords):
	#return SpaceSeparatedTokenizer()|StripFilter()|StopFilter(frozenset(stopwords),minsize=1,renumber=True)|CharsetFilter(unicode2ascii)|TeeFilter(BioIntraWordFilter(mergenums=False,mergewords=True),BioIntraWordFilter(mergenums=False,mergewords=False)|ShingleFilter(2,sep=''),BioPassFilter())|LowercaseFilter()
	#return SpaceSeparatedTokenizer()|StripFilter()|StopFilter(frozenset(stopwords),minsize=1,renumber=True)|CharsetFilter(unicode2ascii)|BioIntraWordFilter(mergenums=False,mergewords=True)|LowercaseFilter()
	return SpaceSeparatedTokenizer()|StripFilter()|StopFilter(frozenset(stopwords),minsize=1,renumber=True)|CharsetFilter(unicode2ascii)|BioIntraWordFilter(delims=u"-'\"()!&;:,.?",mergenums=False,mergewords=True)|LowercaseFilter()

def AnalyzerForNLP(stopset=stopwords):
	#return SpaceSeparatedTokenizer()|StripFilter()|CharsetFilter(unicode2ascii)|BioIntraWordFilter(mergenums=False,mergewords=False)|LowercaseFilter()
	return SpaceSeparatedTokenizer()|StripFilter()|CharsetFilter(unicode2ascii)|LowercaseFilter()
def AnalyzerForAnalysis(stopset=stopwords):
	return SpaceSeparatedTokenizer()|StripFilter()|CharsetFilter(unicode2ascii)|BioIntraWordFilter(mergenums=False,mergewords=False)|LowercaseFilter()

def AnalyzerForSplit():
        return SpaceSeparatedTokenizer()|StripFilter()|CharsetFilter(unicode2ascii)|BioIntraWordFilter(splitnums=False,splitwords=False)|LowercaseFilter()


#network analysis and mining based on igraph,networkx,etc.
'''
from igraph import *
from jgraph import *
from collections import OrderedDict
import neo4j

def search_relation(part,num,left):
	lock=Lock()
	connection=neo4j.connect(dsn)
	cursor=connection.cursor()
	relation_list=[]
	relation_index_set=set()
	for x in part:
	#if isinstance(part,str) or isinstance(part,int):
		#x=part
		statement='MATCH ()-[r]->() WHERE id(r)=%s RETURN\
			id(r),type(r),r,\
			id(startNode(r)),labels(startNode(r)),startNode(r),\
			id(endNode(r)),labels(endNode(r)),endNode(r)' % x
		result=cursor.execute(statement)

		for relation_index,relation_type,relation_attrs,start_node_index,start_node_labels,start_node_attrs,end_node_index,end_node_labels,end_node_attrs in result:
			if relation_index in relation_index_set:
				continue
			start_node_labels=':'.join(start_node_labels)
			end_node_labels=':'.join(end_node_labels)
			start_node_attrs.update({'labels':start_node_labels})
                        end_node_attrs.update({'labels':end_node_labels})

			start_node=Node(start_node_labels,**start_node_attrs)
			start_node.set_index(start_node_index)
			end_node=Node(end_node_labels,**end_node_attrs)
			end_node.set_index(end_node_index)
			relation=Relation(*(start_node,relation_type,end_node),**relation_attrs)
			relation.set_index(relation_index)
			relation_list.append(relation)
			relation_index_set.add(relation_index)
	
	lock.acquire()
        print 'Match Part',str(num)
        print 'Match Number',str(len(part))
        print 'Match Left',str(left)
        print 'Done!'
	print
        lock.release()
	connection.close()
	return relation_list
	#return relation
#use cypher statements to manuplate neo4jdb-backend network graph data
class Node:
	def __init__(self,*labels,**attrs):
		self.labels=labels
		self.attrs=attrs
		self.attrs.update({'labels':self.labels})
		self.index=None
		try:
			self.id=self.attrs['id']
		except:
			raise Exception('No Identifier Defined For Given Node!')

	def set_index(self,index):
		self.index=index
	@property
	def labels(self):
		return self.labels
	@property
	def id(self):
		return self.id
	@property
	def attrs(self):
		return self.attrs
class Relation:
	def __init__(self,*triple,**attrs):
		try:
			self.start_node,self.relation_type,self.end_node=triple
		except:
			raise Exception('Relation Length Must Be Three With Double Nodes And A Tagged Relation Type!')
		try:
			self.id=attrs['id']
		except:
			raise Exception('No Identifier Defined For Given Relation!')
		self.attrs=attrs
		self.attrs.update({'relation_type':self.relation_type,'from':self.start_node.id,'to':self.end_node.id})
		self.index=None
		if attrs.has_key('bidirectional'):
			self.bidirectional=attrs['bidirectional']
		else:
			self.bidirectional=True
	def set_index(self,index):
		self.index=index
	@property
	def start_node(self):
		return self.start_node
	@property
	def end_node(self):
		return self.end_node
	@property
	def relation_type(self):
		return self.relation_type
	@property
	def id(self):
		return self.id
	@property
	def attrs(self):
		return self.attrs
	@property
	def bidirectional(self):
		return self.bidirectional
class Neo4jConnection(neo4j.connection.Connection):
	def __init__(self,dsn=dsn):
		super(Neo4jConnection,self).__init__(dsn)
		self.cursor=self.cursor()
		self.dsn=dsn
	#return the number of nodes in graph db
	@property
	def order(self):
		statement='MATCH (n) RETURN count(n)'
		result=self.cursor.execute(statement).next()[0]
		return result

	#return the number of relations in graph db
	@property
	def size(self):
		statement='MATCH ()-[r]->() RETURN count(r)'
		result=self.cursor.execute(statement).next()[0]
		return result
	#to delete target
	def delete_one_node(self,node):
		statement="MATCH (n) WHERE id(n)=%s DELETE n " % node.index
		self.cursor.execute(statement)
		return node

	def delete_nodes(self,*node):
		for node in nodes:
			yield self.delete_one_node(node)

	def delete_one_relation(self,relation):
		statement="MATCH ()-[r]->() WHERE id(r)=%s DELETE r" % relation.index
		self.cursor.execute(statement)
		return relation

	def delete_relations(self,*relations):
		for relation in relations:
			yield self.delete_relation(relation)

	def delete_all(self):
		print 'Warning: All Nodes And Relations Will Be Permanently Removed!'
		print 'Deleting All Edges...'
		statement='MATCH ()-[r]->() DELETE r'
		self.cursor.execute(statement)
		print 'Deleting All Nodes...'
		statement='MATCH (n) DELETE n'
		self.cursor.execute(statement)
		print 'Done!'
		print

	def create_one_node(self,node):
		if not isinstance(node,Node):
			raise Exception('Invalid Parameter! Node Type Essential!')
		labels=':'.join(node.labels)
		attrs={'node':node.attrs}
		statement="CREATE (n:%s {node}) RETURN id(n),labels(n),n" % labels
		node_index,node_labels,node_attrs=self.cursor.execute(statement,**attrs).next()
		node.set_index(node_index)
		return node

	def create_nodes(self,*nodes):
		for node in nodes:
			yield self.create_one_node(node)

	def merge_one_node(self,node):
		if not isinstance(node,Node):
			raise Exception('Invalid Parameter! Node Type Essential!')
		labels=':'.join(node.labels)
		attrs={'node':node.attrs}
		statement="MERGE (n:%s {%s}) RETURN id(n),labels(n),n" % (labels,','.join(map(lambda x:x[0]+':{'+attrs.keys()[0]+'}.'+x[0],node.attrs.items())))
		node_index,node_labels,node_attrs=self.cursor.execute(statement,**attrs).next()
		node.set_index(node_index)
		return node

	def merge_nodes(self,*nodes):
		for node in nodes:
			yield self.merge_one_node(node)

	def _create_one_relation(self,relation,unique=False):
		if not isinstance(relation,Relation):
			raise Exception('Invalid Parameter! Node Type Essential!')
		start_node,end_node,relation_type,is_bidirectional=relation.start_node,relation.end_node,relation.relation_type,relation.bidirectional
		start_node_labels,end_node_labels=map(lambda x:':'.join(x.labels),[start_node,end_node])
		start_node_index,end_node_index=start_node.index,end_node.index
		relation_attrs={'relation':relation.attrs}
		statement='MATCH (start_node:%s),(end_node:%s) WHERE id(start_node)=%s AND id(end_node)=%s' % (start_node_labels,end_node_labels,start_node_index,end_node_index)
		if unique:
			statement+=' CREATE UNIQUE'
		else:
			statement+=' CREATE'
		statement+=' (start_node)-[r:%s {relation}]->(end_node)' % relation_type
		statement+=' RETURN id(r),type(r),r'
		relation_index,relation_type,relation_attrs=self.cursor.execute(statement, **relation_attrs).next()
		relation.set_index(relation_index)
		return relation

	def create_one_relation(self,relation):
		return self._create_one_relation(relation)

	def create_unique_one_relation(self,relation):
		return self._create_one_relation(relation,unique=True)

	def create_relations(self,*relations):
		for relation in relations:
			yield self.create_one_relation(relation)

	def create_unique_relations(self,*relations):
		for relation in relations:
			yield self.create_unique_one_relation(relation)

	def add_index(self,label,*attrs):
		if not label:
			raise Exception('Empty Labels Invalid')
		for attr in attrs:
			statement='CREATE INDEX ON :%s(%s)' % (label,attr)
			result=self.cursor.execute(statement)

	#to find target nodes
	def find(self,*labels,**attrs):
		if not labels:
			raise Exception('Empty Labels Invalid!')
		labels=':'.join(labels)
		if attrs:
			node_attrs={'node':attrs}
			statement='MATCH (node:%s {%s})' % (labels,','.join(map(lambda x:x[0]+':{'+node_attrs.keys()[0]+'}.'+x[0],attrs.items())))
			statement+=' RETURN id(node),labels(node),node'
			result=self.cursor.execute(statement,**node_attrs)
		else:
			statement='MATCH (node:%s)' % labels
			statement+=' RETURN id(node),labels(node),node'
			result=self.cursor.execute(statement)
		return_value=[]
		for node_index,node_labels,node_attrs in result:
			node=Node(*node_labels,**node_attrs)
			node.set_index(node_index)
			return_value.append(node)
		return return_value

	#to find target node
	def find_one(self,*labels,**attrs):
		return self.find(*labels,**attrs)[0]

	#to match target relations
	#return_type:
	#	'relation': Relation class type
	#	'graph': Graph class type in igraph module
	def match(self,start_node,labels=None,rel_type=None,min_step=1,max_step=2,searches=None,**attrs):
		if start_node and isinstance(start_node,str):
			start_node=self.find_one(start_node.split('~')[0],id=start_node)
		elif start_node and isinstance(start_node,Node):
			pass
	
		relation_attrs={'relation':attrs}
		if labels:
			if isinstance(labels,list) or isinstance(labels,tuple):
				labels=map(lambda x:'"'+x+'"',sorted(labels))
				statement_pattern='MATCH (start_node), (end_node) WHERE id(start_node)=%s AND end_node.ontology IN ['+','.join(labels)+']'
			else:
				raise Exception('Wrong Starting Labels Defined!') 
		else:
			statement_pattern='MATCH (start_node), (end_node) WHERE id(start_node)=%s'
		rel_clause=''
		if rel_type:
			rel_clause+=':'+rel_type
		if attrs:
			rel_clause+=' {%s}' % ','.join(map(lambda x:x[0]+':{'+relation_attrs.keys()[0]+'}.'+x[0],attrs.items()))
		statement_pattern+=' MATCH (start_node)-[relation'+rel_clause+']-(end_node)'

		statement_pattern+=' WHERE'
		#searche:(attr_name,attr_lookup,attr_query) tuple list
		if searches:
			query_list=[]
			
			for search in searches:
				attr_name,attr_lookup,attr_query=search
				if isinstance(attr_query,str):
					attr_query='"'+attr_query+'"'
				else:
					pass
				if attr_lookup=='gt':
					if attr_name=='depth':
						query_list.append(' (relation.%s > %s OR relation.depth = -1)' % tuple([attr_name,attr_query]))
					#else:
						#query_list.append(' relation.%s > %s' % tuple([attr_name,attr_query]))
					elif attr_name.startswith('doc_num') or attr_name.startswith('sent_num'):
						query_list.append(' (relation.%s > %s OR relation.%s = -1)' % tuple([attr_name,attr_query,attr_name]))
					else:
						query_list.append(' relation.%s > %s' % tuple([attr_name,attr_query]))
				elif attr_lookup=='gte':
					if attr_name=='depth':
						query_list.append(' (relation.%s >= %s OR relation.depth = -1)' % tuple([attr_name,attr_query]))
					#else:
						#query_list.append(' relation.%s >= %s' % tuple([attr_name,attr_query]))
					elif attr_name.startswith('doc_num') or attr_name.startswith('sent_num'):
                                                query_list.append(' (relation.%s >= %s OR relation.%s = -1)' % tuple([attr_name,attr_query,attr_name]))
                                        else:
                                                query_list.append(' relation.%s >= %s' % tuple([attr_name,attr_query]))

				elif attr_lookup=='eq':
					if attr_name=='depth':
                                                query_list.append(' (relation.%s = %s OR relation.depth = -1)' % tuple([attr_name,attr_query]))
                                        #else:
                                                #query_list.append(' relation.%s = %s' % tuple([attr_name,attr_query]))
					elif attr_name.startswith('doc_num') or attr_name.startswith('sent_num'):
                                                query_list.append(' (relation.%s = %s OR relation.%s = -1)' % tuple([attr_name,attr_query,attr_name]))
                                        else:
                                                query_list.append(' relation.%s = %s' % tuple([attr_name,attr_query]))

				elif attr_lookup=='lt':
                                        if attr_name=='depth':
                                                query_list.append(' (relation.%s < %s OR relation.depth = -1)' % tuple([attr_name,attr_query]))
                                        #else:
                                                #query_list.append(' relation.%s < %s' % tuple([attr_name,attr_query]))
					elif attr_name.startswith('doc_num') or attr_name.startswith('sent_num'):
                                                query_list.append(' (relation.%s < %s OR relation.%s = -1)' % tuple([attr_name,attr_query,attr_name]))
                                        else:
                                                query_list.append(' relation.%s < %s' % tuple([attr_name,attr_query]))

				elif attr_lookup=='lte':
                                        if attr_name=='depth':
                                                query_list.append(' (relation.%s <= %s OR relation.depth = -1)' % tuple([attr_name,attr_query]))
                                        #else:
                                                #query_list.append(' relation.%s <= %s' % tuple([attr_name,attr_query]))
					elif attr_name.startswith('doc_num') or attr_name.startswith('sent_num'):
                                                query_list.append(' (relation.%s <= %s OR relation.%s = -1)' % tuple([attr_name,attr_query,attr_name]))
                                        else:
                                                query_list.append(' relation.%s <= %s' % tuple([attr_name,attr_query]))

				elif attr_lookup=='neq':
					if attr_name=='depth':
                                                query_list.append(' (relation.%s != %s OR relation.depth = -1)' % tuple([attr_name,attr_query]))
                                        #else:
                                                #query_list.append(' relation.%s != %s' % tuple([attr_name,attr_query]))
					elif attr_name.startswith('doc_num') or attr_name.startswith('sent_num'):
                                                query_list.append(' (relation.%s != %s OR relation.%s = -1)' % tuple([attr_name,attr_query,attr_name]))
                                        else:
                                                query_list.append(' relation.%s != %s' % tuple([attr_name,attr_query]))

			query=' AND '.join(query_list)
			statement_pattern+=query
		#rel_clause+='*%s..%s '%(min_step,max_step)
		statement_pattern+=' RETURN DISTINCT id(relation),id(end_node)'
		start_node_set=set()
		start_node_set.add(start_node.index)
		node_set=set()
		node_set.add(start_node.index)
		relation_set=set()
		step=min_step
		temp=1000
		while step<=max_step:
			print 'Step',str(step)
			new_start_node_set=set()
			for n in start_node_set:
				statement=statement_pattern % n
				print statement
				result=self.cursor.execute(statement,**relation_attrs)
				for relation_id,node_id in result:
					relation_set.add(relation_id)
					new_start_node_set.add(node_id)
					if len(relation_set)%temp==0:
						print 'Relation Number',str(len(relation_set))
					if len(new_start_node_set)%temp==0:
						print 'Node Number',str(len(new_start_node_set))
			start_node_set=new_start_node_set-node_set
			node_set|=new_start_node_set
			step+=1
		print 'Done!'
		relation_id_list=sorted(relation_set)
		#proc_num=cpu_count()
		proc_num=120
		length=len(relation_id_list)

		#increment=int(length/proc_num)+1
		increment=500
		parts=[]
		for i in xrange(0,length,increment):
			if i+increment<=length:
				parts.append(relation_id_list[i:i+increment])
			else:
				parts.append(relation_id_list[i:])
		pool=Pool(processes=cpu_count(),maxtasksperchild=child_num)
		#parts=relation_id_list
		left=length
		num=0
		results=[]
		for x in parts:
			num+=1
			left-=len(x)
			#left-=1
			results.append(pool.apply_async(search_relation,args=(x,num,left,)))
			#results.append(search_relation(x,num,left))
		pool.close()
		pool.join()

		relation_list=[]
		relation_dict={}
		for x in results:
			relation_list.extend(x.get())
			#relation_list.append(x.get())
		relation_dict.update(dict(zip(map(lambda x:x.attrs['id'],relation_list),relation_list)))
		relation_list=sorted(relation_dict.values(),key=lambda x:x.attrs['id'])
		#relation_list=results
		print 'All Done!'
		print 'Return'
		return relation_list
	
	#to match target relation
		def match_one(self,start_node=None,rel_type=None,end_node=None,**attrs):
				return self.match(start_node=start_node,rel_type=rel_type,end_node=end_node,**attrs)[0]

#create igraph Graph object based on cooccurrence graph
#params:
#centric_vertex: vertex id
#onts:ontology name list
#path_limit: adjacency path limit
#start_year: network data since which year
#end_year: network data til which year
#directed: if the graph is directed or undirected and default undirected
#intra_relation: whether directed intra relations for a given ontology included
def load_graph(centric_vertex_id,onts=('caloha','do','go','pathway','proteingene','symp'),min_step=1,max_step=2,start_year=2000,end_year=2014,intra_relation=True,intra_cooccurrence=True,*searches):
	start_year=str(start_year)
	end_year=str(end_year)
	year='-'.join([start_year,end_year])
	year_tag='_'.join(['tag',start_year,end_year])
	ont_names=sorted(onts)
	ont_pairs=list({tuple(sorted(x)) for x in itertools.product(ont_names,ont_names) if x[0]!=x[1]})
	if intra_relation or intra_cooccurrence:
		ont_pairs.extend([tuple([x]*2) for x in ont_names])
	print 'Ontologies:',' '.join(ont_names)
	print 'Year:','-'.join([start_year,end_year])
	print 'Step limit:','-'.join(map(str,[min_step,max_step]))
	print 'Intra relations:',intra_relation and 'Included' or 'Excluded'
	print 'Intra cooccurrence:',intra_cooccurrence and 'Included' or 'Excluded'
	graphdb=Neo4jConnection()
	if not centric_vertex_id:
		raise Exception('Centric vertex not selected!')

	print 'Importing vertices and edges...'
	start_label=centric_vertex_id.split('~')[0]
	end_label=[x for x in ont_names if x!=start_label]
	centric_vertex=graphdb.find_one(start_label,id=centric_vertex_id)
	if not centric_vertex:
		raise Exception('Centric Vertex excluded in the network!')
	print 'Extracting network and Creating graph'
	if intra_relation and intra_cooccurrence:
		relation_list=graphdb.match(
			start_node=centric_vertex,
			labels=ont_names,
			min_step=min_step,
			max_step=max_step,
			*searches,
			**{year_tag:True}
		)
	elif intra_relation:
		relation_list=graphdb.match(
			start_node=centric_vertex,
			labels=ont_names,
			min_step=min_step,
			max_step=max_step,
			*searches,
			**{intra_cooccurrence:False,
			year_tag:True}
		)
	elif intra_cooccurrence:
		relation_list=graphdb.match(
			start_node=centric_vertex,
			labels=ont_names,
			min_step=min_step,
			max_step=max_step,
			*searches,
			**{intra_relation:False,
			year_tag:True}
		)
	else:
		relation_list=graphdb.match(
			start_node=centric_vertex,
			labels=ont_names,
			min_step=min_step,
			max_step=max_step,
			*searches,
			**{intra_relation:False,
			intra_cooccurrence:False,
			year_tag:True}
		)
	node_list=set()
	node_id_list=set()
	relation_id_list=set()
	relation_list=set()
	for relation in relation_list:
		start_node=relation.start_node
		end_node=relation.end_node
		if start_node.id in node_id_list:
			pass
		else:
			node_list.add(start_node)
			node_id_list.add(start_node.id)
		if end_node.id in node_id_list:
			pass
		else:
			node_list.add(end_node)
			node_id_list.add(end_node.id)
		if relation.id in relation_id_list:
			pass
		else:
			relation_list.add(relation)
			relation_id_list.add(relation.id)
	node_id_list=sorted(node_id_list)
	node_list=sorted(node_list,key=lambda x:x.id)
	relation_id_list=sorted(relation_id_list)
	relation_list=sorted(relation_list,key=lambda x:x.id)

	graph=Graph()
	graph.add_vertices(len(node_id_list))
	for k in node_list[0].keys():
		graph.vs[k]=map(lambda x:x[k],node_list)
	graph.add_edges(map(lambda x:(node_id_list.index(x.split(',')[0]),node_id_list.index(x.split(',')[1])),relation_id_list))
	for k in relation_list[0].keys():
		graph.es[k]=map(lambda x:x[k],relation_list)
	graph['ontologies']=','.join(ont_names)
	graph['p_cutoff']=p_cutoff
	graph['npmi_cutoff']=npmi_cutoff
	graph['cooccurrence_cutoff']=cooccurrence_cutoff
	graph['intra_relation']='included' if intra_relation else 'excluded'
	graph['intra_cooccurrence']='included' if intra_cooccurrence else 'excluded'
	graph['year']=year
	print 'Total Vertices Number',str(graph.vcount())
	print 'Total Edges Number',str(graph.ecount())
	print 'Done!'
	print

	return graph

#calculate clustering coefficient for a given graph
def clustering_coefficient(graph):
	return graph.transitivity_undirected()

#get all the connected components
def connected_components(graph):
	return sorted([graph.subgraph(x) for x in graph.clusters()],key=lambda x:x.vcount(),reverse=True)

#get parameters for a given graph
#http://med.bioinf.mpi-inf.mpg.de/netanalyzer/help/2.7/#refDong
def get_parameters(graph,directed=False,unconn=True):
	param_dict=OrderedDict()
	#number of connected components
	#indicate the connectivity of network and a lower number of connected components suggests a stronger connectivity
	param_dict['connected_componet_number']=len(graph.clusters())
	#parameters related to shortest paths
	#network diameter, network radius, average shortest path length
	param_dict['diameter']=graph.diameter()
	param_dict['radius']=graph.radius()
	param_dict['average_shortest_path_length']=mean(map(lambda x:len(x),graph.shortest_paths()))
	#parameters related to neighborhood
	#average number of neighbors, network density, number of isolated nodes, network centralization, network heterogeneity, number of multi-edge node pairs
	param_dict['average_neighbor_number']=mean(map(lambda x:len(x),graph.neighborhood()))
	param_dict['density']=graph.density()
	param_dict['isolated_node_number']=len(graph.vs.select(_degree_eq=0))
	param_dict['centralization']=graph.vcount()/(graph.vcount()-2)*(max(map(lambda x:len(x),graph.neighborhood()))/(graph.vcount()-1)-graph.density())
	param_dict['heterogeneity']=cmath.sqrt(variance(map(lambda x:len(x),graph.neighborhood()))).real/mean(map(lambda x:len(x),graph.neighborhood()))
	#param_dict['multiple_edge_node_pair_number']=len(list(set([sorted((x['from'],x['to'])) for x in graph.es if graph.is_multiple(x)])))
	#clustering coefficient
	#a measure of the degree to which nodes in a graph tend to cluster together
	param_dict['clustering_coefficient']=clustering_coefficient(graph)
	return param_dict



#analyze the stress centrality for a given graph
#stress centrality of a node is the number of shortest paths passing through
def stress_centrality(graph):
	if isinstance(graph,Graph):
		pass
	else:
		raise Exception('Error: Invalid input graph!')
	paths={}
	vertex_pairs=list(itertools.combinations([x.index for x in graph.vs],2))
	for p in vertex_pairs:
		source,target=p
		paths[p]=graph.get_shortest_paths(source,to=graph.vs.select(lambda x:x.index==target))

	centrality_dict={}
	centrality_dict=centrality_dict.fromkeys([x.index for x in graph.vs],0)
	for v in paths.values():
		for x in v:
			centrality_dict[x]+=1

	score_list=sorted([(graph.vs[x[0]],x[1]) for x in centrality_dict.items()],key=lambda x:x[1],reverse=True)
	return score_list

#analyze the radiality centrality for a given graph
#the radiality is defined as sum(d_G + 1 - d(v, w))/(n - 1). where d(w, v) is the length of the shortest path from node w to node v, d_G is the diameter of the network, n is the size of the network.
def radiality_centrality(graph):
	if isinstance(graph,Graph):
		pass
	else:
		raise Exception('Error: Invalid input graph!')

	diameter=graph.diameter()
	size=graph.vcount()
	score_dict={}
	for v in graph.vs:
		score_dict[v]=sum(map(lambda x:graph.shortest_paths(source=v.index,target=x.index)[0][0]==float('Inf') and diameter+1 or diameter+1-graph.shortest_paths(source=v.index,target=x.index)[0][0]/(size-1),graph.vs))
	score_list=sorted(centrality_dict.items(),key=lambda x:x[1],reverse=True)

#analyze the centroid centrality for a given graph
#http://www.cbmc.it/~scardonig/centiscape/CentiScaPefiles/CentralitiesTutorial.pdf
def centroid_centrality(graph):
	pathm=np.array([])
	adjm=graph.get_adjacency().data
	for v1 in xrange(0,graph.vcount()):
		temp=[]
		for v2 in xrange(0,len(graph,vs)):
			if adjm[i][j]>0:
				temp.append(graph.shortest_paths(source=v1,target=v2)[0][0])
			else:
				temp.append(0)
		pathm=np.append(pathm,temp)

	fm=np.zeros((graph.vcount(),graph.vcount()))
	for v1 in xrange(0,graph.vcount()):
		for v2 in xrange(0,graph.vcount()):
			fm[v1][v2]=len(filter(lambda x:x[0]<x[1],zip(pathm[v1],pathm[v2])))-len(filter(lambda x:x[0]>x[1],zip(pathm[v1],pathm[v2])))

	score_dict={}
	for v in graph.vs:
		score_dict[v]=min(fm[v.index])

	return sorted(score_dict.items(),key=lambda x:x[1],reverse=True)

#analyze the eccentricity centrality for a given graph
def eccentricity_centrality(graph):
	score_list=graph.eccentricity()
	return sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)

#analyze the centrality for a given graph
#centrality measurements included:
#	degree centrality
def degree_centrality(graph):
	score_list=graph.degree()
	return sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
#	betweenness centrality
def betweenness_centrality(graph):
	score_list=graph.betweenness()
	return sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
#	closeness centrality
def closeness_centrality(graph):
	score_list=graph.closeness()
	return sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
#	eigenvector centrality
def eigenvector_centrality(graph):
	score_list=graph.evcent()
	return sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
#	pagerank centrality
def pagerank_centrality(graph):
	score_list=graph.pagerank()
	return sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
#analyze the centrality for a given graph
def analyze_centrality(graph):
	centrality_dict=OrderedDict()

	print 'Analyzing degree centrality...'
	score_list=graph.degree()
	centrality_dict['degree']=sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
	print 'Done!'
	print

	print 'Analyzing betweenness centrality...'
	score_list=graph.betweenness()
	centrality_dict['betweenness']=sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
	print 'Done!'
	print

	print 'Analyzing  closeness centrality...'
	score_list=graph.closeness()
	centrality_dict['closeness']=sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
	print 'Done!'
	print

	print 'Analyzing eigenvector centrality...'
	score_list=graph.evcent()
	centrality_dict['eigenvector']=sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
	print 'Done!'
	print

	print 'Analyzing pagerank centrality...'
	score_list=graph.pagerank()
	centrality_dict['pagerank']=sorted([(graph.vs[i],score_list[i]) for i in xrange(0,len(score_list))],key=lambda x:x[1],reverse=True)
	print 'Done!'
	print

	return centrality_dict

#find the hubs for a given graph based on Kleinberg's hub score
def find_hubs(graph):
	return sorted([(graph.vs[i],graph.hub_score()[i]) for i in xrange(0,len(graph.hub_score()))],key=lambda x:x[1],reverse=True)

#find the authorities for a given graph based on Kleinberg's authority score
def find_authorities(graph):
	return sorted([(graph.vs[i],graph.authority_score()[i]) for i in xrange(0,len(graph.authority_score()))],key=lambda x:x[1],reverse=True)

#find all the cliques of graph sorted by the number of vertices in each clique
#a clique is a complete subgraph that is a set of vertices where an edge is present between all two of then excluding loops
def find_cliques(graph):
	return sorted([graph.subgraph(x) for x in graph.cliques()],key=lambda x:x.vcount(),reverse=True)

#find all the strong or weak clusters (or connected components) for a given graph
#mode: STRONG or WEAK and default STRONG
def find_clusters(graph,mode=STRONG):
	return sorted([graph.subgraph(x) for x in graph.clusters()],key=lambda x:x.vcount(),reverse=True)

#find decomposed subgraphs for a given graph
#mode: STRONG or WEAK and default STRONG
def find_subgraphs(graph,mode=STRONG):
	#for x in sorted([(map(lambda y:y['id'],x.vs),map(lambda y:(y['from'],y['to']),x.es)) for x in graph.decompose()],key=lambda x:len(x.vs),reverse=True):
	return sorted(graph.decompose(),key=lambda x:x.vcount(),reverse=True)

#find ego networks or subnetworks centered on given vertices
#params:
#graph
#vertices: the list of id attributes for given vertices
#the implementation to use when constructing the new subgraph:
#'auto','copy_and_delete','create_from_scratch'
def find_egos(graph,vertices,implementation='auto'):
	if isinstance(vertices,list) or isinstance(vertices,VertexSeq):
		pass
	elif isinstance(vertices,int) or isinstance(vertices,str) or isinstance(vertices,Vertex):
		vertices=[vertices]
	else:
		raise Exception('Parameter Error!')

	if all(map(lambda x:isinstance(x,int),vertices)):
		try:
			vertices=map(lambda x:graph.vs[x],vertices)
		except:
			print 'Vertex index integer error!'
			print
	elif all(map(lambda x:isinstance(x,str),vertices)):
		try:
			vertices=map(lambda x:graph.vs.select(id_eq=x)[0],vertices)
		except:
			print 'Vertex ID error!'
			print
	elif all(map(lambda x:isinstance(x,Vertex),vertices)) or isinstance(vertices,VertexSeq):
		pass
	else:
		raise Exception('Parameter Error!')
	#for x in sorted([(map(lambda y:y['id'],x.vs),map(lambda y:(y['from'],y['to']),x.es)) for x in graph.subgraphs([graph.vs.select(id_eq=x) for x in vertices],implementation='auto')],key=lambda x:len(x.vs),reverse=True):
	return sorted([graph.subgraph(x,implementation='auto') for x in vertices],key=lambda x:x.vcount(),reverse=True)

#find clustered modules based on MCODE clustering algorithm
#similar to Cytoscaple MCODE plugin citing
#Bader, Gary D., and Christopher WV Hogue. "An automated method for finding molecular complexes in large protein interaction networks." BMC bioinformatics 4.1 (2003): 2.
#three stages:
#	stage 1: vertex weighting
#	stage 2: molecular complex prediction
#	stage 3: post-processing (optional)
def find_mcode_clusters(graph,vertex_weight_percentage,haircut_flag,fluff_flag,fluff_density_threshold):
	#stage 1: vertext weighting
	def mcode_vertex_weighting(graph):
		vertex_weights=OrderedDict()
		for v in graph.vs:
			neighbors=graph.neighborhood(v.index)
			subgraph=graph.subgraph(neighbors)
			k_core_max=max(subgraph.coreness())
			k_core_graph=subgraph.k_core(k_core_max)
			k=subgraph.coreness().count(k_core_max)
			d=k_core_graph.density()
			vertex_weights[v]=k*d
		return vertex_weights
	#stage 2: molecular complex prediction
	def mcode_find_complex(graph,vertex_weights,vertex_weight_percentage,seed_vertex,complex_list):
		if seed_vertex in complex_list:
			return list(set(complex_list))
		for v in graph.neighborhood(seed_vertex):
			v=graph.vs[v]
			if vertex_weights[v]>vertex_weights[seed_vertex]*(1-vertex_weight_percentage):
				complex_list.append(v)
				complex_list=mcode_find_complex(graph,vertex_weights,vertex_weight_percentage,v,complex_list)

		return list(set(complex_list))

	def mcode_find_complexes(graph,vertex_weights,vertex_weight_percentage):
		complex_set=[]
		for v in graph.vs:
			complex_set.append(graph.subgraph([x.index for x in mcode_find_complex(graph,vertex_weights,vertex_weight_percentage,v,[])]))

		return complex_set
	#stage 3: post-processing
	def mcode_fluff_complex(graph,vertex_weights,fluff_density_threshold,complex_graph):
		complex_graph.delete_vertices(filter(lambda u:vertex_weights[u]<fluff_density_threshold,complex_graph.vs))
		return complex_graph
	def mcode_post_process(graph,vertex_weights,haircut_flag,fluff_flag,fluff_density_threshold,set_of_predicted_complex_graphs):
		for c in list(set_of_predicted_complex_graphs):
			if min(c.coreness())<2:
				set_of_predicted_complex_graphs.remove(c)
			if haircut_flag is True and c in set_of_predicted_complex_graphs:
				set_of_predicted_complex_graphs[set_of_predicted_complex_graphs.index(c)]=c.k_core(2)
			if fluff_flag is True and c in set_of_predicted_complex_graphs:
				set_of_predicted_complex_graphs[set_of_predicted_complex_graphs.index(c)]=mcode_fluff_complex(graph,vertex_weights,fluff_density_threshold,c)
		print set_of_predicted_complex_graphs
		return set_of_predicted_complex_graphs
	#overall process
	vertex_weights=mcode_vertex_weighting(graph)
	set_of_predicted_complex_graphs=mcode_find_complexes(graph,vertex_weights,vertex_weight_percentage)
	return mcode_post_process(graph,vertex_weights,haircut_flag,fluff_flag,fluff_density_threshold,set_of_predicted_complex_graphs)


#perform network clustering based on MCL algorithm
#https://github.com/koteth/python_mcl
def mcl_clustering(G, expand_factor = 2, inflate_factor = 2, max_loop = 10 , mult_factor = 1):

	def normalize(A):
		column_sums = A.sum(axis=0)
		new_matrix = A / column_sums[np.newaxis, :]
		return new_matrix

	def inflate(A, inflate_factor):
		return normalize(np.power(A, inflate_factor))

	def expand(A, expand_factor):
		return np.linalg.matrix_power(A, expand_factor)

	def add_diag(A, mult_factor):
		return A + mult_factor * np.identity(A.shape[0])

	def get_clusters(A):
		clusters = []
		for i, r in enumerate((A>0).tolist()):
			if r[i]:
				clusters.append(A[i,:]>0)

		clust_map  ={}
		for cn , c in enumerate(clusters):
			for x in  [ i for i, x in enumerate(c) if x ]:
				clust_map[cn] = clust_map.get(cn, [])  + [x]
		return clust_map

	def stop(M, i):
		if i%5==4:
			m = np.max( M**2 - M) - np.min( M**2 - M)
			if m==0:
				return True

		return False

	def mcl(M, expand_factor = 2, inflate_factor = 2, max_loop = 10 , mult_factor = 1):
		M = add_diag(M, mult_factor)
		M = normalize(M)

		for i in range(max_loop):
			M = inflate(M, inflate_factor)
			M = expand(M, expand_factor)
			if stop(M, i): break

		clusters = [G.subgraph([y.index for y in x]) for x in get_clusters(M).values()]
		return clusters

	return mcl(np.array(G.get_adjacency().data), expand_factor, inflate_factor, max_loop, mult_factor)


def fastgreedy_community(graph):
	print 'Running fastgreedy community dectection algorithm...'
	return sorted([graph.subgraph(x) for x in graph.community_fastgreedy().as_clustering()],key=lambda x:x.vcount(),reverse=True)

def infomap_community(graph):
	print 'Running infomap community dectection algorithm...'
	return sorted([graph.subgraph(x) for x in graph.community_infomap()],key=lambda x:x.vcount(),reverse=True)

def leading_eigenverctor_community(graph):
	print 'Running leading_eigenverctor community dectection algorithm...'
	return sorted([graph.subgraph(x) for x in graph.community_leading_eigenvector()],key=lambda x:x.vcount(),reverse=True)

def label_propagation_community(graph):
	print 'Running label_propagation community dectection algorithm...'
	return sorted([graph.subgraph(x) for x in graph.community_label_propagation()],key=lambda x:x.vcount(),reverse=True)

def multilevel_community(graph):
	print 'Running multilevel community dectection algorithm...'
	return sorted([map(lambda y:graph.vs[y]['id'],x) for x in graph.community_multilevel()],key=lambda x:x.vcount(),reverse=True)

def edge_betweenness_community(graph):
	print 'Running edge_betweenness community dectection algorithm...'
	return sorted([graph.subgraph(x) for x in graph.community_edge_betweenness().as_clustering()],key=lambda x:x.vcount(),reverse=True)

def walktrap_community(graph):
	print 'Running walktrap community dectection algorithm...'
	return sorted([graph.subgraph(x) for x in graph.community_walktrap().as_clustering()],key=lambda x:x.vcount(),reverse=True)


#find communities based on various igraph community detection algorithms
#spinglass method not suitable to undirected graphs
#optimal_modularity method not feasible for larget networks
def find_communities(graph):
	community_dict=OrderedDict()

	print 'Running fastgreedy community dectection algorithm...'
	community_dict['fastgreedy']=fastgreedy_community(graph)
	print 'Done!'
	print

	print 'Running infomap community dectection algorithm...'
	community_dict['infomap']=infomap_community(graph)
	print 'Done!'
	print

	print 'Running leading_eigenverctor community dectection algorithm...'
	community_dict['leading_eigenverctor']=leading_eigenverctor_community(graph)
	print 'Done!'
	print

	print 'Running label_propagation community dectection algorithm...'
	community_dict['label_propagation']=label_propagation_community(graph)
	print 'Done!'
	print

	print 'Running multilevel community dectection algorithm...'
	community_dict['multilevel']=multilevel_community(graph)
	print 'Done!'
	print

	print 'Running edge_betweenness community dectection algorithm...'
	community_dict['edge_betweenness']=edge_betweenness_community(graph)
	print 'Done!'
	print

	print 'Running walktrap community dectection algorithm...'
	community_dict['walktrap']=walktrap_community(graph)
	print 'Done!'
	print

	return community_dict

#analyze vertex similarity for a given graph
#Zhou, XueZhong, et al. "Human symptoms-disease network." Nature communications 5 (2014).
def score_similarity(graph,vertices,score_method='npmi_score'):
	if isinstance(vertices,list) or isinstance(vertices,VertexSeq):
		pass
	elif isinstance(vertices,int) or isinstance(vertices,str) or isinstance(vertices,Vertex):
		vertices=[vertices]
	else:
		raise Exception('Parameter Error!')

	if all(map(lambda x:isinstance(x,int),vertices)):
		try:
			vertices=map(lambda x:graph.vs[x],vertices)
		except:
			print 'Vertex index integer error!'
			print
	elif all(map(lambda x:isinstance(x,str),vertices)):
		try:
			vertices=map(lambda x:graph.vs.select(id_eq=x)[0],vertices)
		except:
			print 'Vertex ID error!'
			print
	elif all(map(lambda x:isinstance(x,Vertex),vertices)) or isinstance(vertices,VertexSeq):
		pass
	else:
		raise Exception('Parameter Error!')
	if score_method=='npmi_score' or score_method=='p_value':
		pass
	else:
		raise Exception('Score Method Error!')
	year=graph['year']
	score_dict=OrderedDict()
	for vertex_1,vertex_2 in itertools.combinations(vertices,2):
		vector_1=[]
		for x in zip([vertex_1]*graph.vcount(),graph.vs):
			try:
				vector_1.append(graph.es[graph.get_eid(*x)]['_'.join([score_method,year])])
			except:
				vector_1.append(0.0)
		vector_2=[]
		for x in zip([vertex_2]*graph.vcount(),graph.vs):
			try:
				vector_2.append(graph.es[graph.get_eid(*x)]['_'.join([score_method,year])])
			except:
				vector_2.append(0.0)
		score_dict[tuple(sorted([vector_1,vector_2]))]=sum(map(lambda x:x[0]*x[1],zip(vector_1,vector_2)))/(cmath.sqrt(sum(map(lambda x:x**2,vector_1))).real*cmath.sqrt(sum(map(lambda x:x**2,vector_2))).real)
	return score_dict

#analyze vertex diversity for a given graph
#Zhou, XueZhong, et al. "Human symptoms-disease network." Nature communications 5 (2014).
#Liu, Lu, et al. "Mining diversity on networks." Database Systems for Advanced Applications. Springer Berlin Heidelberg, 2010.
def score_diversity(graph):
	return OrderedDict(zip(graph.vs,map(lambda x:sum([1-len(list(set(graph.neighborhood(x)) & set(graph.neighborhood(y))))/len(graph.neighborhood(y)) for y in graph.neighborhood(x)]),graph.vs)))

#find the most probable path between a pair of vertices for a given graph with length no more than 3
#Bell, Lindsey, et al. "Integrated bio-entity network: a system for biological knowledge discovery." PloS one 6.6 (2011): e21474.
def find_mpp(graph,vertices,score_method='npmi_score'):
	if isinstance(vertices,list) or isinstance(vertices,VertexSeq):
		pass
	elif isinstance(vertices,int) or isinstance(vertices,str) or isinstance(vertices,Vertex):
		vertices=[vertices]
	else:
		raise Exception('Parameter Error!')

	if all(map(lambda x:isinstance(x,int),vertices)):
		try:
			vertices=map(lambda x:graph.vs[x],vertices)
		except:
			print 'Vertex index integer error!'
			print
	elif all(map(lambda x:isinstance(x,str),vertices)):
		try:
			vertices=map(lambda x:graph.vs.select(id_eq=x)[0],vertices)
		except:
			print 'Vertex ID error!'
			print
	elif all(map(lambda x:isinstance(x,Vertex),vertices)) or isinstance(vertices,VertexSeq):
		pass
	else:
		raise Exception('Parameter Error!')
	if score_method=='npmi_score' or score_method=='p_value':
		pass
	else:
		raise Exception('Score Method Error!')
	year=graph['year']
	path_dict=OrderedDict()
	for vertex_1,vertex_2 in itertools.combinations(vertices,2):
		try:
			path_dict[tuple(sorted([vertex_1,vertex_2]))]=graph.get_shortest_paths(vertex_1,vertex_2,weights=map(lambda x:x['_'.join([score_method,year])],graph.es),mode=ALL)[0]
		except:
			path_dict[tuple(sorted([vertex_1,vertex_2]))]=[]

	return path_dict

#score Burt's constraint score which is the measurement of structural holes for a given graph
def score_constraint(graph):
	return OrderedDict(sorted(zip(graph.vs,graph.constraint(graph.vs)),key=lambda x:x[1]))

#analyze hidden relations from a start term for a given graph (open discovery)
#based on the linking terms between starting term and target term
#Yetisgen-Yildiz, Meliha, and Wanda Pratt. "A new evaluation methodology for literature-based discovery systems." Journal of biomedical informatics 42.4 (2009): 633-643.
def discover_open_hidden_relations(graph,start_terms,score_method='npmi_score'):
	if isinstance(start_terms,list) or isinstance(start_terms,VertexSeq):
		pass
	elif isinstance(start_terms,int) or isinstance(start_terms,str) or isinstance(start_terms,Vertex):
		start_terms=[start_terms]
	else:
		raise Exception('Parameter Error!')

	if all(map(lambda x:isinstance(x,int),start_terms)):
		try:
			start_terms=map(lambda x:graph.vs[x],start_terms)
		except:
			print 'Vertex index integer error!'
			print
	elif all(map(lambda x:isinstance(x,str),start_terms)):
		try:
			start_terms=map(lambda x:graph.vs.select(id_eq=x)[0],start_terms)
		except:
			print 'Vertex ID error!'
			print
	elif all(map(lambda x:isinstance(x,Vertex),start_terms)) or isinstance(start_terms,VertexSeq):
		pass
	else:
		raise Exception('Parameter Error!')
	if score_method=='npmi_score' or score_method=='p_value':
		pass
	else:
		raise Exception('Score Method Error!')
	year=graph['year']
	relation_dict=OrderedDict()
	for start_term in start_terms:
		target_terms=map(lambda x:graph.vs[x],set(graph.neighborhood(start_term,order=2))-set(graph.neighborhood(start_term)))
		relation_dict[start_term]=OrderedDict([(x[0],{'pivot_num':x[1],'awm_score':x[2]}) for x in sorted(zip(target_terms,map(lambda x:len(list(set(graph.neighborhood(x)) & set(graph.neighborhood(start_term)))),target_terms),map(lambda x:mean([min(graph.es[graph.get_eid(x,t)]['_'.join([score_method,year])],graph.es[graph.get_eid(t,start_term)]['_'.join([score_method,year])]) for t in map(lambda d:graph.vs[d],set(graph.neighborhood(x)) & set(graph.neighborhood(start_term)))]),target_terms)),cmp=lambda x,y:y[1]-x[1] if y[1]!=x[1] else cmp(y[2],x[2]))])
	return relation_dict

#analyze hidden relations between two terms for a given graph (closed discovery)
#based on the linking terms between starting term and target term
def discover_closed_hidden_relations(graph,start_terms,end_terms,score_method='npmi_score'):
	if isinstance(start_terms,list) or isinstance(start_terms,VertexSeq):
		pass
	elif isinstance(start_terms,int) or isinstance(start_terms,str) or isinstance(start_terms,Vertex):
		start_terms=[start_terms]
	else:
		raise Exception('Parameter Error!')

	if isinstance(end_terms,list) or isinstance(end_terms,VertexSeq):
		pass
	elif isinstance(end_terms,int) or isinstance(end_terms,str) or isinstance(end_terms,Vertex):
		end_terms=[end_terms]
	else:
		raise Exception('Parameter Error!')

	if all(map(lambda x:isinstance(x,int),start_terms)):
		try:
			start_terms=map(lambda x:graph.vs[x],start_terms)
		except:
			print 'Vertex index integer error!'
			print
	elif all(map(lambda x:isinstance(x,str),start_terms)):
		try:
			start_terms=map(lambda x:graph.vs.select(id_eq=x)[0],start_terms)
		except:
			print 'Vertex ID error!'
			print
	elif all(map(lambda x:isinstance(x,Vertex),start_terms)) or isinstance(start_terms,VertexSeq):
		pass
	else:
		raise Exception('Parameter Error!')

	if all(map(lambda x:isinstance(x,int),end_terms)):
		try:
			end_terms=map(lambda x:graph.vs[x],end_terms)
		except:
			print 'Vertex index integer error!'
			print
	elif all(map(lambda x:isinstance(x,str),end_terms)):
		try:
			end_terms=map(lambda x:graph.vs.select(id_eq=x)[0],end_terms)
		except:
			print 'Vertex ID error!'
			print
	elif all(map(lambda x:isinstance(x,Vertex),end_terms)) or isinstance(end_terms,VertexSeq):
		pass
	else:
		raise Exception('Parameter Error!')
	if score_method=='npmi_score' or score_method=='p_value':
		pass
	else:
		raise Exception('Score Method Error!')
	year=graph['year']
	relation_dict=OrderedDict()
	for start_term in start_terms:
		target_terms=list((set(graph.neighborhood(start_term,order=2))-set(graph.neighborhood(start_term))) & set(end_terms))
		relation_dict[start_term]=OrderedDict([(x[0],{'pivot_num':x[1],'awm_score':x[2]}) for x in sorted(zip(target_terms,map(lambda x:len(list(set(graph.neighborhood(x)) & set(graph.neighborhood(start_term)))),target_terms),map(lambda x:mean([min(graph.es[graph.get_eid(x,t)]['_'.join([score_method,year])],graph.es[graph.get_eid(t,start_term)]['_'.join([score_method,year])]) for t in map(lambda d:graph.vs[d],set(graph.neighborhood(x)) & set(graph.neighborhood(start_term)))]),target_terms)),cmp=lambda x,y:y[1]-x[1] if y[1]!=x[1] else cmp(y[2],x[2]))])
	return relation_dict

#compare pairwise graph during different periods incrementally
#Sharan, Roded, and Trey Ideker. "Modeling cellular machinery through biological network comparison." Nature biotechnology 24.4 (2006): 427-433.
def pairwise_network_comparison(graphs,vertices=None,edges=None):
	from scipy import interpolate
	if all(map(lambda x:isinstance(x,Graph),graphs)):
		pass
	else:
		raise Exception("Error: No graph input!")

	if all(map(lambda x:'year' in x.attributes()),graphs) and len(map(lambda x:x['year'].split('-')[0],graphs)):
		pass
	else:
		raise Exception('Error: Beginning years differ for inremental analysis!')

	if any([vertices,edges]):
		if vertices:
			if isinstance(vertices,str):
				vertices=[vertices]
			elif isinstance(vertices,list) and all(map(lambda x:isinstance(x,str),vertices)):
				pass
			else:
				raise Exception('Parameter Error!')

		if edges:
			if isinstance(edges,str):
				edges=[edges]
			elif isinstance(edges,list) and all(map(lambda x:len(x)==2 and isinstance(x[0],str) and isinstance(x[1],str)),edges):
				edges=map(lambda x:sorted(x),edges)
			else:
				raise Exception('Parameter Error!')

	else:
		raise Exception('Parameter Null!')

	graphs=sorted(graphs,key=lambda x:x['year'])

	difference_dict={}
	if vertices:
		difference_dict['vertex']={}
		for i in xrange(1,len(graphs)):
			year1,year2=graphs[i-1]['year'],graphs[i]['year']
			year_interval='-'.join([graphs[i-1]['year'].split('-')[1],graphs[i]['year'].split('-')[1]])
			difference_dict['vertex'][year_interval]=dict(zip(vertices,map(lambda x:g[i].vs.select(id_eq=x)[0]['_'.join(['doc_num',year2])]-g[i-1].vs.select(id_eq=x)[0]['_'.join(['doc_num',year1])],vertices)))

	if edges:
		difference_dict['edge']={}
		for i in xrange(1,len(graphs)):
			year1,year2=graphs[i-1]['year'],graphs[i]['year']
			year_interval='-'.join([graphs[i-1]['year'].split('-')[1],graphs[i]['year'].split('-')[1]])
			difference_dict['edge'][year_interval]=dict(zip(vertices,map(lambda x:g[i].vs.select(id_eq=x)[0]['_'.join(['doc_num',year2])]-g[i-1].vs.select(id_eq=x)[0]['_'.join(['doc_num',year1])],vertices)))

	extrapolation_dict={}
	if vertices:
		extrapolation_dict['vertex']={}
		for v in vertices:
			x=np.array([])
			y=np.array([])
			intervals=difference_dict['vertex'].keys()
			for i in intervals:
				x=np.append(x,i[1]-intervals[0][0])
				y=np.append(y,difference_dict['vertex'][i][v])
			f=interpolate.InterpolatedUnivariateSpline(x,y)
			extrapolation_dict['vertex'][v]={(intervals[-1][1],intervals[-1][1]+1):f(intervals[-1][1]+1),(intervals[-1][1]+1,intervals[-1][1]+2):f(intervals[-1][1]+2)}

	if edges:
		extrapolation_dict['edge']={}
		for v in edges:
			x=np.array([])
			y=np.array([])
			intervals=difference_dict['edge'].keys()
			for i in intervals:
				x=np.append(x,i[1]-intervals[0][0])
				y=np.append(y,difference_dict['edge'][i][v])
			f=interpolate.InterpolatedUnivariateSpline(x,y)
			extrapolation_dict['edge'][v]={(intervals[-1][1],intervals[-1][1]+1):f(intervals[-1][1]+1),(intervals[-1][1]+1,intervals[-1][1]+2):f(intervals[-1][1]+2)}

	difference_dict.update(extrapolation_dict)
	return  difference_dict

#perform clustering based on the k-means approach for a given graph
#mode: edge or vertex
#attr: attributes in graph vertices or edges
#method='a': arithmetic mean;
#method='m': median.
#dist=='c': correlation;
#dist=='a': absolute value of the correlation;
#dist=='u': uncentered correlation;
#dist=='x': absolute uncentered correlation;
#dist=='s': Spearman's rank correlation;
#dist=='k': Kendall's tao ;
#dist=='e': Euclidean distance;
#dist=='b': City-block distance.
def kmeans_clustering(graph,mode,attrs,nclusters=10,method='a',dist='e'):
	if isinstance(graph,Graph):
		pass
	else:
		raise Exception('Error: Not a graph imported!')

	if mode == 'vertex' or mode == 'edge':
		pass
	else:
		raise Exception('Error: Not a required mode!')

	if mode == 'vertex' and isinstance(attrs,list) and all(map(lambda x:isinstance(x,str),attrs)) and all(map(lambda x:x in graph.vs.attributes(),attrs)):
		data=np.array([])
		for i in xrange(0,graph.vcount()):
			data=np.append(data,map(lambda x:graph.vs[x][i],attrs))
	elif mode=='edge' and isinstance(attrs,str) and attrs in graph.es.attributes():
		data=np.array([graph.get_adjacency().tolist()[r][c]>0 and graph.es[attrs][graph.get_eid(r,c)] or 0 for c in xrange(0,graph.vcount()) for r in xrange(0,graph.vcount())])
	else:
		raise Exception('Error: Attribute not included!')
	label=kcluster(data,nclusters=nclusters,method=method,dist=dist)[0].tolist()
	clusters=(max(label)+1)*[[]]
	for i in xrange(0,len(label)):
		clusters[label[i]].append(graph.vs[i]['id'])
	clusters=[graph.subgraph(x) for x in clusters]

	return clusters


#perform clustering based on the k-medoids approach for a given graph
#mode: edge or vertex
#attr: attributes in graph vertices or edges
#dist=='c': correlation;
#dist=='a': absolute value of the correlation;
#dist=='u': uncentered correlation;
#dist=='x': absolute uncentered correlation;
#dist=='s': Spearman's rank correlation;
#dist=='k': Kendall's tao ;
#dist=='e': Euclidean distance;
#dist=='b': City-block distance.
def kmedoids_clustering(graph,mode,attrs,nclusters=10,dist='e'):
	if isinstance(graph,Graph):
		pass
	else:
		raise Exception('Error: Not a graph imported!')

	if mode == 'vertex' or mode == 'edge':
		pass
	else:
		raise Exception('Error: Not a required mode!')

	if mode == 'vertex' and isinstance(attrs,list) and all(map(lambda x:isinstance(x,str),attrs)) and all(map(lambda x:x in graph.vs.attributes(),attrs)):
		data=np.array([])
		for i in xrange(0,graph.vcount()):
			data=np.append(data,map(lambda x:graph.vs[x][i],attrs))
	elif mode=='edge' and isinstance(attrs,str) and attrs in graph.es.attributes():
		data=np.array([graph.get_adjacency().tolist()[r][c]>0 and graph.es[attrs][graph.get_eid(r,c)] or 0 for c in xrange(0,graph.vcount()) for r in xrange(0,graph.vcount())])
	else:
		raise Exception('Error: Attribute not included!')

	label=kmedoids(data,nclusters=nclusters)[0].tolist()
	clusters=(max(label)+1)*[[]]
	for i in xrange(0,len(label)):
		clusters[label[i]].append(graph.vs[i]['id'])
	clusters=[graph.subgraph(x) for x in clusters]

	return clusters

#perform clustering based on the hierarchical clustering approach for a given graph
#mode: edge or vertex
#method=='a': arithmetic mean;
#method=='m': median.
#attr: attributes in graph vertices or edges
#dist=='c': correlation;
#dist=='a': absolute value of the correlation;
#dist=='u': uncentered correlation;
#dist=='x': absolute uncentered correlation;
#dist=='s': Spearman's rank correlation;
#dist=='k': Kendall's tao ;
#dist=='e': Euclidean distance;
#dist=='b': City-block distance.
def hierarchical_clustering(graph,mode,attrs,nclusters=10,method='m',dist='e'):
	if isinstance(graph,Graph):
		pass
	else:
		raise Exception('Error: Not a graph imported!')

	if mode == 'vertex' or mode == 'edge':
		pass
	else:
		raise Exception('Error: Not a required mode!')

	if mode == 'vertex' and isinstance(attrs,list) and all(map(lambda x:isinstance(x,str),attrs)) and all(map(lambda x:x in graph.vs.attributes(),attrs)):
		data=np.array([])
		for i in xrange(0,graph.vcount()):
			data=np.append(data,map(lambda x:graph.vs[x][i],attrs))
	elif mode=='edge' and isinstance(attrs,str) and attrs in graph.es.attributes():
		data=np.array([graph.get_adjacency().tolist()[r][c]>0 and graph.es[attrs][graph.get_eid(r,c)] or 0 for c in xrange(0,graph.vcount()) for r in xrange(0,graph.vcount())])
	else:
		raise Exception('Error: Attribute not included!')

	label=treecluster(data,method=method,dist=dist)[0].cut(nclusters=nclusters).tolist()
	clusters=(max(label)+1)*[[]]
	for i in xrange(0,len(label)):
		clusters[label[i]].append(graph.vs[i]['id'])
	clusters=[graph.subgraph(x) for x in clusters]

	return clusters

#perform clustering based on the self-organizing map clustering approach for a given graph
#mode: edge or vertex
#attr: attributes in graph vertices or edges
#dist=='c': correlation;
#dist=='a': absolute value of the correlation;
#dist=='u': uncentered correlation;
#dist=='x': absolute uncentered correlation;
#dist=='s': Spearman's rank correlation;
#dist=='k': Kendall's tao ;
#dist=='e': Euclidean distance;
#dist=='b': City-block distance.
def som_clustering(graph,mode,attrs,niter=1,dist='e'):
	if isinstance(graph,Graph):
		pass
	else:
		raise Exception('Error: Not a graph imported!')

	if mode == 'vertex' or mode == 'edge':
		pass
	else:
		raise Exception('Error: Not a required mode!')

	if mode == 'vertex' and isinstance(attrs,list) and all(map(lambda x:isinstance(x,str),attrs)) and all(map(lambda x:x in graph.vs.attributes(),attrs)):
		data=np.array([])
		for i in xrange(0,graph.vcount()):
			data=np.append(data,map(lambda x:graph.vs[x][i],attrs))
	elif mode=='edge' and isinstance(attrs,str) and attrs in graph.es.attributes():
		data=np.array([graph.get_adjacency().tolist()[r][c]>0 and graph.es[attrs][graph.get_eid(r,c)] or 0 for c in xrange(0,graph.vcount()) for r in xrange(0,graph.vcount())])
	else:
		raise Exception('Error: Attribute not included!')

	label=somcluster(data,niters=niter,dist=dist)[0]
	clusters=(max(label)+1)*[[]]
	for i in xrange(0,len(label)):
		clusters[label[i]].append(graph.vs[i]['id'])
	clusters=[graph.subgraph(x) for x in clusters]

	return clusters

#perform clustering based on the affinity propagation approach for a given graph
#tending to be very slow and in practice running it on large datasets is essentially impossible
#mode: edge or vertex
#attr: attributes in graph vertices or edges
#dist=='c': correlation;
#dist=='a': absolute value of the correlation;
#dist=='u': uncentered correlation;
#dist=='x': absolute uncentered correlation;
#dist=='s': Spearman's rank correlation;
#dist=='k': Kendall's tao ;
#dist=='e': Euclidean distance;
#dist=='b': City-block distance.
def affinity_propagation_clustering(graph,mode,attrs,dist='e'):
	if isinstance(graph,Graph):
		pass
	else:
		raise Exception('Error: Not a graph imported!')

	if mode == 'vertex' or mode == 'edge':
		pass
	else:
		raise Exception('Error: Not a required mode!')

	if mode == 'vertex' and isinstance(attrs,list) and all(map(lambda x:isinstance(x,str),attrs)) and all(map(lambda x:x in graph.vs.attributes(),attrs)):
		data=np.array([])
		for i in xrange(0,graph.vcount()):
			data=np.append(data,map(lambda x:graph.vs[x][i],attrs))
		distm=distmatrix(data,dist='e')
		data=np.array([])
		for x in distm:
			data=np.append(data,x)

	elif mode=='edge' and isinstance(attrs,str) and attrs in graph.es.attributes():
		data=np.array([graph.get_adjacency().tolist()[r][c]>0 and graph.es[attrs][graph.get_eid(r,c)] or 0 for c in xrange(0,graph.vcount()) for r in xrange(0,graph.vcount())])

	else:
		raise Exception('Error: Attribute not included!')
	label=cluster.affinity_propagation(data).labels_
	clusters=(max(label)+1)*[[]]
	for i in xrange(0,len(label)):
		clusters[label[i]].append(graph.vs[i]['id'])
	clusters=[graph.subgraph(x) for x in clusters]

	return clusters


#perform clustering based on the spectral clustering approach for a given graph
#mode: edge or vertex
#attr: attributes in graph vertices or edges
#dist=='c': correlation;
#dist=='a': absolute value of the correlation;
#dist=='u': uncentered correlation;
#dist=='x': absolute uncentered correlation;
#dist=='s': Spearman's rank correlation;
#dist=='k': Kendall's tao ;
#dist=='e': Euclidean distance;
#dist=='b': City-block distance.
def spectral_clustering(graph,attrs,dist='e',n_clusters=8,assign_labels='kmeans'):
	if isinstance(graph,Graph):
		pass
	else:
		raise Exception('Error: Not a graph imported!')

	if mode == 'vertex' or mode == 'edge':
		pass
	else:
		raise Exception('Error: Not a required mode!')

	affinity_propagation=AffinityPropagation()
	if mode == 'vertex' and isinstance(attrs,list) and all(map(lambda x:isinstance(x,str),attrs)) and all(map(lambda x:x in graph.vs.attributes(),attrs)):
		data=np.array([])
		for i in xrange(0,graph.vcount()):
			data=np.append(data,map(lambda x:graph.vs[x][i],attrs))
		distm=distmatrix(data,dist='e')
		data=np.array([])
		for x in distm:
			data=np.append(data,x)
	elif mode=='edge' and isinstance(attrs,str) and attrs in graph.es.attributes():
		data=np.array([graph.get_adjacency().tolist()[r][c]>0 and graph.es[attrs][graph.get_eid(r,c)] or 0 for c in xrange(0,graph.vcount()) for r in xrange(0,graph.vcount())])

	else:
		raise Exception('Error: Attribute not included!')
	label=cluster.spectral_clustering(n_clusters=n_clusters,assign_labels=assign_labels).labels_
	clusters=(max(label)+1)*[[]]
	for i in xrange(0,len(label)):
		clusters[label[i]].append(graph.vs[i]['id'])
	clusters=[graph.subgraph(x) for x in clusters]

	return clusters

#perform network-based recommendation based on crab module for given edges in a graph
#http://muricoca.github.io/crab/tutorial.html
def network_recommender(graph,attr=None,vertices=None):
	if isinstance(attr,str) and attr in graph.es.attributes():
		pass
	else:
		raise Exception('Error: Attributes not included!')

	if isinstance(vertices,list) or isinstance(vertices,VertexSeq):
		pass
	elif isinstance(vertices,int) or isinstance(vertices,str) or isinstance(vertices,Vertex):
		vertices=[vertices]
	else:
		raise Exception('Parameter Error!')

	if all(map(lambda x:isinstance(x,int),vertices)):
		try:
			vertices=map(lambda x:graph.vs[x],vertices)
		except:
			print 'Vertex index integer error!'
			print
	elif all(map(lambda x:isinstance(x,str),vertices)):
		try:
			vertices=map(lambda x:graph.vs.select(id_eq=x)[0],vertices)
		except:
			print 'Vertex ID error!'
			print
	elif all(map(lambda x:isinstance(x,Vertex),vertices)) or isinstance(vertices,VertexSeq):
		pass
	else:
		raise Exception('Parameter Error!')

	data={}
	for i in xrange(0,graph.vcount()):
		data[graph.vs[i]['id']]={}
		for j in graph.neighbors(v):
			data[graph.vs[i]['id']][graph.vs[j]['id']]=graph.es[graph.get_eid(i,j)][attr]

	model=models.MatrixPreferenceDataModel(data)
	similarity=similarities(model,metrics.pearson_correlation)
	recommender=recommenders.knn.UserBbasedRecommender(model,similarity,with_preference=True)

	vertices=map(lambda x:x['id'],vertices)
	rec={}
	for v in vertices:
		rec[v]=map(lambda x:x[0],recommender.recommend(v))
	return rec

#perform network operations such as addition, substraction, filtration, etc. for a given graph based on various attributes
#mode: edge or vertex
#attr_cutoff_operator_dict:
#key:attr, value:dict{'cutoff':cutoff float or int value,'operator':'eq ne gt lt ge le'}
def network_operation(graph,attr_cutoff_operator_dict,mode=None,):
	graph=graph.copy()

	if mode == 'vertex':
		seq=graph.vs
	elif mode == 'edge':
		seq=graph.es
	else:
		raise Exception('Error: Mode incorrect!')

	attrs=attr_cutoff_operator_dict.keys()
	if isinstance(attrs,list) and all(map(lambda x:isinstance(x,str),attrs)) and all(lambda x:x in seq.attributes(),attrs):
		pass
	else:
		raise Exception('Error: Attributes incorrect!')

	del_elements=[]
	for a in attrs:
		cutoff,operator=attr_cutoff_operator_dict[a].items()
		if operator == 'eq':#reserve items whose attribute values equal to cutoff
			del_elements.extend([x.index for x in seq if x[a]!=cutoff])
		elif operator == 'ne':#reserve items whose attribute values inequal to cutoff
			del_elements.extend([x.index for x in seq if x[a]==cutoff])
		elif operator == 'gt':#reserve items whose attribute values greater than cutoff
			del_elements.extend([x.index for x in seq if x[a]<=cutoff])
		elif operator == 'lt':#reserve items whose attribute values less than cutoff
			del_elements.extend([x.index for x in seq if x[a]>=cutoff])
		elif operator == 'ge':#reserve items whose attribute values greater than or equal to cutoff
			del_elements.extend([x.index for x in seq if x[a]<cutoff])
		elif operator == 'le':#reserve items whose attribute values less than or equal to cutoff
			del_elements.extend([x.index for x in seq if x[a]>cutoff])
		else:
			raise Exception('Error: Invalid operator!')

	del_elements=sorted(set(del_elements))

	if mode == 'vertex':
		graph.delete_vertices(del_elements)
	elif mode == 'edge':
		graph.delete_edges(del_elements)

	return graph


#perform virtual knock-out experiments on complex networks to evaluate significance for a given set of vertices in a graph
#Scardoni, Giovanni, et al. "Node interference and robustness: performing virtual knock-out experiments on biological networks: the case of leukocyte integrin activation network." PloS one 9.2 (2014).
#http://www.cbmc.it/~scardonig/interference/InterferenceUserGuide.pdf

#Centrality
#http://www.cbmc.it/~scardonig/centiscape/CentiScaPefiles/CentralitiesTutorial.pdf
#Stress
#Betweenness
#Radiality
#Closeness
#Centroid Value
#Eccentricity

#feature:'stress','betweenness','radiality','closeness','centroid','eccentricity'
#inference:'positive','neutral','negative'
def network_inference(graph,vertices,feature=None):
	if isinstance(graph,Graph):
		pass
	else:
		raise Exception('Error: Invalid input graph!')

	if isinstance(vertices,list) or isinstance(vertices,VertexSeq):
		pass
	elif isinstance(vertices,int) or isinstance(vertices,str) or isinstance(vertices,Vertex):
		vertices=[vertices]
	else:
		raise Exception('Parameter Error!')

	if all(map(lambda x:isinstance(x,int),vertices)):
		try:
			vertices=map(lambda x:graph.vs[x],vertices)
		except:
			print 'Vertex index integer error!'
			print
	elif all(map(lambda x:isinstance(x,str),vertices)):
		try:
			vertices=map(lambda x:graph.vs.select(id_eq=x)[0],vertices)
		except:
			print 'Vertex ID error!'
			print
	elif all(map(lambda x:isinstance(x,Vertex),vertices)) or isinstance(vertices,VertexSeq):
		pass
	else:
		raise Exception('Parameter Error!')

	graph1=graph.copy()
	graph2=graph.copy()
	graph2.delete_vertices([x.index for x in vertices])

	if feature == 'stress':
		score_dict1=dict(stress_centrality(graph1))
		score_dict2=dict(stress_centrality(graph2))
	elif feature == 'betweenness':
		score_dict1=dict(betweenness_centrality(graph1))
		score_dict2=dict(betweenness_centrality(graph2))
	elif feature == 'radiality':
		score_dict1=dict(radiality_centrality(graph1))
		score_dict2=dict(radiality_centrality(graph2))
	elif feature == 'closeness':
		score_dict1=dict(closeness_centrality(graph1))
		score_dict2=dict(closeness_centrality(graph2))
	elif feature == 'centroid':
		score_dict1=dict(centroid_centrality(graph1))
		score_dict2=dict(centroid_centrality(graph2))
	elif feature == 'eccentricity':
		score_dict1=dict(eccentricity_centrality(graph1))
		score_dict2=dict(eccentricity_centrality(graph2))
	else:
		raise Exception('Error: Invalid feature input!')

	left_vertices=graph.vs.select(lambda x:x not in vertices)

	change_dict={}
	change_dict.fromkeys(left_vertices,None)
	for v in left_vertices:
		change_dict[v]=score_dict2[v]-score_dict1[v]

	inference_dict={}
	inference_dict.fromkeys(left_vertices,None)
	for v in left_vertices:
		if change_dict[v]<0:
			inference_dict[v]='positive'
		elif change_dict[v]>0:
			inference_dict[v]='negative'
		else:
			inference_dict[v]='neutral'

	return inference_dict,change_dict


#search other subgraphs based on patterns of user-queried network
#g1: background graph
#g2: query graph
#method: 'auto','vf2','lad'
def subgraph_search(g1,g2,method='auto'):

	if all(map(lambda x:isinstance(x,Graph),[g1,g2])):
		pass
	else:
		raise Exception('Error: Invalid input graph!')

	try:
		if method == 'auto':
			vertices_index_list=set(map(set,g1.get_subisomorphisms_lad(g2))) | set(map(set,g1.get_subisomorphisms_vf2(g2)))

		elif method == 'vf2':
			vertices_index_list=set(map(set,g1.get_subisomorphisms_vf2(g2)))

		elif method == 'lad':
			vertices_index_list=set(map(set,g1.get_subisomorphisms_lad(g2)))
	except:
		print 'Running error!'
		print

	vertices_index_list=map(sorted,vertices_index_list)

	return map(lambda x:g1.subgraph(x),vertices_index_list)
	'''
