# -*- coding: utf-8 -*-
'''-----------------------------------------
purpose:
    cong pmid_ui.json huoqu pmid-mesh duiying guanxi.
    get_mesh // cong pubmed huoqu mesh xinxi // IR_yes_docs.txt, pmid_ui.json, pmid_ui_supp.xml // pmid_meshid.json
    get_mesh_details // cong MeSH huoqu mesh name, term, class // mesh_desc2019.xml // dict_meshs.json
    get_sents // cong fuwuqi huoqu suoyou pubmed sents // pubmed_sent_X.csv, sent_supp.csv // all_sents.json
    get_mesh_obo // zhizuo obo // - // mesh.obo
    get_mesh_pos0
    get_mesh_pos // huoqu mesh weidian, liyong pmid-meshid // - // matched_meshs.json
    mesh_match // match mesh in sents // - // sent_table_m.csv
    get_highlight // match uv, gene, phenotype in sents // uv_synonym.txt, gene_dis_pmid_sent.csv, gene_synonym.csv, dis_table.csv, dis_synonym.csv // sent_table_all.csv
Created on 2019//, @author: lab
-----------------------------------------'''

import os
import csv
import json
import xml.sax
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#pmid_ui.json 缺少部分文献对应关系，故下载pmid_ui_suppl.xml，编程以补充
class pmid_UIhandler(xml.sax.ContentHandler):#xml处理部分
    def __init__(self):
        print('Start extracting supplementary pmid-meshids...')
        self.CurrentData = ''
        self.pmid = ''
        self.meshids = []
        self.flag_pmid = 1
        #self.rec = {}
    def startElement(self, name, attrs):
        self.CurrentData = name
        if self.CurrentData == 'PubmedArticle':
            #print('a new record')
            self.meshids = []
            self.flag_pmid = 1 #pmid waiting for written in:
        elif self.CurrentData == 'DescriptorName':
            self.meshids.append(attrs['UI'])
    def endElement(self, name):
        self.CurrentData = ''#非常重要！！独占一行的结束标签去掉currentdata，防止characters方法出错
        if name == 'PubmedArticle':
            global pmid_meshids
            #self.rec[self.pmid] = self.meshids
            #print(self.pmid, self.rec[self.pmid])
            pmid_meshids[self.pmid] = self.meshids
    def characters(self, content):
        if (self.CurrentData == 'PMID')&(self.flag_pmid == 1):
            self.pmid = content
            self.flag_pmid = 0
class descHandler(xml.sax.ContentHandler):#MeSH descriptor wenjian chuli
    def __init__(self):
        print('Start dealing with desc...')
        self.flag_id = 0
        self.flag_name = 0
        self.flag_term = 0
        self.flag_tree = 0
        self.head = ''
        self.id = ''
        self.name = ''
        self.term = []
        self.tree = ''
        global msids
        self.mis = msids
        print'number of meshids:', len(self.mis)
    def startElement(self, name, attrs):
        self.head = name
        if name == 'DescriptorRecord':
            self.id = ''
            self.name = ''
            self.term = []
            self.tree = ''
            self.flag_id = 1
            self.flag_name = 1
            self.flag_term = 0
            self.flag_tree = 0
        elif name == 'TermUI':
            self.flag_term = 1
        elif name == 'TreeNumberList':
            self.flag_tree = 1
    def endElement(self, name):
        global dict_meshs
        if (name == 'DescriptorRecord')&(self.id in self.mis):
                dict_meshs[self.id] = {'Name': self.name, 'terms': self.term, 'class': self.tree}
    def characters(self, content):
        if (self.head == 'DescriptorUI')&(self.flag_id == 1):
            self.id = content
            self.flag_id = 0
        elif self.id in self.mis:
            if (self.head == 'String')&(self.flag_name == 1):
                self.name = content
                self.flag_name = 0
            elif (self.head == 'TreeNumber')&(self.flag_tree == 1):
                self.tree = content[0]
                self.flag_tree = 0
            elif (self.head == 'String')&(self.flag_term == 1):
                self.term.append(content.strip())
                self.flag_term = 0
        self.head = ''
