library(DOSE)
library(GO.db)
library(org.Hs.eg.db)
library(clusterProfiler)
library(biomaRt)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))  # Set work dir


setwd('../raw/GO_KEGG')
## PART 2: get GO_KEGG_tables
go_p1 <- read.csv("gene_go_table_p1.csv")
go_p2 <- read.csv("gene_go_table_p2.csv")
gos <- merge(go_p1, go_p2, by = c('gene', 'goid', 'goterm', 'initial'), all = T)
gos[is.na(gos)] <- 0
gos[,'source'] <- gos$source.x + gos$source.y
gos <- gos[, c(-5, -6)]
write.csv(gos, "../../results/gene_go_table.csv", row.names = F)

kegg_p1 <- read.csv("gene_pathway_table_p1.csv")
kegg_p2 <- read.csv("gene_pathway_table_p2.csv")
keggs <- merge(kegg_p1, kegg_p2, by = c('gene', 'pathwayid', 'pathwayterm'), all = T)
keggs[is.na(keggs)] <- 0
keggs$source <- keggs$source.x + keggs$source.y
keggs <- keggs[, c(-4, -5)]
write.csv(keggs, "../../results/gene_pathway_table.csv", row.names = F)


# 3. 绘图,enrichment ratio 条目比较
genes <- as.character(read.table('../IR_yes_genes.txt')[,1])
human <- useMart("ensembl", dataset = "hsapiens_gene_ensembl")
genes <- getBM(attributes = c("hgnc_symbol", "ensembl_gene_id", "entrezgene_id"),
               filters = "hgnc_symbol",
               values = genes,
               mart = human)
gene <- as.character(genes[,3])
##GO ontology analysis
ego <- enrichGO(gene          = gene,
                OrgDb         = org.Hs.eg.db,
                ont           = "BP",
                pAdjustMethod = "BH",
                pvalueCutoff  = 0.01,
                qvalueCutoff  = 0.05,
                readable      = TRUE)
# ego@result$source <- 'LM'
# ego@result$enrRatio <- apply(ego@result, 1, function(x) eval(parse(text = paste(x[3], '/(', x[4], ')'))))
# ego@result <- ego@result[order(ego@result$enrRatio, decreasing = T),]
# 按照enrRatio排序
write.table(ego,
            file  = paste0("enr_GOBP_LM1.csv"),
            quote = T, sep = ",")
# 对table进行排序后重新读入
x <- read.csv("enr_GOBP_LM2.csv")
ego@result <- x[order(x$rank),]

ekg <- enrichKEGG(gene         = gene,
                  organism     = 'hsa',
                  pvalueCutoff = 0.05)
ekg <- setReadable(ekg, org.Hs.eg.db, keyType = 'ENTREZID')
ekg@result$enrRatio <- apply(ekg@result, 1, function(x) eval(parse(text = paste(x[3], '/(', x[4], ')'))))
ekg@result <- ekg@result[order(ekg@result$enrRatio, decreasing = T),]
# kegg 按照enrRatio排序好看，所以选enrRatio 作图
# transform the genes in the KEGG results for ID to name.
# interestingly, the entrezgene = entrezid = kegg in some organisms,
# but not in the same db, so entrezid is good, but not that two
write.table(ekg, file = paste0("enr_KEGG_LM1.csv"),
            quote = T, sep = ",")
# 对table进行排序后重新读入
x <- read.csv("enr_KEGG_LM2.csv")
ekg@result <- x[order(x$rank),]

pdf('go.pdf', 10, 8)
# print(dotplot(ego, showCategory=30)) # generatio好像没啥用
# print(emapplot(ego, showCategory = 30))
print(cnetplot(ego, showCategory = 5))
dev.off()
pdf('kegg.pdf', 10, 5)
# print(emapplot(ekg, showCategory = 30))
print(cnetplot(ekg, showCategory = 5))
dev.off()



library(ggplot2)
gos <- ego@result[c(1:20),]
kgs <- ekg@result[c(1:20),]
f <- function(){
  g <- ggplot(data = gos, mapping = aes(Description, Count, fill = log10(p.adjust))) +
    geom_bar(stat = 'identity') +
    labs(x = 'GO Biological Processes', y = 'Gene Number', fill = 'lgP') +
    coord_flip() +
    scale_x_discrete(limits = rev(gos$Description)) +
    scale_fill_gradient2(high = 'blue', low = 'red')
    # scale_fill_gradientn(colours = c('#9BC3D3','#F47C79','#F25F5C'), values = c(0,0.3,1))
  k <- ggplot(data = kgs, mapping = aes(Description, Count, fill = log10(p.adjust))) +
    geom_bar(stat = 'identity') +
    labs(x = 'KEGG Pathways', y = 'Gene Number', fill = 'lgP') +
    coord_flip() +
    scale_x_discrete(limits = rev(kgs$Description)) +
    scale_fill_gradient2(high = 'blue', low = 'red')
    # scale_fill_gradientn(colours = c('#247BA0','#FCE1E1','#F25F5C'))
  pdf('go2.pdf', 10, 5)
  print(g)
  dev.off()
  pdf('kegg2.pdf', 10, 5)
  print(k)
  dev.off()
}
f()
}






if(F){
  ggplot(data = gos, mapping = aes(Description, enrRatio, fill = -log10(p.adjust))) +
    geom_bar(stat = 'identity') +
    labs(x = 'GO Biological Processes', y = 'Enrichment Ratio', fill = '-lgP') +
    coord_flip() +
    scale_x_discrete(limits = rev(gos$Description)) +
    scale_fill_gradientn(colours = c('blue','#f28383','#f53131','red'), values = c(-1,0,0.3,1))
  
  ggplot(data = kgs, mapping = aes(Description, enrRatio, fill = -log10(p.adjust))) +
    geom_bar(stat = 'identity') +
    labs(x = 'KEGG Pathways', y = 'Enrichment Ratio', fill = '-lgP') +
    coord_flip() +
    scale_x_discrete(limits = rev(kgs$Description)) +
    scale_fill_gradientn(colours = c('#1EA896','#ECF8B5','#FF715B'))
}










