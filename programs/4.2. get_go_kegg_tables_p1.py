# -*- coding: utf-8 -*-
'''-----------------------------------------

purpose:
files in:
files out:
Created on 20190125, @author: lab
-----------------------------------------'''
import os
import csv
import json
import sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')
def get_goBP_KEGG():
    genes = []
    with open('../results/gene_table.csv', 'r') as f1:
        g0 = csv.DictReader(f1)
        for g in g0:
            genes.append(g['id'])
    #print genes
    for s in ['1','2']:
        #get goBP
        goBP = {}
        with open('GO_KEGG/enr_GO_BP_p'+s+'.txt', 'r') as f1:
            for line in f1:
                line = line.split('\t')
                goBP[line[0]] = [line[2]] + line[8].split('/')
            del goBP['ID']
        #print goBP['GO:0044774']
        gene_BP = {}
        for i in goBP:# GO
            for j in goBP[i][1:]:# gene in goBP[GO]
                if j in genes:
                    gene_BP.setdefault(j,[]).append(i)
        print 'number of gene with goBP:', len(gene_BP)
        with open('GO_KEGG/gene_go_table_p'+s+'.csv', 'wb') as f2:
            w = csv.writer(f2)
            w.writerow(['gene', 'goid', 'goterm', 'initial', 'source'])
            for i in gene_BP:# gene
                for j in gene_BP[i]:# goBP
                    w.writerow([i, j, goBP[j][0], goBP[j][0][0].upper(), s])
        # get KEGG
        KG = {}
        with open('GO_KEGG/enr_KEGG'+s+'.txt', 'r') as f1:
            for line in f1:
                line = line.split('\t')
                KG[line[0]] = [line[2]] + line[8].split('/')
            del KG['ID']
        #print goBP['GO:0044774']
        gene_KG = {}
        for i in KG:# kegg
            for j in KG[i][1:]:# gene in KG[kegg]
                if j in genes:
                    gene_KG.setdefault(j,[]).append(i)
        print 'number of gene with KEGG:',len(gene_KG)
        with open('GO_KEGG/gene_pathway_table_p'+s+'.csv', 'wb') as f2:
            w = csv.writer(f2)
            w.writerow(['gene', 'pathwayid', 'pathwayterm', 'source'])
            for i in gene_KG:# gene
                for j in gene_KG[i]:# KG
                    w.writerow([i, j, KG[j][0], s])
    return
if __name__ == '__main__':
    os.chdir('../raw')
    get_goBP_KEGG()
    print 'Done!'
    
    
    
    
    
    
    
    
    
    
    