def get_mesh():#huoqu pmid suoyou meshid
    #os.chdir('/home/ultimate/xuhao/RadAtlas_data/20190508_data')
    with open("IR_docs.txt", "r") as all_docs:#pmid对应表
        pmids = []
        for line in all_docs:
            pmids.append(line.strip())
        print 'number of pmids:', len(pmids)
    #利用xml文件补充pmid_ui对应关系
    parser = xml.sax.make_parser()# 创建一个 XMLReader
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)# turn off namepsaces
    parser.setContentHandler(pmid_UIhandler())
    parser.parse('pmid_ui.xml')
    print 'len(pmid_meshids):', len(pmid_meshids)
    pmid_meshid = {}#抽取目标对应关系
    print 'these docs not in pmid_ui.xml:'
    for pmid in pmids:
        try:
            pmid_meshid[pmid] = pmid_meshids[pmid]
        except:
            print(pmid)
    print 'closed.\n'
    print 'all methids extracted.', 'pmids:', len(pmids), 'pmid_meshid:', len(pmid_meshid)
    pmid_meshids = 0#释放内存？不知有没有效果
    with open("pmid_meshid.json", "w") as fo:
        json.dump(pmid_meshid, fo)
    return pmid_meshid
def get_mesh_details(pmid_meshid):
    #os.chdir('/home/ultimate/xuhao/RadAtlas_data/20190508_data')
    global msids
    msids = set()
    for i in pmid_meshid:
        for j in pmid_meshid[i]:
            msids.add(j)
    print 'number of meshids:', len(msids)
    
    global dict_meshs
    dict_meshs = {}
    parser1 = xml.sax.make_parser()# chuangjian XMLReader
    parser1.setFeature(xml.sax.handler.feature_namespaces, 0)# turn off namepsaces
    parser1.setContentHandler(descHandler())
    parser1.parse('mesh_desc2019.xml')
    print('mesh_desc2019.xml processed!')
    print 'number of meshids:', len(dict_meshs)
    
    with open('dict_meshs.json','w') as f1:
        json.dump(dict_meshs, f1)
    return dict_meshs
def get_sents(pmid_meshid):
    all_sents = {}
    print 'number of pmids:', len(pmid_meshid)
    print("Loading Pubmed sentences...")
    for y in range(70):
        print(2015 - y)
        ye = str(2015 - y)
        name = "pubmed_sent/pubmed_sent_" + ye + ".csv"
        with open(name,'r') as infile:
            reader = csv.DictReader(infile)
            for line in reader:
                pmid = line['id'].split('_')
                if pmid[0] in pmid_meshid:
                    all_sents.setdefault(pmid[0], {})
                    all_sents[pmid[0]][line['id']] = line['sent']#{pmid:{x_1:_______,x_2:_______,...},...}
    print 'These docs not collected:'
    for i in pmid_meshid:
        if i not in all_sents:
            print i
    print 'closed.\n'
    # print(all_sents['10070974'])
    print('All papers imported.')
    print 'number of docs:', len(all_sents)

    with open('all_sents.json', 'w') as fo:
        json.dump(all_sents, fo)
    return all_sents
