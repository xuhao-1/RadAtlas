# 1: get Literature mined genes from mc.ionradiation_user_curation_history.csv
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))  # Set work dir
setwd('../raw')

ir_MC_sent <- read.csv('mc.ionradiation_user_curation_history.csv')

yes_sents <- ir_MC_sent[ir_MC_sent[,6] == 1,]#所有 yes sent
#所有句子
all_sent <- read.csv('mc.ionradiation_gene_sent.csv')
all_sent <- all_sent[all_sent[,2]%in%yes_sents[,3],]
all_sents <- merge(yes_sents[,-c(1,4)], all_sent[,c(2,4,7)], by = c('main_term', 'sent_id'), all = T)
all_sents[is.na(all_sents[,3]),3] <- all_sents[is.na(all_sents[,3]),6]
all_sents <- all_sents[,-6]
all_sents <- all_sents[!duplicated(all_sents),]
write.table(all_sents, 'IR_results.txt', sep = '\t', quote = F)

genes <- yes_sents[,3]
genes <- as.character(genes[!duplicated(genes)])#所有yes基因
write(genes, 'IR_yes_genes.txt')

sents <- all_sents[,2]
sents <- as.character(sents[!duplicated(sents)])#所有句子
write(sents, 'IR_sents.txt')

gene_dis_pmid_sent <- all_sents
colnames(gene_dis_pmid_sent) <- c('gene', 'sent', 'term', 'curation_yes', 'curation_no')
gene_dis_pmid_sent[,'doc'] <- apply(gene_dis_pmid_sent, 1, function(x) strsplit(as.character(x['sent']),'_')[[1]][[1]])
# gene_dis_pmid_sent <- gene_dis_pmid_sent[!duplicated(gene_dis_pmid_sent),]
write.csv(gene_dis_pmid_sent, 'gene_dis_pmid_sent1.csv', row.names = F)

docs <- gene_dis_pmid_sent[,'doc']
docs <- as.character(docs[!duplicated(docs)])#所有句子
write(docs, 'IR_docs.txt')
# View(docs)