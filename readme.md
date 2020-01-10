The programs and algorithms for construction of RadAtlas
======
_Environment: R version 3.5.2, RStudio Version 1.1.456, Python 2.7.6, Eclipse Platform Version: Photon (4.8)_

The programs should be run in order.

I: Details of self-developed bio-entity recognizer are in 'bio_entity_recognizer' folder.  
1. create_index_sent.py,  
Indexer  
2. type_sent.py, term_sent.py, nlp_sent.py,  
Analyser, ```python type_sent.py ionizing_radiation.obo```  
3. synonym_sent.py  
5. search_sent.py  
7. match_sent.py,  
```nohup python match_sent.py ontology1 ontology2 ontology3 &```

II. Programs used in data processes are stored in 'programs' folder.  
1. get_LM_genes.R,  
to get genes from literature mining and manual curation  	
2. get DEGs gene & table.R,  
to get genes from differentially expressed genes and MySQL tables: "gene_table.csv", "gene_dis_pmid_sent.csv"  	
3. get_synonym.py,  
to get genes' synonyms table "gene_synonym.csv"  	
4. GO_KEGG_analysis.R, get_go_kegg_tables_p1.py, get_GO_KEGG_tables_p2.R,  
to get GO and KEGG analysis results: "gene_go_table.csv", "gene_pathway_table.csv"  	
5. get_snp_table.py,  
to get SNPs for genes: "gene_snp_table.csv"  	
6. get_all_term_highlight.py,  
to get terms in sentences highlighted, and MeSH terms associated to genes: "sent_table.csv", "gene_mesh_table.csv", "mesh_term_table.csv"  
7. get_dataset_table.R,  
to get expression data for differentially expressed genes: "datasets_value_table.csv"




