#to preprocess original downloaded ontology obo-format files

from time import time
import sys
import os
from global_module import *
from collections import OrderedDict
from copy import copy
import networkx
from pymongo import *
from multiprocessing import cpu_count

print

t1=time()

chemical_name_punctuation_num=8

#input parameter: ontology name
ontology_name=sys.argv[1]

#input file: ontology.obo
#input file: ontology_relations_original.json
infile_name_1=ontology_name+obo_format
infile_name_2=ontology_name+'_raw_relation'+json_format

outfile_name_1=ontology_name+'_raw_term'+json_format
outfile_name_2=ontology_name+'_term'+json_format
outfile_name_3=ontology_name+'_relation'+json_format
outfile_name_4=ontology_name+'_depth'+json_format
outfile_name_5=ontology_name+'_parent'+json_format
outfile_name_6=ontology_name+'_bfs'+json_format

print 'Ontology',ontology_name
print 'Converting formats...'
os.system('dos2unix '+ontology_dir+os.path.sep+infile_name_1)
print 'Done'
print 'Consuming time',str(time()-t1)
print

t2=time()
print 'Loading data...'
infile=open(ontology_dir+os.path.sep+infile_name_1,'r')
#content=infile.read().decode('latin1').encode('utf8')
content=infile.read()
infile.close()

for x in content.split('\n\n'):
    if x.startswith('[Term]'):
        print x.strip().split('\n')[1].split('id: ')[1]
block_dict=OrderedDict([('~'.join([ontology_name,x.strip().split('\n')[1].split('id: ')[1].lower()]),x.strip()) for x in content.split('\n\n') if x.startswith('[Term]')])
id_list=block_dict.keys()
infile.close()

with open(data_dir+os.path.sep+infile_name_2,'r') as infile:
	id_to_relations=json.loads(infile.read())
relation_dict=id_to_relations['is_a']
print 'Done!'
print 'Consuming time',str(time()-t2)
print

t3=time()
print 'Preprocessing terms...'
new_block_dict=OrderedDict()
new_id_list=[]

if ontology_name=='go':
	with open(ontology_dir+os.path.sep+'human_gene_ontology_annotation'+json_format,'r') as infile:
		human_go_id_list=json.loads(infile.read())
		new_id_list=list(human_go_id_list)
		temp_list=list(human_go_id_list)
		while len(temp_list)>0 and not set(temp_list).issubset(set(new_id_list)):
			for x in list(temp_list):
				if relation_dict.has_key(x):
					new_id_list.append(x)
					new_id_list.extend(relation_dict[x])
					temp_list.remove(x)
					temp_list.extend(relation_dict[x])
			temp_list=list(set(temp_list))

		new_id_list=sorted(set(new_id_list))
		for id in new_id_list:
			new_block_dict[id]=block_dict[id]

if ontology_name=='ef':
        with open(ontology_dir+os.path.sep+'filtered_efo'+json_format,'r') as infile:
                filtered_efo_id_list=json.loads(infile.read())
                new_id_list=list(filtered_efo_id_list)
                temp_list=list(filtered_efo_id_list)
                while len(temp_list)>0 and not set(temp_list).issubset(set(new_id_list)):
                        for x in list(temp_list):
                                if relation_dict.has_key(x):
                                        new_id_list.append(x)
                                        new_id_list.extend(relation_dict[x])
                                        temp_list.remove(x)
                                        temp_list.extend(relation_dict[x])
                        temp_list=list(set(temp_list))

                new_id_list=sorted(set(new_id_list))
                for id in new_id_list:
                        new_block_dict[id]=block_dict[id]

elif ontology_name=='do':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='caloha':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='cellosaurus':
	for id in id_list:
		if block_dict[id].lower().find('xref: ncbi_taxid:9606 ! homo sapiens')>-1:
			new_id_list.append(id)

	temp_list=list(new_id_list)
	while len(temp_list)>0 and not set(temp_list).issubset(set(new_id_list)):
		for x in list(temp_list):
			if relation_dict.has_key(x):
				new_id_list.append(x)
				new_id_list.extend(relation_dict[x])
				temp_list.remove(x)
				temp_list.extend(relation_dict[x])
		temp_list=list(set(temp_list))

	new_id_list=sorted(set(new_id_list))

	for id in new_id_list:
		new_block_dict[id]=block_dict[id]


elif ontology_name=='hp':
	new_id_list=id_list
	new_block_dict.update(block_dict)
	'''
elif ontology_name=='pathway':
	new_id_list=id_list
	new_block_dict.update(block_dict)
	'''
elif ontology_name=='mop':
	new_id_list=id_list
	new_block_dict.update(block_dict)
