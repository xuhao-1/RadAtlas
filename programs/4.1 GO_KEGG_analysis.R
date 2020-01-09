library(DOSE)
library(GO.db)
library(org.Hs.eg.db)
library(clusterProfiler)
library(biomaRt)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))  # Set work dir


## PART 1: GO & KEGG analyses
setwd('../raw/GO_KEGG')
human <- useMart("ensembl", dataset = "hsapiens_gene_ensembl")
gs <- list()
gs[[1]] <- as.character(read.table('../IR_yes_genes.txt')[,1])
gs[[2]] <- as.character(read.table('../gene_omics.txt')[,1])
for (i in c(1,2)){
  genes <- gs[[i]]
  genes <- getBM(attributes = c("hgnc_symbol", "ensembl_gene_id", "entrezgene_id"),
                  filters = "hgnc_symbol",
                  values = genes,
                  mart = human)
  # write.csv(genes[[2]], 'man.csv')
  ##GO ontology analysis
  gene <- as.character(genes[,3])
  ego <- enrichGO(gene          = gene,
                  OrgDb         = org.Hs.eg.db,
                  ont           = 'BP',
                  pAdjustMethod = "BH",
                  pvalueCutoff  = 0.01,
                  qvalueCutoff  = 0.05,
                  readable      = TRUE)
  write.table(ego,
              file  = paste0("enr_GO_BP", i, ".txt"),
              quote = FALSE, sep = "\t")
  }
  ## kegg ontology analysis
  
  kk <- enrichKEGG(gene         = gene,
                   organism     = 'hsa',
                   pvalueCutoff = 0.05)
  kk <- setReadable(kk, org.Hs.eg.db, keyType = 'ENTREZID')
                        # transform the genes in the KEGG results for ID to name.
                        # interestingly, the entrezgene = entrezid = kegg in some organisms,
                        # but not in the same db, so entrezid is good, but not that two
  write.table(kk, file = paste0("enr_KEGG", i, ".txt"),
              quote = FALSE, sep = "\t")

}
go_bp <- read.table('enr_GO_BP1.txt', sep = '\t', quote = "")
go_bp[,'enrRatio'] <- apply(go_bp, 1, function(x) eval(parse(text = paste(x[3], '/(', x[4], ')'))))
# go_bp <- go_bp[go_bp[,'enrRatio'] >= 9,]
write.table(go_bp, 'enr_GO_BP_p1.txt',quote = FALSE, sep = "\t")

go_bp <- read.table('enr_GO_BP2.txt', sep = '\t', quote = "")
go_bp[,'enrRatio'] <- apply(go_bp, 1, function(x) eval(parse(text = paste(x[3], '/(', x[4], ')'))))
# go_bp <- go_bp[go_bp[,'enrRatio'] >= 9,]
write.table(go_bp, 'enr_GO_BP_p2.txt',quote = FALSE, sep = "\t")



