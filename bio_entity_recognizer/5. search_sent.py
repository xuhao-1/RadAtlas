#search ontolgoy terms in pre-built index and restore retrieved results into mongodb
from __future__ import division
from global_module import *
import math
import os
import re
import math
import string
from whoosh.query import *
from whoosh.analysis import *
from whoosh.index import *
from whoosh.scoring import *
from time import time,sleep
import sys, itertools
import networkx as nw
from pymongo import MongoClient
from multiprocessing import Queue
from multiprocessing import Pool as ThreadPool
from multiprocessing import Lock as ThreadLock
from multiprocessing import cpu_count
from shutil import rmtree

#from multiprocessing.dummy import Pool as ThreadPool
#from multiprocessing.dummy import Lock as ThreadLock
from os import popen,system
import gc

print

#phrase_set_slop=1
#query_set_slop=2
'''
def search(part_count,part_total,proc_num,index,item,num,total):

	lock=ThreadLock()

	lock.acquire()
	print 'Thread',str(num%proc_num+1)
	print 'Part',str(part_count)
	print 'Total',str(part_total)
	print 'Starting',str(num+1),'...'
	print 'Left',str(total-num-1),'...'
	print
	lock.release()

	analyzer=AnalyzerForAnalysis()
	searcher=index.searcher()
	#infile_path=word_dir+os.path.sep+ontology_name+os.path.sep+item
	#with open(infile_path,'r') as infile:
		#k,variants=json.loads(infile.read())

	k,variants=item
	outfile_name=k+json_format
	outfile_path=search_dir+os.path.sep+ontology_name+os.path.sep+outfile_name

	t_r=time()
	parts=map(lambda x:x[0],variants)
        part_min_len=min([len(x.split()) for x in parts])
        part_max_len=max([len(x.split()) for x in parts])
        part_total_len=sum([len(x.split()) for x in parts])
	variants=dict(variants)
	#parts=variants.keys()
	#part_min_len=min([len(x) for x in parts])
	#part_max_len=max([len(x) for x in parts])
	#part_total_len=sum([len(x) for x in parts])

	term=sorted(set(reduce(lambda x,y:x+y,map(lambda z:z.split(),parts))),key=parts.index)
	term_len=len(term)
	combinations=[]
	for x in xrange(int(math.floor(term_len/part_max_len)),int(math.ceil(term_len/part_min_len))+1):
                combinations.extend(filter(lambda y:' '.join(sorted(y,key=parts.index))==' '.join(term),list(itertools.combinations(parts,x))))
	queries=[]

	for y in combinations:
		print y
		temp=[y]
		if len(y)>4:
			for x in y:
				temp.append(y[:y.index(x)]+y[y.index(x)+1:])
		for x in temp:
			query_set_slop=0
			query_list=[]
			for z in x:
				z1=[]
				slop_list=[]
				for z2 in variants[z]:
					z3=[t.text for t in analyzer(z2)]
					if len(z3)>1:
						if len(z3)>4:
							phrase_set_slop=len(z3)+1
						else:
							phrase_set_slop=len(z3)
						z1.append(Phrase('content',z3,slop=phrase_set_slop))
						slop_list.append(phrase_set_slop)
					else:
						z1.append(Term('content',z3[0]))
						slop_list.append(1)
				z=z1
				#z=map(lambda z:Phrase('content',[t.text for t in analyzer(z)],slop=phrase_set_slop) if len([t.text for t in analyzer(z)])>1 else Term('content',z),variants[z])

				if len(z)==1:
					query_list.append(z[0])
				else:
					query_list.append(Or(z))
				query_set_slop+=max(slop_list)
			if len(query_list)==1:
				queries.append(query_list[0])
			else:
				#if len(query_list)>4:
					#query_set_slop=len(query_list)+1
				#else:
					#query_set_slop=len(query_list)
				if query_set_slop>4:
					query_set_slop+=1
				else:
					pass
				queries.append(SpanNear2(query_list,slop=query_set_slop,ordered=False,mindist=0))
		print x,map_tag('en-ptb','universal',tagger.tag(word_tokenizer(x))[0][1]).lower()
	posts=[]
	sent_set=set()
	for query in queries:
		results=searcher.search(query,limit=None,terms=True)
		if len(results)>0:
			posts.extend([dict(zip(['sent','matched_terms','ontology','term','score','year'],[x['title'],map(lambda t:t[1],x.matched_terms()),k.split('~')[0],'~'.join(k.split('~')[:2]),str(x.score),x['year']])) for x in results if x['title'] not in sent_set])
			sent_set|=set([x['title'] for x in results])	
#'query':' '.join(map(lambda y:y[1],list(query.iter_all_terms())))

	hit_num=len(posts)
	if hit_num>0:
		outfile=open(outfile_path,'w')
		data=json.dumps(posts,encoding='utf-8',ensure_ascii=False)
		outfile.write(data)
		outfile.close()

	lock.acquire()

	print 'Thread',str(num%proc_num+1)
        print 'Part',str(part_count)
        print 'Total',str(part_total)
	print 'Number',str(num+1),'Done!'
	print 'Identifier',k
	print 'Term:',term
	print 'Queries:',queries
	print 'Query Terms:'
	print str(' '.join(term))
	if hit_num>0:
		print "Hits",str(hit_num),'...'
	print 'Left',str(total-num-1),'...'
	print 'Consuming time',str(time()-t_r)
	print

	lock.release()


	del searcher,variants,combinations,queries,posts,sent_set
	gc.collect()
'''
def search(part_count,part_total,proc_num,index,item,num,total):

	lock=ThreadLock()

	lock.acquire()
	print 'Thread',str(num%proc_num+1)
	print 'Part',str(part_count)
	print 'Total',str(part_total)
	print 'Starting',str(num+1),'...'
	print 'Left',str(total-num-1),'...'
	#print 'Item',item
	print
	lock.release()

	analyzer=AnalyzerForAnalysis()
	splitting=AnalyzerForSplit()
	searcher=index.searcher(weighting=BM25F)
	#infile_path=word_dir+os.path.sep+ontology_name+os.path.sep+item
	#with open(infile_path,'r') as infile:
		#k,variants=json.loads(infile.read())
	k=item[0]
	term=item[1][0]
	if len(term)<=term_size_cutoff:
		pass
	else:
		return
	variants=item[1][1]
	outfile_name=k+json_format
	outfile_path=search_dir+os.path.sep+ontology_name+os.path.sep+outfile_name

	t_r=time()

	phrase_count={}
	parts=sorted(set(map(lambda x:x[0],variants)))
	part_min_len=min([len([t.text for t in splitting(x)]) for x in parts])
	part_max_len=max([len([t.text for t in splitting(x)]) for x in parts])
	variants=dict(variants)
	for x in variants.keys():
		x=' '.join([t.text for t in splitting(x)])
		pattern_list=['\s+?('+x+')\s+?','^('+x+')\s+?','\s+?('+x+')$','^('+x+')$']
		phrase_count[x]=sum(map(lambda t:len(re.compile(t).findall(' '.join([t.text for t in splitting(' '.join(term))]))),pattern_list))
	#parts=variants.keys()
	#part_min_len=min([len(x) for x in parts])
	#part_max_len=max([len(x) for x in parts])
	#part_total_len=sum([len(x) for x in parts])
	
	term_len=len(set([t.text for t in splitting(' '.join(term))]))
	combinations=[]
	for x in xrange(int(math.floor(term_len/part_max_len)),int(math.ceil(term_len/part_min_len))+1):
		combinations.extend(filter(lambda y:sorted([t.text for t in splitting(' '.join(sorted(y,key=parts.index)))])==sorted(set([t.text for t in splitting(' '.join(term))])),list(itertools.combinations(parts,x))))
	queries=[]

	for y in combinations:
		temp=[y]
	#	if len(y)>4:
	#		for x in y:
	#			temp.append(y[:y.index(x)]+y[y.index(x)+1:])
	#	for x in y:
	#		if check_general_words(x):
	#			temp.append(y[:y.index(x)]+y[y.index(x)+1:])	
		for x in temp:
			query_list=[]
			for z in x:
				z1=[]
				for z2 in variants[z]:
					z3=[t.text for t in analyzer(z2)]	
					if len(z3)>1:
						#z1.append(Phrase('content',z3,slop=phrase_set_slop))
						z1.append(Phrase('content',z3,slop=phrase_slop_cutoff))
						#for t in z3:
							#z1.append(Term('content',t))
					else:
						z1.append(Term('content',z3[0]))
				z4=z
				z=z1
				#z=map(lambda z:Phrase('content',[t.text for t in analyzer(z)],slop=phrase_set_slop) if len([t.text for t in analyzer(z)])>1 else Term('content',z),variants[z])

				for t in xrange(0,phrase_count[' '.join([s.text for s in splitting(z4)])]):
					if len(z)==1:
						query_list.append(z[0])
					else:
						query_list.append(Or(z))
				#if len(z)==1:
					#query_list.append(z[0])
				#else:
					#query_list.append(Or(z))
			if len(query_list)==1:
				queries.append(query_list[0])
			else:
				#if len(query_list)>4:
					#query_set_slop=len(query_list)+1
				#else:
					#query_set_slop=len(query_list)
				#queries.append(SpanNear2(query_list,slop=query_set_slop,ordered=False,mindist=0))
				queries.append(SpanNear2(query_list,ordered=False,slop=query_slop_cutoff))
        print queries
	'''
	posts=[]
	sent_set=set()
	for query in queries:
		results=searcher.search(query,limit=None,terms=True)
		if len(results)>0:
			posts.extend([dict(zip(['sent','matched_terms','ontology','term','score','year'],[x['title'],map(lambda t:t[1],x.matched_terms()),k.split('~')[0],'~'.join(k.split('~')[:2]),str(x.score),x['year']])) for x in results if x['title'] not in sent_set])
                        #sent_set|=set([x['title'] for x in results])

#'query':' '.join(map(lambda y:y[1],list(query.iter_all_terms())))

	hit_num=len(posts)
	if hit_num>0:
		outfile=open(outfile_path,'w')
		data=json.dumps(posts,encoding='utf-8',ensure_ascii=False)
		outfile.write(data)
		outfile.close()
	'''
	results=searcher.search(SpanOr(queries),limit=None,terms=True)
	posts=[]
	if len(results)>0:
		posts.extend([dict(zip(['sent','matched_terms','ontology','term','score','year'],[x['title'],map(lambda t:t[1],x.matched_terms()),k.split('~')[0],'~'.join(k.split('~')[:2]),str(x.score),x['year']])) for x in results])
	hit_num=len(posts)
	if hit_num>0:
		outfile=open(outfile_path,'w')
		data=json.dumps(posts,encoding='utf-8',ensure_ascii=False)
		outfile.write(data)
		outfile.close()

	lock.acquire()

	print 'Thread',str(num%proc_num+1)
        print 'Part',str(part_count)
        print 'Total',str(part_total)
	print 'Number',str(num+1),'Done!'
	print 'Identifier',k
	print 'Term:',term
	print 'Queries:',queries
	print 'Query Terms:'
	print str(' '.join(term))
	if hit_num>0:
		print "Hits",str(hit_num),'...'
		#print 'Sents',sorted(set(sent_set))
	print 'Left',str(total-num-1),'...'
	print 'Consuming time',str(time()-t_r)
	print

	lock.release()


	del searcher,variants,combinations,queries,posts
	gc.collect()

