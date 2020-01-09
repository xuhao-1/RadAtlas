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
def get_snp():
    snps = {}
    with open('snp_result.txt', 'r') as f1:
        for line in f1:
            if '[Homo sapiens]' in line:
                SNPid = re.split(r'[. ][ ]', line)[1]
            if 'Gene:' in line:
                gene = line[5:].strip()
                snps.setdefault(SNPid,[]).append(gene)
    print 'snp number:', len(snps)
    with open('../results/gene_snp_table.csv', 'wb') as f2:
        w = csv.writer(f2)
        w.writerow(['gene', 'SNPid'])
        for i in snps:# SNPid
            for j in snps[i]:# gene
                w.writerow([j, i])
    return
if __name__ == '__main__':
    os.chdir('../raw')
    get_snp()
    print 'Done!'
    
    
    
    
    
    
    
    
    
    
    
