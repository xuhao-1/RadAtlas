# encoding=utf-8
import csv
import os
from os import walk
import json
import re
import sys
# import pickle
from scipy.stats.contingency import chi2_contingency as chi2

'''nohup python match_sent_ly.py Object proteingene Constrain &'''
#没有Constrain就写empty
#如果在curated之后去跑，将curated的基因和句子放到csv里，第一列基因第二列句子，不要表头，放到liuyuan目录下，将csv文件名作为第四个输入变量，如curated_list_uvgd.csv

def is_empty_by_except(d, key):
    try:
        type(d[key])
        return False
    except KeyError:
        #        print "%s ValueError" % num
        return True


def doesnot_exist_by_except(filename):
    try:
        d = json.load(open(filename, 'r'))
        return False
    except:
        try:
            FileNotFoundError
        except NameError:
            # py2
            FileNotFoundError = IOError
            return True


def is_out_of_range_by_except(d, key):
    try:
        type(d[key])
        return True
    except IndexError:
        #        print "%s ValueError" % num
        return False
os.chdir('/home/ultimate/liuyuan/pubmed_xml/pubmed_xml')
d_journal = {}
for y in range(70):
    print(y)
    ye = str(2015 - y)
    name = ye + ".csv"
    with open(name,'r') as infile:
        d_journal.setdefault(ye , {})

        i = 0
        reader=csv.reader(infile)
        for x in reader:
            if(i == 0):
                i+=1
                continue
            #d1[ye].setdefault(x[0],x[2])
            d_journal[ye].setdefault(x[0],x[1])
        i+=1

os.chdir('/home/ultimate/liuyuan')
dict_IF = {}
IF = open("impact_factor.txt")
for l in IF:
    content = l.split("[")
    dict_IF.setdefault(content[0].lower(),content[1])

os.chdir('/home/ultimate/liuyuan/pubmed_sent')
dx = {}
print("Loading Pubmed sentences...")
d_year = {}
for y in range(36):
    print(2018 - y)
    ye = str(2018 - y)
    name = "pubmed_sent_" + ye + ".csv"
    with open(name, 'r') as infile:
        dx.setdefault(ye, {})

        i = 0
        reader = csv.reader(infile)
        for x in reader:
            if (i == 0):
                i += 1
                continue
            d_year.setdefault(x[0], []).append(x[1])
            dx[ye].setdefault(x[0], []).append(x[2])
        i += 1
os.chdir('/home/ultimate/liuyuan/list_curated')
'''
list_sentences = []
with open('sentences.csv','r') as infile:
        reader=csv.reader(infile)
        for x in reader:
            list_sentences.append(x[1][:x[1].rfind('_')])

names = ['sent_id','text']
with open('abstract.csv','w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = names)
    writer.writeheader()
    for ppid in list_sentences:
        for i in range(40):
            sen = ppid+'_'+str(i)
            if not is_empty_by_except(d_year,sen):
                dict_csv = {}
                year = d_year[sen][0]
                dict_csv.setdefault("sent_id",sen)
                dict_csv.setdefault("text",dx[year][sen])

                writer.writerow(dict_csv)
'''

curated_gene_list = set()
curated_sentences = set()
if len(sys.argv)>4:
    csv_name = sys.argv[4]
    with open(csv_name, 'r') as infile:
        reader = csv.reader(infile)
        for x in reader:
            curated_gene_list.add(x[0])
            try:
                curated_sentences.add(x[1])
            except IndexError:
                continue

os.chdir('/home/ultimate/liuyuan')
do_cancer_term = json.load(open("all_cancer_terms_in_do.json",'r'))
do_constrain = do_cancer_term["cancer_set"]
#do_constrain = ['null']

do_term = json.load(open("do_term.json", 'r'))
symp_term = json.load(open("symp_term.json", 'r'))
dict_conv = {}
d_alter = json.load(open('proteingene_term.json', 'r'))
dict_conv_r = {}
f = open('symbol_to_proteingene.json')
convertion = json.load(f)
for l in convertion:
    content = convertion[l]
    ###content = content[content.rfind('~')+1:]
    if (re.search("|", content)):
        u2 = content.split("|")
        u2[0] = u2[0][(u2[0].rfind("~")) + 1:]
        for uu in range(len(u2)):
            u1 = "proteingene~" + u2[uu]
            dict_conv.setdefault(u1, l)
            dict_conv_r.setdefault(l, []).append(u1)
    else:

        dict_conv.setdefault(content, l)
        # print(content[1][:-2])
        dict_conv_r.setdefault(l, content)