ontology_name=sys.argv[1]

if len(sys.argv)>2:
	proc_num=int(sys.argv[2])
else:
#	with popen("grep 'processor' /proc/cpuinfo | sort -u | wc -l") as cmd:
#		proc_num=int(cmd.read().strip())
#	proc_num=20
	proc_num=cpu_count()

if len(sys.argv)>3:
	child_num=int(sys.argv[3])
else:
	child_num=1

t1=time()

if ontology_name not in os.listdir(search_dir):
	#os.system('mkdir '+search_dir+os.path.sep+ontology_name)
	os.mkdir(search_dir+os.path.sep+ontology_name)
else:
	os.chdir(search_dir)
	rmtree(ontology_name)
	os.chdir('..')
	os.mkdir(search_dir+os.path.sep+ontology_name)
	#pass
	#os.system('cd '+search_dir+';rm -rf '+ontology_name+';cd ..')
	#os.system('mkdir '+search_dir+os.path.sep+ontology_name)

t1=time()

print 'Read indexes...'
index=open_dir(index_dir)

print 'Done!'
print 'Consuming time',str(time()-t1),'...'
print

t2=time()
#word_mappings=os.listdir(word_dir+os.path.sep+ontology_name)
with open(data_dir+os.path.sep+ontology_name+'_mapping'+json_format) as infile:
	word_mappings=json.loads(infile.read()).items()