elif ontology_name=='mpath':
	new_id_list=id_list
	new_block_dict.update(block_dict)
#elif ontology_name=='pro':
#	with open(ontology_dir+os.path.sep+'human_uniprot_protein_list.txt','r') as infile:
#		human_pro_list=[x.strip().lower() for x in infile.readlines()]
#	for id in id_list:
#		if id.split('~')[1].startswith('pr') and id.split(':')[1] in human_pro_list:
#			new_id_list.append(id)
#	new_id_list=sorted(set(new_id_list),key=new_id_list.index)
#	g=networkx.DiGraph()
#	for k in id_to_relations.keys():
#		g=networkx.compose(g,networkx.DiGraph(id_to_relations.get(k,{})))
#	start_nodes=list(new_id_list)
#	end_nodes=list(set(reduce(lambda x,y:x+y,map(g.successors,start_nodes))))
#	while len(end_nodes)>0 and not set(end_nodes).issubset(set(new_id_list)):
#		new_id_list.extend(end_nodes)
#		new_id_list=list(set(new_id_list))
#		start_nodes=list(end_nodes)
#		end_nodes=list(set(reduce(lambda x,y:x+y,map(g.successors,start_nodes))))
#	for id in new_id_list:
#		new_block_dict[id]=block_dict[id]

#elif ontology_name=='pro':
#	for id in id_list:
#		if id.startswith('pr') and block_dict[id].split('\n')[2].strip().find('(')==-1 and block_dict[id].split('\n')[2].strip().find(')')==-1:
#		#block_dict[id].split('\n')[2].strip().endswith('(human)'):
#			new_id_list.append(id)

#        target_term='pro~pr:000000001'#target term: id: PR:000000001 name: protein
#	node_list_1=[]
#        g=networkx.DiGraph()
##        for k in id_to_relations.keys():
#	for k in ['is_a']:
#                g=networkx.compose(g,networkx.DiGraph(id_to_relations.get(k,{})))
#	start_nodes=[target_term]
#        end_nodes=list(set(reduce(lambda x,y:x+y,map(g.predecessors,start_nodes))))
#        node_list_1.extend(start_nodes)
#        node_list_1=list(set(node_list_1))
#	while len(end_nodes)>0 and not set(end_nodes).issubset(set(node_list_1)):
#                node_list_1.extend(end_nodes)
#                node_list_1=list(set(node_list_1))
#                start_nodes=list(end_nodes)
#                end_nodes=list(set(reduce(lambda x,y:x+y,map(g.predecessors,start_nodes))))

#	#temp_list=copy(new_id_list)
#	#while len(temp_list)>0:
#	#	for x in list(temp_list):
#	#		if relation_dict.has_key(x):
#	#			new_id_list.append(x)
#	#			new_id_list.extend(relation_dict[x])
#	#			temp_list.remove(x)
#	#			temp_list.extend(relation_dict[x])
#	#	temp_list=list(set(temp_list))

#	node_list_2=[]
#	start_nodes=new_id_list
#        end_nodes=list(set(reduce(lambda x,y:x+y,map(g.predecessors,start_nodes))))
#        node_list_2.extend(start_nodes)
#        node_list_2=list(set(node_list_2))
#        while len(end_nodes)>0 and not set(end_nodes).issubset(set(node_list_2)):
#                node_list_2.extend(end_nodes)
#                node_list_2=list(set(node_list_2))
#                start_nodes=list(end_nodes)
#                end_nodes=list(set(reduce(lambda x,y:x+y,map(g.predecessors,start_nodes))))

#	new_id_list=sorted(set(node_list_1) & set(node_list_2) & set(id_list))

#	for id in new_id_list:
#		new_block_dict[id]=block_dict[id]


#elif ontology_name=='progene':
	#new_id_list=id_list
	#new_block_dict.update(block_dict)

