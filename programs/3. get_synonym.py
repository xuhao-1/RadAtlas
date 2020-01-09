# -*- coding: utf-8 -*-
'''-----------------------------------------

purpose: get genes' synonyms
-----------------------------------------'''
import os
import csv
import json
import sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')
def get_gene_synonym():
    ## 获取所有基因的同义词
    genes = []
    with open('../results/gene_table2.csv', 'r') as f1:
        g0 = csv.DictReader(f1)
        for g in g0:
            genes.append(g['id'])
        print 'genes number:', len(genes)
    gene_synonym = {}
    with open('proteingene.obo', 'r') as f2:
        for line in f2:
            x = line.split(': ')
            if x[0] == 'name':
                gn = x[1].strip()
                if gn in genes:
                    gene_synonym[gn] = []
                    lows = [] # yongyi panduan tongyici shifou chongfu
                else:
                    gn = ''
            if x[0] == 'synonym' and gn != '':
                synm = x[1].split('"')[1]
                if synm.lower() not in lows:
                    gene_synonym[gn].append(synm)
                    lows.append(synm.lower())
    print 'gene_synonym number:', len(gene_synonym)
    for i in genes:
        if i not in gene_synonym:
            gene_synonym[i] = [i]
    with open('../gene_synonym.csv', 'wb') as f3:
        w = csv.writer(f3)
        #先写入columns_name
        w.writerow(["gene","synonym","initial"])
        for i in genes:
            if i in gene_synonym:
                for j in gene_synonym[i]:
                    w.writerow([i, j, i[0].upper()])
            else:
                w.writerow([i,i,i[0].upper()])
    return
if __name__ == '__main__':
    os.chdir('../raw') 
    get_gene_synonym()
    print 'Done!'
    
    
    
    
    
    
    
    
    
    
    