def get_all_pos(pmid_meshid, dict_meshs, all_sents):
    #获取IR的pmid-class-term
    IR = []
    with open('IR.txt', 'r') as fIR:
        for i in fIR.readlines():
            IR.append(i.strip())#[IR1,IR2,...]
    
    # 获取mesh的pmid-class-term
    meshid_terms = {}
    #print 'get meshid_term'
    for i in dict_meshs:
        meshid_terms[i] = [dict_meshs[i]['class']] + list(set(dict_meshs[i]['terms'] + [dict_meshs[i]['Name']]))#{meshid:[A,term1,term2,...],...}
    del meshid_terms['D011839'], meshid_terms['D000512'], meshid_terms['D001610'], meshid_terms['D005720']#delete IR
    print 'get pmid_term'
    pmid_terms = {}
    for pmid in pmid_meshid:
        pmid_terms[pmid] = {}#{pmid:{A:[term1,term2,...],B:...},...}
        pmid_terms[pmid]['IR'] = IR#{pmid:{IR:[IR1,IR2,...],A:...},...}
        for meshid in pmid_meshid[pmid]:
            if meshid in meshid_terms:
                cla = meshid_terms[meshid][0]
                pmid_terms[pmid].setdefault(cla, [])
                pmid_terms[pmid][cla] += meshid_terms[meshid][1:]#{pmid:{A:[term1,term2,...],B:...},...}
    #             for term in terms:
    #                 pmid_terms[pmid][cla].append(term)#{pmid:{A:[term1,term2,...],B:...},...}
    # print pmid_terms['10520714']

    # 获取基因的pmid-class-term
    pmid_gene = {}#{pmid:{gene1,gene2,...},...}
    with open('gene_dis_pmid_sent1.csv', 'r') as f1:
        r1 = csv.DictReader(f1)
        for i in r1:
            pmid_gene.setdefault(i['doc'], set()).add(i['gene'])# {pmid:{gene1,gene2,...},...}
    with open('../results/gene_synonym.csv', 'r') as f2:
        r2 = csv.DictReader(f2)
        genes = {}#{gene1:[g1,g2,...],...}
        for i in r2:
            genes.setdefault(i['gene'], []).append(i['synonym'])#{gene1:[g1,g2,...],...}
    for i in pmid_gene:#pmid
        x = []
        for j in pmid_gene[i]:#gene in {pmid:{gene1,gene2,...},...}
            x = x + genes[j]#[g11,g12,...,g21,g22,...]
        pmid_terms[i]['GENE'] = x#{pmid:{IR:[IR1,IR2,...],A:...,GENE:...},...}
    # print pmid_terms['10520714']
    #export the pmid-IR/GENE/MeSH original relation
    with open('pmid_terms.json', 'w') as ft:
        json.dump(pmid_terms, ft)
        
    # extracting all terms' position (IR,GENE,MeSH)
    matched_terms ={}#{pmid:{sentid:{A:[[0,5],...],B:...},...},...}
    for pmid in all_sents:
        #print 'pmid:', pmid
        matched_terms[pmid] = {}
        for sentid in all_sents[pmid]:
            #print 'sentid:', sentid
            sent = all_sents[pmid][sentid]
            matched_terms[pmid][sentid] = {}
            for cla in pmid_terms[pmid]:
                for term in pmid_terms[pmid][cla]:
                    term2 = term.lower()
                    l = len(term2)
                    for n in range(0, len(sent)-l):
                        sent2 = sent[n:n+l].lower()
                        if term2 == sent2:
                            if (n == 0) or (sent[n-1] in ''' ([{<+-/&"'._''') and (sent[n+l] in ''' )]}>+-/&"'._,!?;:'''):
                                    matched_terms[pmid][sentid].setdefault(cla, []).append([n,n+l])
    print "all terms' position (IR,GENE,MeSH) got."
    print len(matched_terms)
    with open('matched_terms.json', 'w') as fo:
        json.dump(matched_terms, fo)
    return matched_terms