elif ontology_name=='se':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='symp':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='rnao':
	new_id_list=id_list
	new_block_dict.update(block_dict)
	'''
elif ontology_name=='chebi':
	#target_term='chebi:52217'#target term: id: CHEBI:52217 name: pharmaceutical
	#target_term='chebi:33232'#target term: id: CHEBI:33232 name: application
	#target_term='chebi:50906'#target term: id: CHEBI:50906 name: role
	#target_term='chebi~chebi:23888'#target term: id: CHEBI:23888 name:drug
	#target_term='chebi~chebi:47867' name: indicator
	target_terms=['chebi~chebi:23888']

        node_list=[]
	g=networkx.DiGraph()
	#for k in id_to_relations.keys():
	for k in ['has_role','is_a']:
                g=networkx.compose(g,networkx.DiGraph(id_to_relations.get(k,{})))

        #start_nodes=[target_term]
	start_nodes=target_terms
	end_nodes=list(set(reduce(lambda x,y:x+y,map(g.predecessors,start_nodes))))
        node_list.extend(start_nodes)
	node_list=list(set(node_list))
        while len(end_nodes)>0 and not set(end_nodes).issubset(set(node_list)):
		node_list.extend(end_nodes)
		node_list=list(set(node_list))
                start_nodes=list(end_nodes)
                end_nodes=list(set(reduce(lambda x,y:x+y,map(g.predecessors,start_nodes))))
	new_id_list=sorted(set(node_list) & set(id_list))
	for id in new_id_list:
		new_block_dict[id]='\n'.join([x for x in block_dict[id].split('\n') if (not x.lower().startswith('synonym')) or (x.lower().startswith('synonym') and sum(map(lambda n:x.count(n),list(string.punctuation)))<=chemical_name_punctuation_num) and x.lower().find('related formula')==-1 and x.lower().find('related smiles')==-1 and x.lower().find('related inchi')==-1 and x.lower().find('related inchikey')==-1])
		#new_block_dict[id]='\n'.join([x for x in block_dict[id].split('\n') if (not x.startswith('synonym')) or (x.startswith('synonym') and x.find('related formula')==-1 and x.find('related smiles')==-1 and x.find('related inchi')==-1 and x.find('related inchikey')==-1)])
	'''
elif ontology_name=='mod':
	#new_id_list=id_list
	#new_block_dict.update(block_dict)
	for id in id_list:
		if block_dict[id].lower().find('subset: psi-mod-slim')>-1:
			new_id_list.append(id)
			new_block_dict[id]=block_dict[id]

elif ontology_name=='so':
	new_id_list=id_list
	new_block_dict.update(block_dict)
	'''
elif ontology_name=='gro':
	new_id_list=id_list
	new_block_dict.update(block_dict)
	'''
elif ontology_name=='vario':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='cmo':
	for id in id_list:
		new_id_list.append(id)
		new_block_dict[id]='\n'.join([x for x in block_dict[id].split('\n') if 'curation_status' not in x.lower() and 'not4curation' not in x.lower()])

elif ontology_name=='mi':
	#new_id_list=id_list
	#new_block_dict.update(block_dict)
	for id in id_list:
		if block_dict[id].lower().find('subset: psi-mi_slim')>-1:
			new_id_list.append(id)
			new_block_dict[id]=block_dict[id]
	'''
elif ontology_name=='proteingene':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='vt':
        new_id_list=id_list
        new_block_dict.update(block_dict)
	
elif ontology_name=='pro':
	with open(ontology_dir+os.path.sep+'hgncmapping'+txt_format,'r') as infile:
		new_id_list=sorted(set([ontology_name+'~'+x.strip().lower().split()[0] for x in infile.readlines()]))
	for id in set(new_id_list) & set(id_list):
		new_block_dict[id]=block_dict[id]

elif ontology_name=='ef':
	with open(ontology_dir+os.path.sep+'filtered_efo'+json_format,'r') as infile:
		new_id_list=json.loads(infile.read())
		for id in new_id_list:
			new_block_dict[id]=block_dict[id]
	'''
elif ontology_name=='drugbank':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='hmdb':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='geneprot':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='reactome':
	new_id_list=id_list
	new_block_dict.update(block_dict)

elif ontology_name=='':
	new_id_list=id_list
	new_block_dict.update(block_dict)


else:

	new_id_list=id_list
	new_block_dict.update(block_dict)

print 'Length',str(len(new_id_list))
print 'Done!'
print 'Consuming time',str(time()-t3)
print

t4=time()
print 'Extracting terms...'
id_to_terms={}

for id in id_list:
	block=block_dict[id]
	id=''
	name=''
	synonym_list=[]

	temp_list=[x for x in block.split('\n') if len(x)>0 and x is not None]
	for x in temp_list:
		if x.lower().startswith('id: '):
			id='~'.join([ontology_name,x.split(': ')[1].strip().lower()])
		if x.lower().startswith('name: '):
			name=x.split(': ')[1].strip()
			synonym_list.append(name)
		if x.lower().startswith('synonym: '):
			synonym_list.append(x.split('"')[1].strip())

	id_to_terms[id]=sorted(set(synonym_list),key=synonym_list.index)

outfile=open(data_dir+os.path.sep+outfile_name_1,'w')
data=json.dumps(id_to_terms,encoding='utf-8',ensure_ascii=False)
outfile.write(data)
outfile.close()