step=len(word_mappings)
length=len(word_mappings)
count=int(math.ceil(length/step))
for i in xrange(0,count):
	t=time()
	print 'Part',str(i+1)
	print
	part=word_mappings[i*step:(i+1)*step]
	pool=ThreadPool(processes=proc_num,maxtasksperchild=child_num)
	#pool=ThreadPool(processes=proc_num)
	for x in xrange(0,len(part)):
		pool.apply_async(search,args=(i+1,count,proc_num,index,word_mappings[x+i*step],x+i*step,length,))
		#search(i+1,count,proc_num,index,word_mappings[x+i*step],x+i*step,length)
	pool.close()
	pool.join()

	print 'Done!'
	print 'Consuming time',str(time()-t)
	print

	print 'Cleaning caches...'
	os.system('sync')
	os.system('free -m')
	os.system('echo 1 >/proc/sys/vm/drop_caches')
	print 'Done!'
	print

index.close()

print 'Cleaning caches...'
os.system('sync')
os.system('free -m')
os.system('echo 1 >/proc/sys/vm/drop_caches')
print 'Done!'
print

print 'Done!'
print 'Consuming time',str(time()-t2),'...'
print

#print 'Waiting...'
#sleep(10)
#print 'Done!'
#print

#proc_num=cpu_count()