def term_match(matched_terms, all_sents):
    #os.chdir('/home/ultimate/xuhao/UVGD_data/20190123_data')
    #print len(all_sents)
    with open('../results/sent_table.csv', 'w+') as doc_sent_mesh:
        fileheader = ['sent', 'raw_text', 'matched_text']
        fileout = csv.DictWriter(doc_sent_mesh, fileheader)
        fileout.writeheader()
        for pmid in matched_terms:
            for sentid in matched_terms[pmid]:
                t0 = all_sents[pmid][sentid]
                records = {'sent': sentid, 'raw_text': t0}
                ps_c = []
                ps_A = []
                ps_B = []
                for cla in matched_terms[pmid][sentid]:
                    ps = matched_terms[pmid][sentid][cla]
                    for p in ps:
                        ps_c.append(cla)
                        ps_A.append(p[0])
                        ps_B.append(p[1])
                r = len(ps_c)
                #print 'r:', r, 'len(ps_c,A,B):', len(ps_c), len(ps_A), len(ps_B)
                if r==0:
                    records['matched_text'] = t0
                    fileout.writerow(records)
                elif r==1:
                    records['matched_text'] = t0[:ps_A[0]] + '<span class="term_' + ps_c[0] + '">' + t0[ps_A[0]:ps_B[0]] + '</span>' + t0[ps_B[0]:]
                    fileout.writerow(records)
                else:#jiejue term chonghe de wenti
                    for n in range(r-1):
                        for m in range(n+1,r):
                            if ps_A[n]>ps_A[m]:
                                ps_c[n], ps_c[m] = ps_c[m], ps_c[n]
                                ps_A[n], ps_A[m] = ps_A[m], ps_A[n]
                                ps_B[n], ps_B[m] = ps_B[m], ps_B[n]
                    br = set()# bad record, xuyao delete
                    for n1 in range(r-1):
                        for m1 in range(n1+1,r):
                            if ps_B[n1]>ps_B[m1]:
                                br.add(m1)
                            elif ps_B[n1]>ps_A[m1]+1:
                                ps_B[n1] = ps_A[m1]
                    for x in sorted(list(br), reverse=True):
                        del ps_c[x], ps_A[x], ps_B[x]
                    r = len(ps_c)
                    t1 = t0[:ps_A[0]]
                    for i in range(r-1):
                        t1 = t1 + '<span class="term_' + ps_c[i] + '">' + t0[ps_A[i]:ps_B[i]] + '</span>' + t0[ps_B[i]:ps_A[i+1]]
                    t1 = t1 + '<span class="term_' + ps_c[r-1] + '">' + t0[ps_A[r-1]:ps_B[r-1]] + '</span>' + t0[ps_B[r-1]:]
                    records['matched_text'] = t1
                    fileout.writerow(records)
    print('"sent_table.csv" closed!')
    return
def gene_mesh_tables(dict_meshs, pmid_meshid):
    gene_doc = {}
    with open('gene_dis_pmid_sent1.csv', 'r') as f2:
        r = csv.DictReader(f2)
        for line in r:
            if line['curation_yes'] == '1':
                gene_doc.setdefault(line['gene'], set()).add(line['doc'])
    with open('../results/gene_mesh_table.csv', 'wb') as f4:
        w4 = csv.writer(f4)
        w4.writerow(['gene', 'doc', 'meshname', 'initial'])
        ms = set()
        for i in gene_doc:# gene
            for j in gene_doc[i]:# doc
                for k in pmid_meshid[j]:# meshid
                    if k in dict_meshs:
                        ms.add(k)
                        m = dict_meshs[k]['Name']
                        w4.writerow([i, j, m, m[0].upper()])
    print 'gene_mesh_table.csv completed'
    with open('../results/mesh_term_table.csv', 'wb') as f3:
        w3 = csv.writer(f3)
        w3.writerow(['mesh', 'term'])
        for i in ms:# meshid
            for j in dict_meshs[i]['terms']:# meshterms
                w3.writerow([dict_meshs[i]['Name'], j])
    print 'mesh_term_table.csv completed'
    return
if __name__ == '__main__':
    os.chdir('../raw')
    # step1: get all meshs in pmids
    pmid_meshid = get_mesh()
    with open('pmid_meshid.json', 'r') as f1:
        pmid_meshid = json.load(f1)

    # step2: get mesh's detail of id-name-term-class
    dict_meshs = get_mesh_details(pmid_meshid)
    with open('dict_meshs.json', 'r') as f2:
        dict_meshs = json.load(f2)

    # step3: get all docs
    all_sents = get_sents(pmid_meshid)
    with open('all_sents.json','r') as f3:
        all_sents = json.load(f3)

    # step4: get all terms' position (IR,GENE,MeSH) in sents
    matched_terms = get_all_pos(pmid_meshid, dict_meshs, all_sents)
    with open('matched_terms.json','r') as f3:
        matched_terms = json.load(f3)

    # step5: match and highlight terms in sents
    term_match(matched_terms, all_sents)

    # step6: get gene_mesh_table and mesh_term_table
    gene_mesh_tables(dict_meshs, pmid_meshid)

    print('Done!')