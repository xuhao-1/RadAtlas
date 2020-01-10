#generate synonym mappings based on metamap
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import string
import re
import json
import os
from time import time, sleep
import networkx
import itertools
import sys
from global_module import *
from multiprocessing import *
from collections import OrderedDict

from nltk.stem import PorterStemmer,LancasterStemmer
from nltk.stem.snowball import EnglishStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from string import punctuation,lowercase

print

def metamap_cmd_invoke(part,lib_dir,temp_dir,proc):
	count=0
	for k in part:
		count+=1
		left=len(part)-count
		metamap_cmd=(lib_dir+os.path.sep+'public_mm/bin/metamap -u -v -y -8 -D '+temp_dir+os.path.sep+'%s '+temp_dir+os.path.sep+'%s> /dev/null') % (k+'.txt',k+'.txt.out')
		os.system(metamap_cmd)
		print 'proc'+str(proc),count,left,k

porter=PorterStemmer()
lancaster=LancasterStemmer()
snowball=EnglishStemmer()
wordnet=WordNetLemmatizer()

ontology_name=sys.argv[1]
if len(sys.argv)>2:
	proc_num=int(sys.argv[2])
else:
	proc_num=cpu_count()
print 'Ontology',ontology_name

infile_name=ontology_name+'_nlp'+json_format
infile=open(data_dir+os.path.sep+infile_name,'r')
term_synonyms=json.loads(infile.read())
infile.close()

print 'Writing data to files...'
filelist=[]
for k in term_synonyms.iterkeys():
	values=term_synonyms[k]
	count=0
	for synonym in values:
		count+=1
		filelist.append('~'.join([k,str(count)]))
		tempfile_name='~'.join([k,str(count)])+'.txt'
		print tempfile_name
		#if os.path.exists(temp_dir+os.path.sep+tempfile_name) and os.path.isfile(temp_dir+os.path.sep+tempfile_name):
		#	pass
		#else:
		
		tempfile=open(temp_dir+os.path.sep+tempfile_name,'w')
		tempfile.write(synonym+"\n")
		tempfile.close()
		
print 'Done!'

print 'Initializing metamap...'
cmd=os.popen('ps aux|grep java.*metamap')
if len(cmd.read().split("\n"))>3:
#if 0:
	pass
else:
	os.system(lib_dir+os.path.sep+'public_mm/bin/skrmedpostctl restart > /dev/null' )
	os.system(lib_dir+os.path.sep+'public_mm/bin/wsdserverctl restart > /dev/null' )
	print 'Waiting...'
	#sleep(180)
cmd.close()
print 'Done!'

t=time()
#count=0
#left=len(filelist)
#for k in filelist:
	#print count,left,k
	#if os.path.exists(temp_dir+os.path.sep+k+'.txt.out') and os.path.isfile(temp_dir+os.path.sep+k+'.txt.out'):
	#	pass
	#else:
	#	metamap_cmd=(lib_dir+os.path.sep+'public_mm/bin/metamap -u -v -y -8 '+temp_dir+os.path.sep+'%s '+temp_dir+os.path.sep+'%s> /dev/null') % (k+'.txt',k+'.txt.out')
	#	os.system(metamap_cmd)
	#count+=1
	#left-=1


step=int(len(filelist)/proc_num)+1

parts=[]
for i in xrange(0,len(filelist),step):
	if i+step<=len(filelist):
		parts.append(filelist[i:i+step])
	else:
		parts.append(filelist[i:])

proc_record=[]
count=0
for x in parts:
	count+=1
	print 'Process',str(count),'starting...'
	proc=Process(target=metamap_cmd_invoke,args=(x,lib_dir,temp_dir,count))
	proc.start()
	proc_record.append(proc)

for proc in proc_record:
	proc.join()

print time()-t