#t3=time()


#print 'Restarting database...'
##system('service postgresql restart')
##system('service postgresql start')
#print 'Done!'
#print

#print 'Importing into database...'

#from sqlalchemy import create_engine,MetaData,inspect,\
#	Table,Column,Integer,Float,Text,Sequence,func
#from sqlalchemy.dialects.postgresql import JSON, JSONB

#db=create_engine(connection_string,pool_size=proc_num)
#engine=db.connect()
#metadata=MetaData(engine)

#table_name='_'.join([ontology_name,'search'])
#print 'Table name',table_name
#inspector=inspect(engine)
#if table_name in inspector.get_table_names():
#	table=Table(table_name,metadata,autoload=True)
#	table.drop(checkfirst=True)
#	metadata.remove(table)
#sequence=Sequence('_'.join([table_name,'id_seq']),metadata=metadata)
#sequence.drop(checkfirst=True)
#metadata.remove(sequence)
#table=Table(table_name,metadata,
#	Column('id',Integer,sequence,primary_key=True),
#	Column('sent',Text,index=True),
#	Column('matched_terms',JSON),
#	Column('ontology',Text),
#	Column('term',Text,index=True),
#	Column('score',Float),
#	Column('year',Text,index=True)
#	)

#table.create(checkfirst=True)

