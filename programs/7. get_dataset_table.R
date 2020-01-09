# 为所有DEG作表达图象
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))  # Set work dir
setwd('../raw/datasets')
fs <- list.files(pattern = 'EXP*')
genes <- read.csv('../../results/gene_dis_pmid_sent.csv')[,c(1,2)]
genes <- genes[genes[,2] >1,]
genes <- genes[!duplicated(genes[,1]),1]
f1 <- function(x){
  t <- read.csv(x)
  t[,1] <- toupper(t[,1])
  t <- t[(t[,1] %in% genes),]
  return(t)
}
exprs <- lapply(fs, f1)
exprs2 <- data.frame(genes)
lapply(1:5, function(x) exprs2 <<- merge(exprs2, exprs[[x]], by.x = 1, by.y = 1, all = TRUE))
rownames(exprs2) <- exprs2[,1]
exprs2 <- exprs2[,-1]
# write.csv(exprs2[,-1], '../exprs_table.csv')


detail <- read.csv('../dataset_detail_v2.csv')
rownames(detail) <- detail[,2]
# detail2 <- t(as.matrix(detail))
# write.csv(detail1, '../sample_detail_table.csv')
detail <- detail[,c(1, 5:7)]
detail[,'title'] <- paste(detail[,1], detail[,4], sep = c('_'))
detail <- detail[,c(5, 2, 3)]
group_list <- paste(detail[,1], detail[,2], detail[,3], sep = c('_'))
groupM <- model.matrix(~0 + factor(group_list))
groupM[groupM == 0] <- NA
rownames(groupM) <- rownames(detail)
colnames(groupM) <- levels(factor(group_list))

# v <- as.matrix(exprs2) %*% as.matrix(groupM)
m <- apply(exprs2, 1, function(x) apply(groupM, 2, function(x2) mean(x*x2, na.rm = T)))
sd <- apply(exprs2, 1, function(x) apply(groupM, 2, function(x2) sd(x*x2, na.rm = T)))
# write.csv(t(as.matrix(m)), '../mean_table.csv')
# write.csv(t(as.matrix(sd)), '../standardDeviation_table.csv')

result <- cbind(do.call(rbind, as.list(m)), do.call(rbind, as.list(sd)))
result <- as.data.frame(result)

result[,'gene'] <- rep(colnames(m), each = 32)
result[,'title'] <- rownames(m)
result[,c('geoid', 'condition', 'dose', 'timepoint')] <- do.call(rbind, strsplit(result[,4],'_'))[,c(1,2,3,4)]
result[,'error1'] <- result[,1] - result[,2]
result[,'error2'] <- result[,1] + result[,2]
result[,'mean'] <- result[,1]

# result[3,1] - result[3,2]
# result[,'meancol'] <- paste0('[', result[,6], ', ', result[,1], ']')
# result[,'errorbar'] <- paste0('[', result[,6], ', ', result[,8], ', ', result[,9], ']')

# colnames(result) <- c('mean', 'errorbar', 'gene', 'title', 'geoid', 'dose', 'timepoint')
result <- result[,c(3,4,5,6,7,8,11,9,10)]

# select_dataset <- read.csv('select_dataset_v2.csv')
# select_dataset <- as.character(select_dataset[,'title'])
# result <- result[(result[,'title'] %in% select_dataset),]
epr <- result[,c(7:9)]
epr[is.na(epr)] <- '\\N'
epr[epr == -Inf] <- '\\N'
epr[epr == 0] <- '\\N'
result[,c(7:9)] <- epr
write.csv(result, '../../results/datasets_value_table.csv', row.names = F)





