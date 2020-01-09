#to extract term relations in ontology obo-format files
from time import time
import sys
import json
import os
import networkx
from global_module import *

print

t1=time()

#input parameter: ontology name
ontology_name=sys.argv[1] 

#input file: ontology.obo
infile_name=ontology_name+obo_format

print 'Ontology',ontology_name


os.system('dos2unix '+ontology_dir+os.path.sep+infile_name)

print 'Constructing relation graph...'
infile=open(ontology_dir+os.path.sep+infile_name,'r')
#content=infile.read().decode('latin1').encode('utf8')
content=infile.read()
term_list=[x for x in content.split('\n\n') if x.startswith('[Term]')]
relation_list=content.split('[Typedef]')[1:]
infile.close()

outfile_name=ontology_name+'_raw_relation'+json_format
print relation_list
#relation_types='is_a intersection_of union_of disjoint_from'.split()
relation_types=['is_a','interaction_of']
for relation in relation_list:
	relation_type=filter(lambda x:x.lower().startswith('id: '),relation.split("\n"))[0].split(': ')[1].strip().lower()
	print relation_type
	relation_types.append(relation_type)

id_to_relations={}
for k in relation_types:
	id_to_relations[k]={}

for relation_type in relation_types:
	for term in iter(term_list):
		temp_list=filter(lambda x:len(x)>0 and x is not None,term.split("\n"))

		id=''
		relation_list=[]
		for x in iter(temp_list):
			if x.lower().startswith('id: '):
				id='~'.join([ontology_name,x.split(': ')[1].strip().lower()])
			elif relation_type=='is_a':
				if x.lower().startswith('is_a: '):
					relation_list.append('~'.join([ontology_name,x.split(': ')[1].strip().split('!')[0].strip().lower()]))
			elif relation_type=='intersection_of':
				if x.lower().startswith('intersection_of: '):
					relation_list.append('~'.join([ontology_name,x.split(': ')[1].strip().split('!')[0].strip().lower()]))
			#elif relation_type=='union_of':
			#	if x.lower().startswith('union_of: '):
			#		relation_list.append('~'.join([ontology_name,x.split(': ')[1].strip().split('!')[0].strip().lower()]))
			#elif relation_type=='disjoint_from':
			#	if x.lower().startswith('disjoint_from: '):
			#		relation_list.append('~'.join([ontology_name,x.split(': ')[1].strip().split('!')[0].strip().lower()]))

			else:
				if x.lower().startswith('relationship: ') and x.lower().find(relation_type)>-1:
					relation_list.append('~'.join([ontology_name,x.split(': ')[1].strip().split()[1].strip().lower()]))

		if len(relation_list)==0:
			id_to_relations[relation_type][id]=[]
		else:
			id_to_relations[relation_type][id]=relation_list
outfile=open(data_dir+os.path.sep+outfile_name,'w')
data=json.dumps(id_to_relations,encoding='utf-8',ensure_ascii=False)
outfile.write(data)
outfile.close()

print 'Done!'
print 'Consuming time...'
print time()-t1
print

