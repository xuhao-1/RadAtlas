from global_module import *
from whoosh.index import *
from whoosh.fields import *
from whoosh.analysis import *
from whoosh.writing import *
import os
from multiprocessing import Pool,cpu_count
from whoosh.writing import AsyncWriter
from time import time,sleep

#from pymongo import MongoClient
from sqlalchemy import create_engine,MetaData,inspect,\
        Table,Column,Integer,Float,Text,Sequence,func,Boolean
from sqlalchemy.dialects.postgresql import JSON, JSONB

index_dir = 'index_test'
start_year=1946
end_year=2015

if len(sys.argv)>1:
	proc_num=int(sys.argv[1])
else:
	proc_num=cpu_count()

print 'Indexing...'
t1=time()
schema=Schema(title=ID(unique=True,stored=True,sortable=True),content=TEXT(stored=True,analyzer=AnalyzerForIndex(),phrase=True),year=TEXT(stored=True,sortable=True))
if not os.path.exists(index_dir):
	os.system(' '.join(['mkdir',index_dir]))
index=create_in(index_dir,schema)
#writer = AsyncWriter(index)
#writer=index.writer(limitmb=2048,procs=proc_num,multisegment=True)
#writer.commit()
#writer.close()
#analyzer = writer.schema["content"].analyzer
#analyzer.cachesize = -1
#analyzer.clean()

step=5
year_list=[]

#for x in xrange(start_year,end_year+1,step):
	#year_list.append([str(x) for x in range(start_year,end_year+1)[range(start_year,end_year+1).index(x):range(start_year,end_year+1).index(x)+step]])

year_list.append(map(str,range(start_year,end_year+1)))
db=create_engine(connection_string,pool_size=proc_num)
#engine=db.connect()
#metadata=MetaData(engine)
#inspector=inspect(engine)

for years in year_list:
	t2=time()
	print 'Years','-'.join(years)
	
	print 'Restarting database...'
#	db=create_engine(connection_string,pool_size=proc_num)
	engine=db.connect()
	metadata=MetaData(engine)
	inspector=inspect(engine)
	#os.system('mongod -f /etc/mongodb.conf --shutdown')
	#os.system('mongod -f /etc/mongodb.conf &')
	print 'Done!'
	print

	#client=MongoClient()
	#db=client['pubmed']
	writer = AsyncWriter(index)

	for year in years:
		#collection=db[year]
		#total=collection.count()
		table_name='pubmed_sent_'+year
		table=Table(table_name,metadata,autoload=True)
		statement=table.count()
		total=engine.execute(statement).fetchone()[0]
		print 'Doc count',str(total)
		print
	        
		t=time()
		num=0
		#for post in collection.find():
		statement=table.select()
		for post in engine.execute(statement).fetchall():
			num+=1
			left=total-num
			if left > 5000 and left % 5000==0:
				print 'Year',year,'Left',str(left),'Count',str(num)
				print 'Consuming time:',str(time()-t)
				print
				t=time()

			#title=post['_id']
			title=post['id']
			sent=post['sent']
			year=post['year']
			writer.add_document(title=title,content=sent,year=year)
	
	#client.close()
	engine.close()
	print 'Done!'
	print 'Consuming time',str(time()-t2)+'s'
	print 

        print 'Restarting database...'
        #os.system('mongod -f /etc/mongodb.conf --shutdown')
        #os.system('mongod -f /etc/mongodb.conf &')
        print 'Done!'
        print

	print 'Waiting...'
        #sleep(15)
        print 'Done'
        print

	
	t3=time()
	print 'Committing...'
	writer.commit()
	#writer.close()
	print 'Done!'
	print
	
	print'Cleaning caches...'
        os.system('sync')
	os.system('free -m')
	os.system('echo 1 >/proc/sys/vm/drop_caches')
	print 'Done!'
	print

	print 'Waiting...'
	#sleep(15)
	print 'Done!'
	print

	print 'Consuming time',str(time()-t2)+'s'
	print

#engine.close()
index.close()

sent_count_year={}
db=create_engine(connection_string,pool_size=proc_num)
engine=db.connect()
metadata=MetaData(engine)
for years in year_list:
	for year in years:
        	table_name='_'.join(['pubmed_sent',year])
        	table=Table(table_name,metadata,autoload=True)
        	statement=table.count()
        	sent_count_year[year]=engine.execute(statement).fetchone()[0]
        	print 'Count',year,str(sent_count_year[year])

table_name='pubmed_sent_count'
inspector=inspect(engine)
if table_name in inspector.get_table_names():
        table=Table(table_name,metadata,autoload=True)
        table.drop()
        metadata.remove(table)
table=Table(table_name,metadata,
	Column('year',Text,primary_key=True,index=True),
	Column('count',Integer)
)
table.create()
table=Table(table_name,metadata,autoload=True)
statement=table.insert()
posts=[dict(zip(['year','count'],x)) for x in sent_count_year.items()]
engine.execute(statement,posts)
engine.close()
print 'Running...'
print 'Total consuming time',str(time()-t1)+'s'
print