d1 = {}
d2 = {}
d3 = {}
d4 = {}
d5 = {}
d_third = {}
d_p3 = {}
set1 = set()
set2 = set()
# input parameter: ontology name
ontology_name1 = sys.argv[1]
ontology_name2 = sys.argv[2]
ontology_name3 = sys.argv[3]
path1 = '/home/ultimate/literature_mining/search/' + ontology_name1
os.chdir(path1)
filename_list = []
for (dirpath, dirnames, filenames) in walk(path1):
    filename_list.extend(filenames)

print("Loading ontology 1...")
d_p1 = {}
d_p2 = {}
j = 0

for filename in filename_list:
    '''
    for x in range(50):
        fi = filename.lower()+'~'+str(x)+'.json'
        if not doesnot_exist_by_except(fi):
            print(fi)
            with open(fi, 'r') as infile:
                f = json.load(infile)
                for item in f:
                    key = item["sent"]
                    set1.add(key)
                    value = item["term"]
                    d1.setdefault(key,[]).append(value)
                    d_p1.setdefault(value,[]).append(key)
    '''
    if not doesnot_exist_by_except(filename):
        # print(filename)

        #id = "do~" + filename.split('~')[1]
        #if id not in do_constrain:
        #   continue

        #else:
        with open(filename, 'r') as infile:
            f = json.load(infile)
            for item in f:
                key = item["sent"]
                set1.add(key)
                value = item["term"]
                d1.setdefault(key, []).append(value)
                d_p1.setdefault(value, []).append(key)

path2 = '/home/ultimate/literature_mining/search/' + ontology_name2
os.chdir(path2)
filename_list = []
for (dirpath, dirnames, filenames) in walk(path2):
    filename_list.extend(filenames)
print("Loading ontology 2...")
ss = 0
sss = 0

for filename in filename_list:

    with open(filename, 'r') as infile:
        # filesize = os.path.getsize(filename)
        f = json.load(infile)
        for item in f:
            key = item["sent"]
            set2.add(key)
            value = item["term"]
            d2.setdefault(key, []).append(value)
            d_p2.setdefault(value, []).append(key)
    ss += 1
    if (ss == 10000):
        print("loading file %d-%d..." % (sss * 10000, (sss + 1) * 10000))
        sss += 1
        ss = 0
    # print(ss)

common_sent = set1 & set2
sys3 = sys.argv[3]
if not (sys3 == "empty"):
    set3 = set()
    path3 = '/home/ultimate/literature_mining/search/' + ontology_name3
    os.chdir(path3)
    filename_list = []
    for (dirpath, dirnames, filenames) in walk(path3):
        filename_list.extend(filenames)

    print("Loading ontology 3...")
    for filename in filename_list:
        with open(filename, 'r') as infile:
            f = json.load(infile)
            for item in f:
                key = item["sent"]
                value = item["term"]
                set3.add(key)
                d_third.setdefault(key, []).append(value)
                d_p3.setdefault(value, []).append(key)

    common_sent = common_sent & set3



d = {}
''' {ontology1 : [ontology2...]} '''
for sent in common_sent:
    for key1 in d1[sent]:
        for key2 in d2[sent]:
            d.setdefault(key1, []).append(key2)

''' {ontology1 : [sentences...]} '''
for sent in common_sent:
    for key4 in d1[sent]:
        d4.setdefault(key4, []).append(sent)

''' {ontology2 : [sentences...]} '''
for sent in common_sent:
    for key2 in d2[sent]:
        d3.setdefault(key2, []).append(sent)

''' {common_sentences : [ontology3...]} '''
# for sent in common_sent:
#    for key in d_third[sent]:
#        d5.setdefault(sent,[]).append(key)


d_new = {}
for key in d:
    s = set(d[key])
    for ssss in s:
        d_new.setdefault(key, []).append(ssss)