'''
def extract(number,total,x):

	print 'Thread:',str(number%proc_num==0 and proc_num or number%proc_num)
	print 'Number:',str(number)
	print 'Left:',str(total-number)
	mapping=OrderedDict()
	infile_name=x+'.txt.out'
	infile=open(temp_dir+os.path.sep+infile_name,'r')
	content=infile.read().lower()
	infile.close()
	
	all_phrases=sum(map(lambda t:word_tokenizer(t.split('phrase: ')[1]),filter(lambda t:'phrase: ' in t,content.split('\n\n'))),[])
	
	temp=filter(lambda t:'variants' in t and '{' in t,content.split("\n\n"))
	temp=map(lambda t:t.split("\n"),temp)

	temp=content.split("\n\n")
	for i in xrange(0,len(temp)):
		if 'variants' in temp[i]  and '{' in temp[i]:
			y=temp[i].split('\n')
			k=y[0].split('[')[0].strip()
			mapping[k]=mapping.get(k,[])
			v=[]
			for z in y[1:]:
				z=z.replace("'s",'').replace("'t",' not ').replace("'d",' would ').replace("'l",' will ').replace("'",'').replace('&',' and ').replace('|', ' or ')
				#z=' '.join(filter(lambda t:t not in stopwords,word_tokenizer(z.split(':')[1].split('{')[0].strip())))	                                
				if ', ' in z:
                                        if int(z.split(':')[1].split('=')[0].split('{')[1].split(',')[1].strip())<semantic_dist:
                                                pass
                                        else:
                                                continue
                                else:
                                        if int(z.split(':')[1].split('=')[0].split('{')[1].strip())<semantic_dist:
                                                pass
                                        else:
                                                continue
				if '"' in z:
					if 'd' in z.split('"')[1]:
						continue
					else:
						pass
				else:
					pass
				z=z.split(':')[1].split('{')[0].strip()
				if len(word_tokenizer(k))>1 and len(word_tokenizer(z))>1:
					v.append(z)
				elif len(word_tokenizer(k))>1 and len(word_tokenizer(z))==1:
					if len(z)>1 and len(set(z)&set(lowercase))>0:
						v.append(z)
				elif len(word_tokenizer(z))>1:
					if k in aa_words and k==z:
                                                v.append(z)
                                        elif k in aa_words and ''.join([t for t in z if t.isalnum()])==''.join(t for t in k if t.isalnum()):
                                                pass
					else:
						v.append(z)

				elif lancaster.stem(z)==lancaster.stem(k):
					if k in aa_words and k==z:
						v.append(z)
					elif k in aa_words and ''.join([t for t in z if t.isalnum()])==''.join(t for t in k if t.isalnum()):
						pass
					elif k not in aa_words and porter.stem(z)==porter.stem(k) and len(z)>1 and len(set(z)&set(lowercase))>0:
						v.append(z)
					else:
						pass
				elif lancaster.stem(z)!=lancaster.stem(k):
					if k in aa_words and k==z:
						v.append(z)
					elif k in aa_words and ''.join([t for t in z if t.isalnum()])==''.join(t for t in k if t.isalnum()):
                                                pass
					elif k not in aa_words and porter.stem(z)!=porter.stem(k) and len(z)>1 and len(set(z)&set(lowercase))>0:
						v.append(z)
					else:
						if k not in aa_words and z not in aa_words and len(z)>1 and len(set(z)&set(lowercase))>0:
							v.append(z)
						else:
							pass
			mapping[k].extend(v)
		elif i<len(temp)-1 and 'phrase' in temp[i] and 'variants' not in temp[i+1]:
			y=temp[i].split(':')[1].strip()
			mapping[y]=[y]
		elif i==len(temp)-1 and 'phrase' in temp[i]:
			y=temp[i].split(':')[1].strip()
			mapping[y]=[y]

		existed_phrases=sum(map(lambda t:word_tokenizer(t),mapping.keys()),[])
		if len(set(all_phrases)-set(existed_phrases))>0:
			for t in sorted(set(all_phrases)-set(existed_phrases),key=all_phrases.index):
				mapping[t]=[t]

	if len(mapping.keys())==1:
		k=mapping.keys()[0]
		#mapping[k]=sorted(set([t for t in mapping[k] if t not in frequent_words]))
		if any(map(lambda t:check_frequent_words(t),mapping[k])):
			mapping[k]=[]
		else:
			mapping[k]=sorted(set([t for t in mapping[k] if not check_frequent_words(t)]))
		
	for k in mapping.keys():
		mapping[k]=sorted(set(mapping[k]))

	for k in mapping.keys():
		if len(mapping[k])==0:
			mapping.pop(k)
	return {x:mapping.items()}
'''