#total=0
#step=5000

#print 'Getting infile list...'
#infile_list=filter(lambda x:x.startswith(ontology_name),os.listdir(search_dir+os.path.sep+ontology_name))
#print 'Done!'
#print

#left=len(infile_list)

#def insert_db(proc_num,x,length,infile_name):
#	lock=ThreadLock()
#	t=time()
#	infile=open(search_dir+os.path.sep+ontology_name+os.path.sep+infile_name,'r')
#	posts=json.loads(infile.read())
#	infile.close()
#	engine=db.connect()
#	statement=table.insert()
#	result=engine.execute(statement,posts)
#	engine.close()
#	lock.acquire()
#	num=result.rowcount
#	print 'Thread:',str(x%proc_num+1)
#	print 'Number:',str(x+1)
#	print 'Left:',str(length-x-1)
#	print 'Insert:',str(num)
#	print 'Consuming:',str(time()-t)
#	print
#	lock.release()

#pool=ThreadPool(processes=proc_num,maxtasksperchild=child_num)
##pool=ThreadPool(processes=proc_num)
#length=len(infile_list)
#for x in xrange(0,length):
#	pool.apply_async(insert_db,args=(proc_num,x,length,infile_list[x],))
#	#insert_db(proc_num,x,length,infile_list[x])
#pool.close()
#pool.join()

#statement=table.count()
#table_count=engine.execute(statement).fetchone()[0]
#print 'Total insertion:',str(table_count)
#print
#engine.close()
#print 'Done!'
#print

##
## print 'Restarting database...'
## #system('mongod -f /etc/mongodb.conf --shutdown')
## system('mongod -f /etc/mongodb.conf &')
## print 'Done!'
## print
##
## print 'Importing into database...'
## client=MongoClient()
## db=client['search']
## if ontology_name in db.collection_names():
## 	db.drop_collection(ontology_name)
##
## collection=db[ontology_name]
##
## total=0
## step=5000
##
## print 'Getting infile list...'
## infile_list=filter(lambda x:x.startswith(ontology_name),os.listdir(search_dir+os.path.sep+ontology_name))
## print 'Done!'
## print
##
## left=len(infile_list)
##
## def insert_db(proc_num,x,length,infile_name):
## 	lock=ThreadLock()
## 	t=time()
## 	infile=open(search_dir+os.path.sep+ontology_name+os.path.sep+infile_name,'r')
## 	posts=json.loads(infile.read())
## 	infile.close()
## 	result=collection.insert(posts)
##
## 	lock.acquire()
## 	num=len(posts)
## 	print 'Thread:',str(x%proc_num+1)
## 	print 'Number:',str(x+1)
## 	print 'Left:',str(length-x-1)
## 	print 'Insert:',str(num)
## 	print 'Consuming:',str(time()-t)
## 	print
## 	lock.release()
##
## #pool=ThreadPool(processes=proc_num,maxtasksperchild=child_num)
## pool=ThreadPool(processes=proc_num)
## length=len(infile_list)
## length=len(infile_list)
## for x in xrange(0,length):
## 	pool.apply_async(insert_db,args=(proc_num,x,length,infile_list[x],))
##
## pool.close()
## pool.join()
##
## print 'Total insertion:',str(collection.count())
## print
## client.close()
## print 'Done!'
## print

#print 'Done!'
#print 'Consuming time',str(time()-t3)
#print

##print 'Restarting database...'
##system('mongod -f /etc/mongodb.conf --shutdown')
##system('mongod -f /etc/mongodb.conf &')
##print 'Done!'
##print

print 'Cleaning caches...'
os.system('sync')
os.system('free -m')
os.system('echo 1 >/proc/sys/vm/drop_caches')
print 'Done!'
print

print 'Done!'
print 'Consuming time',str(time()-t1)
print