print 'Done!'

new_id_to_terms={}

for id in new_id_list:
	block=new_block_dict[id]
	id=''
	name=''
	synonym_list=[]

	temp_list=[x for x in block.split('\n') if len(x)>0 and x is not None]
	for x in temp_list:
		if x.lower().startswith('id: '):
			id='~'.join([ontology_name,x.split(': ')[1].strip().lower()])
		if x.lower().startswith('name: '):
			name=x.split(': ')[1].strip()
			synonym_list.append(name)
		if x.lower().startswith('synonym: '):
			synonym_list.append(x.split('"')[1].strip())

	new_id_to_terms[id]=sorted(set(synonym_list),key=synonym_list.index)

print 'Done!'

new_id_to_relations={}
'''
for t in id_to_relations.keys():
	if t == 'is_a':
		pass
	else:
		id_to_relations.pop(t)
'''
for t in sorted(id_to_relations.keys()):
	print 'Relation type',t
	new_relation_dict={}
	for x in new_id_list:
		new_relation_dict[x]=list(set(id_to_relations[t][x]) & set(new_id_list))
	new_id_to_relations[t]=new_relation_dict

print 'Done!'
print 'Consuming time',str(time()-t4)
print

t5=time()

print 'Calculating all term depths'
relations=new_id_to_relations['is_a']
g=networkx.DiGraph(relations)

start_nodes=filter(lambda x:g.in_degree()[x]==0,g.in_degree().keys())
end_nodes=[x[0] for x in g.out_degree().items() if x[1]==0]
isolated_nodes=[x[0] for x in g.degree().items() if x[1]==0]
connected_nodes=list(set(g.nodes())-set(isolated_nodes))

#start_nodes=g.nodes()
#end_nodes=g.nodes()
#isolated_nodes=g.nodes()
#connected_nodes=[]

term_to_depths=dict(zip(isolated_nodes,[-1]*len(isolated_nodes)))
term_to_depths.update(dict([(x,min([len(networkx.shortest_path(g,source=x,target=y)) for y in end_nodes if networkx.has_path(g,source=x,target=y)])) for x in connected_nodes]))

print 'Checking depths...'
if ont_depth_cutoff.has_key(ontology_name):
	term_in_depths=set([k for k,v in term_to_depths.items() if v>ont_depth_cutoff.get(ontology_name,0) or term_to_depths[k]==-1])
else:
	term_in_depths=set([k for k,v in term_to_depths.items()])

print 'Done!'

print 'Fitering id depth...'
new_id_list=sorted(term_in_depths)
print 'Done'

print 'Filtering term depths...'

for k in new_id_to_terms.keys():
	if k in term_in_depths:
		pass
	else:
		new_id_to_terms.pop(k)

outfile=open(data_dir+os.path.sep+outfile_name_2,'w')
data=json.dumps(new_id_to_terms,encoding='utf-8',ensure_ascii=False)
outfile.write(data)
outfile.close()
print 'Done!' 

print 'Filtering relation depth...'
for t in new_id_to_relations.keys():
	for k in new_id_to_relations[t].keys():
		if k in term_in_depths:
			for v in new_id_to_relations[t][k][:]:
				if v in term_in_depths:
					pass
				else:
					new_id_to_relations[t][k].remove(v)
		else:
			new_id_to_relations[t].pop(k)
outfile=open(data_dir+os.path.sep+outfile_name_3,'w')
data=json.dumps(new_id_to_relations,encoding='utf-8',ensure_ascii=False)
outfile.write(data)
outfile.close()
print 'Done!'
print

outfile=open(data_dir+os.path.sep+outfile_name_4,'w')
data=json.dumps(term_to_depths,encoding='utf-8',ensure_ascii=False)
outfile.write(data)
outfile.close()

print 'Done!'
print 'Consuming time',str(time()-t5)
print

t6=time()

print 'Extracting all parent nodes...'

for x in end_nodes:
	g.add_edge(x,ontology_name)
for x in [x for x in relations.keys() if x not in g.nodes()]:
	g.add_edge(x,ontology_name)

root_node=ontology_name

parent_nodes=dict([(x,sorted(set(sum(list(networkx.all_simple_paths(g,source=x,target=ontology_name)),[])))) for x in g.nodes()])

print 'Filtering parent depths...'
for k in parent_nodes.keys():
	if k in term_in_depths:
		for v in parent_nodes[k][:]:
			if v in term_in_depths:
				pass
			else:
				parent_nodes[k].remove(v)
	else:
		parent_nodes.pop(k)