def extract(number,total,x):

	print 'Thread:',str(number%proc_num==0 and proc_num or number%proc_num)
	print 'Number:',str(number)
	print 'Left:',str(total-number)
	mapping=OrderedDict()
	infile_name=x+'.txt.out'
	infile=open(temp_dir+os.path.sep+infile_name,'r')
	content=infile.read().lower()
	infile.close()
	
	all_phrases=sum(map(lambda t:word_tokenizer(t.split('phrase: ')[1]),filter(lambda t:'phrase: ' in t,content.split('\n\n'))),[])
	if len(all_phrases)>term_size_cutoff:
		return {}
	temp=filter(lambda t:'variants' in t and '{' in t,content.split("\n\n"))
	temp=map(lambda t:t.split("\n"),temp)

	temp=content.split("\n\n")
	for i in xrange(0,len(temp)):
		if 'variants' in temp[i]  and '{' in temp[i]:
			y=temp[i].split('\n')
			k=y[0].split('[')[0].strip()
			mapping[k]=mapping.get(k,[])
			v=[k]
			for z in y[1:]:
				z=z.replace("'s",'').replace("'t",' not ').replace("'d",' would ').replace("'l",' will ').replace("'",'').replace('&',' and ').replace('|', ' or ')
				#z=' '.join(filter(lambda t:t not in stopwords,word_tokenizer(z.split(':')[1].split('{')[0].strip())))																					
				
				if ', ' in z:
					if int(z.split('{')[1].split(',')[1].split('=')[0].strip())<semantic_dist and ('d' not in z.split('{')[1].split(',')[1].split('=')[1].split('}')[0] or wordnet.lemmatize(z.split(':')[1].split('{')[0].strip()) == wordnet.lemmatize(k) or wordnet.lemmatize(z.split(':')[1].split('{')[0].strip(),pos='v') == wordnet.lemmatize(k,pos='v') or wordnet.lemmatize(z.split(':')[1].split('{')[0].strip(),pos='a') == wordnet.lemmatize(k,pos='a') or snowball.stem(z.split(':')[1].split('{')[0].strip()) == snowball.stem(k)):
						pass
					else:
						continue
				else:
					if int(z.split('{')[1].split('=')[0].strip())<semantic_dist:
						pass
					else:
						continue
				
				if len(set(all_phrases))==1:
					#if '"' in z.split(':')[1] and (z.split(':')[1].split('"')[1]=='i' or z.split(':')[1].split('"')[1]=='p'):
					if '"' in z.split(':')[1] and ('d' not in z.split(':')[1].split('"')[1] or wordnet.lemmatize(z.split(':')[1].split('{')[0].strip()) == wordnet.lemmatize(k) or wordnet.lemmatize(z.split(':')[1].split('{')[0].strip(),pos='v') == wordnet.lemmatize(k,pos='v') or wordnet.lemmatize(z.split(':')[1].split('{')[0].strip(),pos='a') == wordnet.lemmatize(k,pos='a') or snowball.stem(z.split(':')[1].split('{')[0].strip()) == snowball.stem(k)):
						pass
					else:
						continue
				
				z=z.split(':')[1].split('{')[0].strip()	
				
				if len(word_tokenizer(k))>1 and len(word_tokenizer(z))>1:
					v.append(z)
				elif len(word_tokenizer(k))>1 and len(word_tokenizer(z))==1:
					if len(z)>1 and len(set(z)&set(lowercase))>0:
						v.append(z)
				elif len(word_tokenizer(z))>1:
					v.append(z)
                                else:
                                        if k in aa_words and k == z:
                                                v.append(z)
                                        elif k in aa_words:
                                                pass
					elif snowball.stem(k) == snowball.stem(z):
						v.append(z)
					elif lancaster.stem(k) != lancaster.stem(z):
						v.append(z)
					else:
						pass

				'''
				elif len(word_tokenizer(z))>1:
					if k in aa_words and k==z:
                                                v.append(z)
                                        elif k in aa_words and ''.join([t for t in z if t.isalnum()])==''.join(t for t in k if t.isalnum()):
                                                pass
					else:
						v.append(z)
				
				elif lancaster.stem(z)==lancaster.stem(k):
					print k,z
					if k in aa_words and k==z:
						v.append(z)
					elif k in aa_words and ''.join([t for t in z if t.isalnum()])==''.join(t for t in k if t.isalnum()):
						pass
					#elif k not in aa_words and porter.stem(z)==porter.stem(k) and len(z)>1 and len(set(z)&set(lowercase))>0:
						#v.append(z)
						#print k,z
					elif k not in aa_words and len(z)>1 and len(set(z)&set(lowercase))>0:
						v.append(z)
					else:
						pass
				elif lancaster.stem(z)!=lancaster.stem(k):
					if k in aa_words and k==z:
						v.append(z)
					elif k in aa_words and ''.join([t for t in z if t.isalnum()])==''.join(t for t in k if t.isalnum()):
                                                pass
					elif k not in aa_words:
						v.append(z)
					else:
						pass
					#elif k not in aa_words and porter.stem(z)!=porter.stem(k) and len(z)>1 and len(set(z)&set(lowercase))>0:
						#v.append(z)
					#else:
						#if k not in aa_words and z not in aa_words and len(z)>1 and len(set(z)&set(lowercase))>0:
							#v.append(z)
						#else:
							#pass
				'''
			mapping[k].extend(v)
		elif i<len(temp)-1 and 'phrase' in temp[i] and 'variants' not in temp[i+1]:
			y=temp[i].split(':')[1].strip()
			mapping[y]=[y]
		elif i==len(temp)-1 and 'phrase' in temp[i]:
			y=temp[i].split(':')[1].strip()
			mapping[y]=[y]
		existed_phrases=sum(map(lambda t:word_tokenizer(t),mapping.keys()),[])
		if len(set(all_phrases)-set(existed_phrases))>0:
			for t in sorted(set(all_phrases)-set(existed_phrases),key=all_phrases.index):
				mapping[t]=[t]
	
	if len(mapping.keys())==1:
		k=mapping.keys()[0]
		#mapping[k]=sorted(set([t for t in mapping[k] if t not in frequent_words]))
		
		if any(map(lambda t:check_frequent_words(t),mapping[k])):
			mapping[k]=[]
		else:
			mapping[k]=sorted(set([t for t in mapping[k] if not check_frequent_words(t)]))
	
	if len(mapping.keys())==1:
		k=mapping.keys()[0]
		if len(word_tokenizer(k))>1:
			mapping[k]=sorted(set([t for t in mapping[k] if t>min_word_size]))
		else:
			if len(k)<=min_word_size:
				mapping.pop(k)
			elif len(k)>min_word_size:
				mapping[k]=sorted(set([t for t in mapping[k] if t>min_word_size]))	
	if sum(map(len,mapping.keys()))<=min_word_size:
		for k in mapping.keys():
			mapping.pop(k)
	
	#for k in mapping.keys():
		#mapping[k]=[t for t in mapping[k] if len(word_tokenizer(t))>1 or (len(word_tokenizer(t))==1 and not check_frequent_words(t))]
	
	for k in mapping.keys():
		mapping[k]=sorted(set(mapping[k]))

	for k in mapping.keys():
		if len(mapping[k])==0:
			mapping.pop(k)
	#return_value=[]
	#for k,v in mapping.items():
		#return_value.extend([(k,v)]*len(re.compile(''.join(['^',k,'\s+|\s+',k,'\s+|\s+',k,'$|^',k,'$'])).findall(' '.join(all_phrases))))
	if len(mapping.keys())>0:
		return {x:(all_phrases,mapping.items())}
	else:
		return {}
	#return {x:(all_phrases,return_value)}