print("Matching...")
# if not (sys3=="empty"):
names = ['year', 'matched_term', 'matched_term_constrain', 'sent_id', 'p_value', 'raw_text','Journal','IF']
# else:
#    names = ['year','matched_term','sent_id','p_value','raw_text']
# names = ['year','matched_term','matched_term_constrain','sent_id','p_value','raw_text']
os.chdir(path2)
d_gene = {}
set_gene = set()
for do_id in d_new:
    for gene in d_new[do_id]:
        set_gene.add(gene)

new_path = '/home/ultimate/literature_match/' + ontology_name1
try:
    os.chdir(new_path)
except OSError:
    os.mkdir(new_path)
    os.chdir(new_path)

for do_id in d_new:

    output_name = do_id + '.csv'
    print(output_name)
    ind = do_id.rfind("~")
    with open(output_name, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=names)
        writer.writeheader()

        for gene in d_new[do_id]:

            if not is_empty_by_except(d_alter, gene):
                if curated_gene_list:
                    if d_alter[gene][0] not in curated_gene_list:
                        continue

            gene1 = gene
            # print(gene1)
            '''
            if not is_empty_by_except(dict_conv, gene):

                gene1 = dict_conv[gene]
            else:
                gene1 = gene
            print(gene1)
            '''
            sent_count_1 = len(d_p1[do_id])
            sent_count_2 = len(d_p2[gene1])
            sent_common_count = len(set(d3[gene]) & set(d4[do_id]))
            sent_total_count = 100000000
            chi2_table = [[sent_common_count, sent_count_1 - sent_common_count], [sent_count_2 - sent_common_count,
                                                                                  sent_total_count - sent_count_1 - sent_count_2 + sent_common_count]]
            if min(min(chi2_table)) <= 5:
                correction = True
            else:
                correction = False
            # p_value=round(chi2(chi2_table,correction=correction)[1],4)
            try:
                p_value = chi2(chi2_table, correction=correction)[1]
            except:
                p_value = 0.0
            # if(p_value>0.13):
            #    continue
            # if(p_value==0.0):
            #    continue
            for sentence_id in set(d3[gene]) & set(d4[do_id]):
                doc = sentence_id.split('_')[0]
                year = d_year[sentence_id][0]
                if not is_empty_by_except(d_journal, year):
                    if not is_empty_by_except(d_journal[year], doc):
                        JournalName = d_journal[year][doc]
                        JournalName = JournalName.lower()
                        if (re.search(":", JournalName)):
                            index = JournalName.rfind(":")
                            JournalName = JournalName[:index - 1]
                        if (re.search("\(", JournalName)):
                            index = JournalName.rfind("(")
                            JournalName = JournalName[:index - 1]

                        if is_empty_by_except(d_journal, doc):
                            d_journal.setdefault(doc, []).append(JournalName)
                            # d_journal.setdefault(PMID,[]).append(str(record[0]["ISSN"]))
                            if not is_empty_by_except(dict_IF, JournalName):
                                d_journal.setdefault(doc, []).append(dict_IF[JournalName])
                            else:
                                d_journal.setdefault(doc, []).append(0)
                            # print(JournalName)

                if curated_sentences:
                    #if sentence_id[:sentence_id.rfind('_')] not in curated_sentences:
                    if sentence_id not in curated_sentences:
                        continue

                dict_csv = {}

                # year = re.findall(r"\d+\.?\d*",year)
                # year = year[0]
                dict_csv.setdefault("year", year)
                if not is_empty_by_except(d_alter, gene1):
                    dict_csv.setdefault("matched_term", d_alter[gene1])
                else:
                    dict_csv.setdefault("matched_term", gene1)
                if not (sys3 == "empty"):
                    set_constrain_term = set(d_third[sentence_id])
                    for id in set_constrain_term:
                        dict_csv.setdefault("matched_term_constrain", []).append(id)

                dict_csv.setdefault("sent_id", sentence_id)
                dict_csv.setdefault("p_value", p_value)
                dict_csv.setdefault("raw_text", dx[year][sentence_id])
                if not is_empty_by_except(d_journal, doc):
                    dict_csv.setdefault("Journal", d_journal[doc][0])
                    dict_csv.setdefault("IF", d_journal[doc][1])
                else:
                    d_journal.setdefault(doc, ['NULL', 0])
                    dict_csv.setdefault("Journal", d_journal[doc][0])
                    dict_csv.setdefault("IF", d_journal[doc][1])
                writer.writerow(dict_csv)

print("Done!")