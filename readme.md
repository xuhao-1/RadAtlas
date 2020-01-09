The programs and algorithms for construction of RadAtlas
======
_Environment: R version 3.5.2, RStudio Version 1.1.456, Python 2.7.6, Eclipse Platform Version: Photon (4.8)_  
_The programs should be run in order._

I: Details of self-developed bio-entity recognizer are in 'bio_entity_recognizer' folder.

II. Programs used in data processes are stored in 'programs' folder.  
1. get genes from literature mining and manual curation  	
2. get genes from differentially expressed genes and MySQL tables: "gene_table.csv", "gene_dis_pmid_sent.csv"  	
3. get genes' synonyms table "gene_synonym.csv"  	
4. get GO and KEGG analysis results: "gene_go_table.csv", "gene_pathway_table.csv"  	
5. get SNPs for genes: "gene_snp_table.csv"  	
6. get terms in sentences highlighted, and MeSH terms associated to genes: "sent_table.csv", "gene_mesh_table.csv", "mesh_term_table.csv"  
7. get expression data for differentially expressed genes: "datasets_value_table.csv"