results=[]
print 'Extracting synonyms...'
t=time()
word_synonyms={}
number=0
total=len(filelist)
child_num=1
pool=Pool(processes=proc_num,maxtasksperchild=child_num)
for x in filelist:
	number+=1
	results.append(pool.apply_async(extract,args=(number,total,x,)))
	#print extract(number,total,x)
pool.close()
pool.join()

for x in results:
	word_synonyms.update(x.get())

for k in word_synonyms.keys():
        if len(word_synonyms[k])==0:
                word_synonyms.pop(k)

#for x in filelist:


#for k in word_synonyms.keys():
	#if len(word_synonyms[k].keys())==0:
		#word_synonyms.pop(k)

#word_synonyms['0']='0 zero'.split(' ')
#word_synonyms['1']='one first i 1st'.split(' ')
#word_synonyms['2']='two second ii 2nd'.split(' ')
#word_synonyms['3']='three third iii 3rd'.split(' ')
#word_synonyms['4']='four fourth iiii iv 4th'.split(' ')
#word_synonyms['5']='five fifth v 5th'.split(' ')
#word_synonyms['6']='six sixth vi 6th'.split(' ')
#word_synonyms['7']='seven seventh vii 7th'.split(' ')
#word_synonyms['8']='eight eighth viii 8th'.split(' ')
#word_synonyms['9']='nine nineth ix viiii 9th'.split(' ')
#word_synonyms['10']='ten tenth x 10th'.split(' ')
#word_synonyms['11']='eleven 11th 11st eleventh xi'.split(' ')
#word_synonyms['12']='twelve twelfth 12th 12nd xii'.split(' ')
#word_synonyms['13']='thirteen thirteenth 13th 13rd xiii'.split(' ')
#word_synonyms['14']='fourteen fourteenth 14th xiv xiiii'.split(' ')
#word_synonyms['15']='fifteen fifteenth 15th xv'.split(' ')
#word_synonyms['16']='sixteen sixteenth 16th xvi'.split(' ')
#word_synonyms['17']='seventeen seventeenth xvii'.split(' ')
#word_synonyms['18']='eighteen eighteenth xviii'.split(' ')
#word_synonyms['19']='nineteen nineteenth xviiii xiv'.split(' ')
#word_synonyms['20']='twenty twentieth xx'.split(' ')
#word_synonyms['21']='twenty-one twenty-first 21st 21th xxi'.split(' ')
#word_synonyms['22']='twenty-two twenty-second 22nd 22th xxii'.split(' ')
#word_synonyms['23']='twenty-three twenty-third 23rd 21th xxiii'.split(' ')
#word_synonyms['24']='twenty-four twenty-fourth 24th xxiiii xxiv'.split(' ')
#word_synonyms['25']='twenty-five twenty-fifth 25th xxv'.split(' ')
#word_synonyms['26']='twenty-six twenty-sixth 26h xxvi'.split(' ')
#word_synonyms['27']='twenty-seven twenty-seventh 27th xxvii'.split(' ')
#word_synonyms['28']='twenty-eight twenty-eighth 28th xxviii'.split(' ')
#word_synonyms['29']='twenty-nine twenty-nineth 29th xxviiii xxiv'.split(' ')
#word_synonyms['30']='thirty thirtieth 30th'.split(' ')
#word_synonyms['35']='thirty-five thirty-fifth 35th'.split(' ')
#word_synonyms['40']='fourty forty fourtieth fortieth 40th'.split(' ')
#word_synonyms['45']='fourty-five forty-five fourty-fifth forty-fifth 45th'.split(' ')
#word_synonyms['50']='fifty fiftieth 50th'.split(' ')
#word_synonyms['55']='fifty-five fifty-fifth 55th'.split(' ')
#word_synonyms['60']='sixty sixtieth 60th'.split(' ')
#word_synonyms['65']='sixty-five sixty-fifth 65th'.split(' ')
#word_synonyms['70']='seventy seventieth 70th'.split(' ')
#word_synonyms['75']='seventy-five seventy-fifth 75th'.split(' ')
#word_synonyms['80']='eighty eightieth 80th'.split(' ')
#word_synonyms['85']='eighty-five eighty-fifth 85th'.split(' ')
#word_synonyms['90']='ninety ninetith 90th'.split(' ')
#word_synonyms['95']='ninety-five ninety-fifth 95th'.split(' ')
#word_synonyms['100']='one-hundred one-hundredth 100th'.split(' ')
#word_synonyms['200']='two-hundred two-hundreds two-hundredth 200th'.split(' ')
#word_synonyms['300']='three-hundred three-hundreds three-hundredth 300th'.split(' ')
#word_synonyms['400']='four-hundred four-hundreds four-hundredth 400th'.split(' ')
#word_synonyms['500']='five-hundred five-hundreds five-hundredth 500th'.split(' ')
#word_synonyms['600']='six-hundred six-hundreds six-hundredth 600th'.split(' ')
#word_synonyms['700']='seven-hundred seven-hundreds seven-hundredth 700th'.split(' ')
#word_synonyms['800']='eight-hundred eight-hundreds eight-hundredth 800th'.split(' ')
#word_synonyms['900']='nine-hundred nine-hundreds nine-hundredth 900th'.split(' ')
#word_synonyms['1000']='1,000 one-thousand one-thousandth ten-hundreds ten-hundredth 1000th'.split(' ')
#word_synonyms['2000']='2,000 two-thousand two-thousandth twenty-hundreds twenty-hundredth 2000th'.split(' ')
#word_synonyms['3000']='3,000 three-thousand three-thousandth thirty-hundreds thirty-hundredth 3000th'.split(' ')
#word_synonyms['4000']='4,000 four-thousand four-thousandth fourty-hundreds fourty-hundredth forty-hundreds forty-hundredth 4000th'.split(' ')
#word_synonyms['5000']='5,000 five-thousand five-thousandth fifty-hundreds fifty-hundredth 5000th'.split(' ')
#word_synonyms['6000']='6,000 two-thousand two-thousandth twenty-hundreds twenty-hundredth 6000th'.split(' ')
#word_synonyms['7000']='7,000 seven-thousand seven-thousandth seventy-hundreds seventy-hundredth 7000th'.split(' ')
#word_synonyms['8000']='8,000 eight-thousand eight-thousandth eighty-hundreds eighty-hundredth 8000th'.split(' ')
#word_synonyms['9000']='9,000 nine-thousand nine-thousandth ninety-hundreds ninety-hundredth 9000th'.split(' ')
#word_synonyms['10000']='10,000 ten-thousands ten-thousandth 10,000th 10000th'.split(' ')
#word_synonyms['20000']='20,000 twenty-thousands twenty-thousandth 20,000th 20000th'.split(' ')
#word_synonyms['30000']='30,000 thirty-thousands thirty-thousandth 30,000th 30000th'.split(' ')
#word_synonyms['40000']='40,000 fourty-thousands fourty-thousandth forty-thousands forty-thousandth 40,000th 40000th'.split(' ')
#word_synonyms['50000']='50,000 fifty-thousands fifty-thousandth 50,000th 50000th'.split(' ')
#word_synonyms['60000']='60,000 sixty-thousands sixty-thousandth 60,000th 60000th'.split(' ')
#word_synonyms['70000']='70,000 seventy-thousands seventy-thousandth 70,000th 70000th'.split(' ')
#word_synonyms['80000']='80,000 eighty-thousands eighty-thousandth 80,000th 80000th'.split(' ')
#word_synonyms['90000']='90,000 ninety-thousands ninety-thousandth 90,000th 90000th'.split(' ')
#print 'Done!'
#print time()-t