outfile=open(data_dir+os.path.sep+outfile_name_5,'w')
data=json.dumps(parent_nodes,encoding='utf-8',ensure_ascii=False)
outfile.write(data)
outfile.close()
print 'Done!'
print 'Consuming time...'
print time()-t6
print

#breadth_first_search_list based on is_a relations

t7=time()
print 'Building BFS search list...'

breadth_first_search_list=sorted(g.nodes(),cmp=lambda x,y:cmp(-1*len(networkx.shortest_path(g,source=x,target=root_node)),-1*len(networkx.shortest_path(g,source=y,target=root_node))) if cmp(-1*len(networkx.shortest_path(g,source=x,target=root_node)),-1*len(networkx.shortest_path(g,source=y,target=root_node)))!=0 else cmp(-1*len(networkx.shortest_path(g,target=x)),-1*len(networkx.shortest_path(g,target=y))))

print 'Filtering search list...'
for i,t in enumerate(breadth_first_search_list):
	breadth_first_search_list[i]=sorted(set(t) & term_in_depths,key=t.index)
	if len(breadth_first_search_list[i])>0:
		pass
	else:
		breadth_first_search_list.pop(i)
print 'Done!'
print
outfile=open(data_dir+os.path.sep+outfile_name_6,'w')
data=json.dumps(breadth_first_search_list,encoding='utf-8',ensure_ascii=False)
outfile.write(data)
outfile.close()
print 'Done!'
print 'Consuming time...'
print time()-t7
print

print 'Inserting data'
print
print 'Restarting database...'
#os.system('service postgresql restart')
#os.system('service postgresql start')
print 'Done!'
print

from sqlalchemy import create_engine,MetaData,inspect,\
	Table,Column,Integer,Text
from sqlalchemy.dialects.postgresql import JSON, JSONB

proc_num=cpu_count()
db=create_engine(connection_string,pool_size=proc_num)
engine=db.connect()
metadata=MetaData(engine)

table_name='_'.join([ontology_name,'term'])
print 'Table name',table_name
inspector=inspect(engine)
if table_name in inspector.get_table_names():
	table=Table(table_name,metadata,autoload=True)
	table.drop(checkfirst=True)
	metadata.remove(table)
table=Table(table_name,metadata,
		Column('id',Text,primary_key=True,index=True,unique=True),
		Column('terms',JSON),
		Column('depth',Integer),
		Column('relations',JSON)
	)

table.create(checkfirst=True)
#metadata.create_all()

#term->ont->[{id:id,terms:[terms],depth:depth,relations:{type:[adjacency_list]}}]
posts=map(lambda x:{'id':x,'terms':new_id_to_terms[x],'depth':term_to_depths[x],'relations':dict(map(lambda t:(t,new_id_to_relations[t][x]),new_id_to_relations.keys()))},new_id_list)
statement=table.insert()
result=engine.execute(statement,posts)
print 'Inserted',str(result.rowcount)
engine.close()
print 'Done!'
print
#print 'Restarting database...'
#os.system('mongod -f /etc/mongodb.conf --shutdown')
#os.system('mongod -f /etc/mongodb.conf &')
#print 'Done!'
#print

print 'Cleaning caches...'
os.system('sync')
os.system('free -m')
os.system('echo 1 >/proc/sys/vm/drop_caches')
print 'Done!'
print
# print 'Inserting data'
# print
# print 'Restarting database...'
# #os.system('mongod -f /etc/mongodb.conf --shutdown')
# os.system('mongod -f /etc/mongodb.conf &')
# print 'Done!'
# print
#
# client=MongoClient()
#
# db_name='term'
# print 'DB name',db_name
# db=client[db_name]
# if ontology_name in db.collection_names():
# 	db.drop_collection(ontology_name)
#
# collection=db[ontology_name]
#
# #term->ont->[{id:id,terms:[terms],depth:depth,relations:{type:[adjacency_list]}}]
# posts=map(lambda x:{'id':x,'terms':new_id_to_terms[x],'depth':term_to_depths[x],'relations':dict(map(lambda t:(t,new_id_to_relations[t][x]),new_id_to_relations.keys()))},new_id_list)
# result=collection.insert(posts)
# print 'Inserted',str(len(posts))
# print 'Done!'
# print
# client.close()
# #print 'Restarting database...'
# #os.system('mongod -f /etc/mongodb.conf --shutdown')
# #os.system('mongod -f /etc/mongodb.conf &')
# #print 'Done!'
# #print
#
# print 'Cleaning caches...'
# os.system('sync')
# os.system('free -m')
# os.system('echo 1 >/proc/sys/vm/drop_caches')
# print 'Done!'
# print

print
print 'Total consuming time...'
print time()-t1
print