print 'Generate mappings...'
t=time()
#word_mappings=[]
"""
for k in word_synonyms.keys():
	v=word_synonyms[k]
	word_mappings.extend(list(itertools.product(v,v)))

word_mappings=filter(lambda x:x[0]!=x[1] and x[0].find(' ')==-1 and x[1].find(' ')==-1,word_mappings)
"""
#for k in word_synonyms.keys():
#	v=word_synonyms[k]
#	word_mappings.extend(itertools.product([k],v))
#word_mappings=filter(lambda x:x[0]!=x[1] and x[1]!='' and x[0].find(' ')==-1 and x[1].find(' ')==-1,word_mappings)
#word_mappings.extend(map(lambda x:list(reversed(x)),word_mappings))
#g=networkx.DiGraph(word_mappings)
#word_mappings=sorted(g.edges())

#pattern=re.compile('[\d]+')
#words=sorted(set(filter(lambda x:not pattern.findall(x),words)), key=lambda x:len(x))
print 'Done!'
print time()-t

print 'Writing data...'
t=time()

#if ontology_name not in os.listdir(word_dir):
	#os.system('mkdir '+word_dir+os.path.sep+ontology_name)
#else:
	#pass
	#os.system('cd '+word_dir+';rm -rf '+ontology_name+';cd ..')
	#os.system('mkdir '+word_dir+os.path.sep+ontology_name)

#for k in word_synonyms.keys():
	#print 'Output:',str(k)
	#outfile_name=word_dir+os.path.sep+ontology_name+os.path.sep+k+json_format
	#with open(outfile_name,'w') as outfile:
		#data=json.dumps([k,word_synonyms[k]],encoding='utf-8',ensure_ascii=False)
		#outfile.write(data)

outfile_name=data_dir+os.path.sep+ontology_name+'_mapping.json'
outfile=open(outfile_name,'w')
data=json.dumps(word_synonyms,encoding='utf-8',ensure_ascii=False)
outfile.write(data)
outfile.close()

#outfile_name='word_dictionary.json'
#outfile=open(outfile_name,'w')
#data=json.dumps(words,indent=4,encoding='utf-8',ensure_ascii=False)
#outfile.write(data)
#outfile.close()
print 'Done!'
print time()-t
