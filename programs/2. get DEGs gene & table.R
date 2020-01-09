# get differentially expressed genes
# from mc.ionradiation_user_curation_history.csv
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))  # Set work dir

library(GEOquery)
library(limma)


## PART 1. get DEGs
setwd('../raw/datasets')
if(T){
  GSE23393 = function(gse){
    gse <- "GSE23393"    #目标GSE
    # data
    gGEO <- getGEO(gse, destdir = ".")##获取GEO数据
    gset <- gGEO[[1]]#class(gset)
    exprSet <- exprs(gset)#original ES
    exprSet <- as.data.frame(na.omit(exprSet)) #得到数据框geshi
    #exprSet <- log2(exprSet) #得到数据框geshi
    
    
    pdata <- pData(gset)#样本信息
    fdata <- fData(gset)#探针信息
    # detail <- read.csv('20190306_detail.csv')
    # detail <- detail[detail[,1] == gse, ]
    # plot, QC-test
    plot_bp <- function(){
      par(cex = 0.7)#graphical parameters
      n.sample <- ncol(exprSet)
      if(n.sample > 40) par(cex = 0.5)
      cols <- rainbow(n.sample * 1.2)
      boxplot(exprSet, col = cols, main = "expression value", las = 2)
    }
    plot_bp()##QC检测
    # gene-probe
    exprSet1 <-merge(fdata[, c(1, 7)], exprSet, by.x = "ID", by.y = "row.names", all.y = T)[, -1]
    # remove the duplicated, non-specific and non-gene probesets
    rmDupID <- function(a){
      sums <- rowSums(a[, -1])
      a<- a[order(sums, decreasing=T),]#probe sort by expr level
      a<- a[!duplicated(a[,1]),]#去除重复探针，保留表达值最大的探针数据
      a<- a[!is.na(a[,1]),]#去除非基因探针
      a<- a[!is.null(a[,1]),]#去除非基因探针
      a<- a[nchar(a[,1])!=0,]#去除非基因探针
      a<- a[!grepl("---", a[,1]),]#去除非基因探针
      a<- a[!grepl("///", a[,1]),]#去除非特异性探针
      rownames(a)<- a[,1]
      a<- a[,-1]
      return(a)
    }
    exprSet2<-rmDupID(exprSet1)
    # ##分组
    # desMatx <- function(){
    #   group_list <- rep(c('0Gy', '1.25Gy'), 8)
    #   ##制作设计矩阵
    #   design <- model.matrix(~0 + factor(group_list))
    #   colnames(design) <- levels(factor(group_list))
    #   rownames(design) <- rownames(pdata)
    #   return(design)
    # }
    # design <- desMatx()
    # groups <- colnames(design)
    # print(groups)
    # 
    
    
    # remake design matrix
    desMatx <- function(){
      ind <- rep(c('A','B','C','D','E','F','G','H'), each = 2)# individual
      treat <- rep(c('C','R'), 8)# concrol, irradiated
      ##制作设计矩阵
      design <- model.matrix(~ind + treat)
      rownames(design) <- rownames(pdata)
      return(design)
    }
    design <- desMatx()
    groups <- colnames(design)
    print(groups)
    # ##制作差异比较矩阵
    # contMatx <- function(){
    #   sibship <- c(1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8)
    #   treat <- rep(c(1,2), 8)
    #   contrast_m <- list()
    #   contrast_m[[1]] <- makeContrasts(
    #     paste(groups[2], groups[1], sep = '-'),
    #     levels = design
    #     )
    #   colnames(contrast_m[[1]])[1] = 'Homo_sapiens.peripheral_blood.0_1.25Gy.4h.TBI'
    #   return(contrast_m)
    # }
    # contrast_m <- contMatx()
    # View(contrast_m[[1]])
    #limma包进行差异分析
    fit <- lmFit(exprSet2, design)#使用去重后的表达矩阵进行linear model
    fit2 <- eBayes(fit)
    
    tempOut <-  topTable(fit2, coef = 'treatR', n = 2000, adjust.method = 'BH') #jin bijiao liangzu zhijian
    #tempOut <-  topTableF(fit2, lfc = 1, n = 2000, adjust = "BH") #duozu zhijian bijiao
    results <- decideTests(fit2, method = 'separate')#duochong jianyan jiaozheng
    summary(results)
    #vennDiagram(results)
    
    write.csv(tempOut, paste0("genes_", gse, ".csv"), quote = F)
  }
  rm(list = ls())
  GSE43310 = function(gse){
    gse <- "GSE43310"    #目标GSE
    # data
    gGEO <- getGEO(gse, destdir = ".")##获取GEO数据
    gset <- gGEO[[1]]#class(gset)
    exprSet <- exprs(gset)#original ES
    exprSet <- as.data.frame(na.omit(exprSet)) #得到数据框geshi
    #exprSet <- log2(exprSet) #得到数据框geshi
    
    
    pdata <- pData(gset)#样本信息
    fdata <- fData(gset)#探针信息
    # detail <- read.csv('20190306_detail.csv')
    # detail <- detail[detail[,1] == gse, ]
    # plot, QC-test
    plot_bp <- function(){
      par(cex = 0.7)#graphical parameters
      n.sample <- ncol(exprSet)
      if(n.sample > 40) par(cex = 0.5)
      cols <- rainbow(n.sample * 1.2)
      boxplot(exprSet, col = cols, main = "expression value", las = 2)
    }
    plot_bp()##QC检测
    # gene-probe
    exprSet1 <-merge(fdata[, c(1, 7)], exprSet, by.x = "ID", by.y = "row.names", all.y = T)[, -1]
    # remove the duplicated, non-specific and non-gene probesets
    rmDupID <- function(a){
      sums <- rowSums(a[, -1])
      a<- a[order(sums, decreasing=T),]#probe sort by expr level
      a<- a[!duplicated(a[,1]),]#去除重复探针，保留表达值最大的探针数据
      a<- a[!is.na(a[,1]),]#去除非基因探针
      a<- a[!is.null(a[,1]),]#去除非基因探针
      a<- a[nchar(a[,1])!=0,]#去除非基因探针
      a<- a[!grepl("---", a[,1]),]#去除非基因探针
      a<- a[!grepl("///", a[,1]),]#去除非特异性探针
      rownames(a)<- a[,1]
      a<- a[,-1]
      return(a)
    }
    exprSet2<-rmDupID(exprSet1)
    # ##分组
    # desMatx <- function(){
    #   group_list <- rep(c('0Gy', '1.25Gy'), 8)
    #   ##制作设计矩阵
    #   design <- model.matrix(~0 + factor(group_list))
    #   colnames(design) <- levels(factor(group_list))
    #   rownames(design) <- rownames(pdata)
    #   return(design)
    # }
    # design <- desMatx()
    # groups <- colnames(design)
    # print(groups)
    # 
    
    
    # remake design matrix
    desMatx <- function(){
      ind <- rep(c('A','B','C','D','E','F','G','H'), each = 3)# individual
      # treat <- rep(c('C','R'), 8)# concrol, irradiated
      ##制作设计矩阵
      design <- model.matrix(~0 + ind)
      rownames(design) <- rownames(pdata)
      return(design)
    }
    design <- desMatx()
    groups <- colnames(design)
    print(groups)
    # ##制作差异比较矩阵
    # contMatx <- function(){
    #   sibship <- c(1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8)
    #   treat <- rep(c(1,2), 8)
    #   contrast_m <- list()
    #   contrast_m[[1]] <- makeContrasts(
    #     paste(groups[2], groups[1], sep = '-'),
    #     levels = design
    #     )
    #   colnames(contrast_m[[1]])[1] = 'Homo_sapiens.peripheral_blood.0_1.25Gy.4h.TBI'
    #   return(contrast_m)
    # }
    # contrast_m <- contMatx()
    # View(contrast_m[[1]])
    contrast_m1 <- makeContrasts(
      indB-indA, indC-indA, indD-indA, indC-indB, indD-indB, indD-indC,
      levels = design)
    contrast_m2 <- makeContrasts(
      indF-indE, indG-indE, indH-indE, indG-indF, indH-indF, indH-indG,
      levels = design)
    #limma包进行差异分析
    fit <- lmFit(exprSet2, design)#使用去重后的表达矩阵进行linear model
    fit2 <- contrasts.fit(fit, contrast_m1)
    fit2 <- eBayes(fit2)
    
    # tempOut <-  topTable(fit2, coef = 'treatR', n = 2000, adjust.method = 'BH') #jin bijiao liangzu zhijian
    tempOut <-  topTableF(fit2, lfc = 1, n = 2000, adjust = "BH") #duozu zhijian bijiao
    results <- decideTests(fit2, method = 'separate')#duochong jianyan jiaozheng
    summary(results)
    #vennDiagram(results)
    write.csv(tempOut, paste0("genes1_", gse, ".csv"), quote = F)
    
    
    fit <- lmFit(exprSet2, design)#使用去重后的表达矩阵进行linear model
    fit2 <- contrasts.fit(fit, contrast_m2)
    fit2 <- eBayes(fit2)
    
    # tempOut <-  topTable(fit2, coef = 'treatR', n = 2000, adjust.method = 'BH') #jin bijiao liangzu zhijian
    tempOut <-  topTableF(fit2, lfc = 1, n = 2000, adjust = "BH") #duozu zhijian bijiao
    results <- decideTests(fit2, method = 'separate')#duochong jianyan jiaozheng
    summary(results)
    #vennDiagram(results)
    write.csv(tempOut, paste0("genes2_", gse, ".csv"), quote = F)
  }
  rm(list = ls())
  GSE57059 = function(gse){
    gse <- "GSE57059"    #目标GSE
    # data
    gGEO <- getGEO(gse, destdir = ".")##获取GEO数据
    gset <- gGEO[[1]]#class(gset)
    exprSet <- exprs(gset)#original ES
    exprSet <- as.data.frame(na.omit(exprSet)) #得到数据框geshi
    exprSet <- log2(exprSet) #得到数据框geshi
    
    
    pdata <- pData(gset)#样本信息
    fdata <- fData(gset)#探针信息
    # detail <- read.csv('20190306_detail.csv')
    # detail <- detail[detail[,1] == gse, ]
    # plot, QC-test
    plot_bp <- function(){
      par(cex = 0.7)#graphical parameters
      n.sample <- ncol(exprSet)
      if(n.sample > 40) par(cex = 0.5)
      cols <- rainbow(n.sample * 1.2)
      boxplot(exprSet, col = cols, main = "expression value", las = 2)
    }
    plot_bp()##QC检测
    # gene-probe
    exprSet1 <-merge(fdata[, c(1, 7)], exprSet, by.x = "ID", by.y = "row.names", all.y = T)[, -1]
    # remove the duplicated, non-specific and non-gene probesets
    rmDupID <- function(a){
      sums <- rowSums(a[, -1])
      a<- a[order(sums, decreasing=T),]#probe sort by expr level
      a<- a[!duplicated(a[,1]),]#去除重复探针，保留表达值最大的探针数据
      a<- a[!is.na(a[,1]),]#去除非基因探针
      a<- a[!is.null(a[,1]),]#去除非基因探针
      a<- a[nchar(a[,1])!=0,]#去除非基因探针
      a<- a[!grepl("---", a[,1]),]#去除非基因探针
      a<- a[!grepl("///", a[,1]),]#去除非特异性探针
      rownames(a)<- a[,1]
      a<- a[,-1]
      return(a)
    }
    exprSet2<-rmDupID(exprSet1)
  
    
    # remake design matrix
    desMatx <- function(){
      ind <- rep(c('S60','S610','S240','S2410','M60','M610','M240','M2410'), each = 3)# individual
      ##制作设计矩阵
      design <- model.matrix(~0 + ind)
      rownames(design) <- rownames(pdata)
      return(design)
    }
    design <- desMatx()
    groups <- colnames(design)
    print(groups)
    # ##制作差异比较矩阵
    contrast_m1 <- makeContrasts(
      indS610-indS60, indS2410-indS240, (indS2410-indS240)-(indS610-indS60),
      levels = design)
    contrast_m2 <- makeContrasts(
      indM610-indM60, indM2410-indM240, (indM2410-indM240)-(indM610-indM60),
      levels = design)
    #limma包进行差异分析
    fit <- lmFit(exprSet2, design)#使用去重后的表达矩阵进行linear model
    fit2 <- contrasts.fit(fit, contrast_m1)
    fit2 <- eBayes(fit2)
    
    # tempOut <-  topTable(fit2, coef = 'treatR', n = 2000, adjust.method = 'BH') #jin bijiao liangzu zhijian
    tempOut <-  topTableF(fit2, lfc = 1, n = 2000, adjust = "BH") #duozu zhijian bijiao
    results <- decideTests(fit2, method = 'separate')#duochong jianyan jiaozheng
    summary(results)
    #vennDiagram(results)
    write.csv(tempOut, paste0("genes1_", gse, ".csv"), quote = F)
    
    
    fit <- lmFit(exprSet2, design)#使用去重后的表达矩阵进行linear model
    fit2 <- contrasts.fit(fit, contrast_m2)
    fit2 <- eBayes(fit2)
    
    # tempOut <-  topTable(fit2, coef = 'treatR', n = 2000, adjust.method = 'BH') #jin bijiao liangzu zhijian
    tempOut <-  topTableF(fit2, lfc = 1, n = 2000, adjust = "BH") #duozu zhijian bijiao
    results <- decideTests(fit2, method = 'separate')#duochong jianyan jiaozheng
    summary(results)
    #vennDiagram(results)
    write.csv(tempOut, paste0("genes2_", gse, ".csv"), quote = F)
  }
  rm(list = ls())
  GSE62623 = function(gse){
    gse <- "GSE62623"    #目标GSE
    # data
    gGEO <- getGEO(gse, destdir = ".")##获取GEO数据
    gset <- gGEO[[1]]#class(gset)
    exprSet <- exprs(gset)#original ES
    exprSet <- as.data.frame(na.omit(exprSet)) #得到数据框geshi
    #exprSet <- log2(exprSet) #得到数据框geshi
    
    
    pdata <- pData(gset)#样本信息
    fdata <- fData(gset)#探针信息
    # detail <- read.csv('20190306_detail.csv')
    # detail <- detail[detail[,1] == gse, ]
    # plot, QC-test
    plot_bp <- function(){
      par(cex = 0.7)#graphical parameters
      n.sample <- ncol(exprSet)
      if(n.sample > 40) par(cex = 0.5)
      cols <- rainbow(n.sample * 1.2)
      boxplot(exprSet, col = cols, main = "expression value", las = 2)
    }
    plot_bp()##QC检测
    # gene-probe
    exprSet1 <-merge(fdata[, c(1, 10)], exprSet, by.x = "ID", by.y = "row.names", all.y = T)[, -1]
    # remove the duplicated, non-specific and non-gene probesets
    rmDupID <- function(a){
      sums <- rowSums(a[, -1])
      a<- a[order(sums, decreasing=T),]#probe sort by expr level
      a<- a[!duplicated(a[,1]),]#去除重复探针，保留表达值最大的探针数据
      a<- a[!is.na(a[,1]),]#去除非基因探针
      a<- a[!is.null(a[,1]),]#去除非基因探针
      a<- a[nchar(a[,1])!=0,]#去除非基因探针
      a<- a[!grepl("---", a[,1]),]#去除非基因探针
      a<- a[!grepl("///", a[,1]),]#去除非特异性探针
      rownames(a)<- a[,1]
      a<- a[,-1]
      return(a)
    }
    exprSet2<-rmDupID(exprSet1)
    # ##分组
    desMatx <- function(){
      ind <- c("2GyLDR", "2GyLDR", "0GyLDR", "0GyLDR", "0GyLDR", "4GyLDR", "4GyLDR", "4GyLDR", "4GyLDR", "4GyLDR", "4GyLDR", "0GyHDR", "0GyHDR", "0GyHDR", "1GyHDR", "1GyHDR", "1GyHDR", "1GyHDR", "1GyHDR", "1GyHDR", "2GyHDR", "2GyHDR", "2GyHDR", "2GyHDR", "2GyHDR", "2GyHDR", "4GyHDR", "4GyHDR", "4GyHDR", "4GyHDR", "4GyHDR", "4GyHDR", "0GyHDR", "0GyHDR", "0GyHDR", "1GyLDR", "1GyLDR", "1GyLDR", "1GyLDR", "1GyLDR", "1GyLDR", "0GyLDR", "0GyLDR", "0GyLDR", "2GyLDR", "2GyLDR", "2GyLDR", "2GyLDR")
      ##制作设计矩阵
      design <- model.matrix(~0 + ind)
      rownames(design) <- rownames(pdata)
      return(design)
    }
    design <- desMatx()
    groups <- colnames(design)
    print(groups)
    # ##制作差异比较矩阵
    contrast_m1 <- makeContrasts(
      ind1GyLDR-ind0GyLDR, ind2GyLDR-ind0GyLDR, ind4GyLDR-ind0GyLDR, ind2GyLDR-ind1GyLDR, ind4GyLDR-ind1GyLDR, ind4GyLDR-ind2GyLDR,
      levels = design)
    contrast_m2 <- makeContrasts(
      ind1GyHDR-ind0GyHDR, ind2GyHDR-ind0GyHDR, ind4GyHDR-ind0GyHDR, ind2GyHDR-ind1GyHDR, ind4GyHDR-ind1GyHDR, ind4GyHDR-ind2GyHDR,
      levels = design)
    #limma包进行差异分析
    fit <- lmFit(exprSet2, design)#使用去重后的表达矩阵进行linear model
    fit2 <- contrasts.fit(fit, contrast_m1)
    fit2 <- eBayes(fit2)
    
    # tempOut <-  topTable(fit2, coef = 'treatR', n = 2000, adjust.method = 'BH') #jin bijiao liangzu zhijian
    tempOut <-  topTableF(fit2, lfc = 1, n = 2000, adjust = "BH") #duozu zhijian bijiao
    results <- decideTests(fit2, method = 'separate')#duochong jianyan jiaozheng
    summary(results)
    #vennDiagram(results)
    write.csv(tempOut, paste0("genes1_", gse, ".csv"), quote = F)
    
    
    fit <- lmFit(exprSet2, design)#使用去重后的表达矩阵进行linear model
    fit2 <- contrasts.fit(fit, contrast_m2)
    fit2 <- eBayes(fit2)
    
    # tempOut <-  topTable(fit2, coef = 'treatR', n = 2000, adjust.method = 'BH') #jin bijiao liangzu zhijian
    tempOut <-  topTableF(fit2, lfc = 1, n = 2000, adjust = "BH") #duozu zhijian bijiao
    results <- decideTests(fit2, method = 'separate')#duochong jianyan jiaozheng
    summary(results)
    #vennDiagram(results)
    write.csv(tempOut, paste0("genes2_", gse, ".csv"), quote = F)
  }
  rm(list = ls())
  GSE84041 = function(gse){
    gse <- "GSE84041"    #目标GSE
    # data
    gGEO <- getGEO(gse, destdir = ".")##获取GEO数据
    gset <- gGEO[[1]]#class(gset)
    exprSet <- exprs(gset)#original ES
    exprSet <- as.data.frame(na.omit(exprSet)) #得到数据框geshi
    #exprSet <- log2(exprSet) #得到数据框geshi
    
    
    pdata <- pData(gset)#样本信息
    fdata <- fData(gset)#探针信息
    # detail <- read.csv('20190306_detail.csv')
    # detail <- detail[detail[,1] == gse, ]
    # plot, QC-test
    plot_bp <- function(){
      par(cex = 0.7)#graphical parameters
      n.sample <- ncol(exprSet)
      if(n.sample > 40) par(cex = 0.5)
      cols <- rainbow(n.sample * 1.2)
      boxplot(exprSet, col = cols, main = "expression value", las = 2)
    }
    plot_bp()##QC检测
    # gene-probe
    exprSet1 <-merge(fdata[, c(1, 7)], exprSet, by.x = "ID", by.y = "row.names", all.y = T)[, -1]
    # remove the duplicated, non-specific and non-gene probesets
    rmDupID <- function(a){
      sums <- rowSums(a[, -1])
      a<- a[order(sums, decreasing=T),]#probe sort by expr level
      a<- a[!duplicated(a[,1]),]#去除重复探针，保留表达值最大的探针数据
      a<- a[!is.na(a[,1]),]#去除非基因探针
      a<- a[!is.null(a[,1]),]#去除非基因探针
      a<- a[nchar(a[,1])!=0,]#去除非基因探针
      a<- a[!grepl("---", a[,1]),]#去除非基因探针
      a<- a[!grepl("///", a[,1]),]#去除非特异性探针
      rownames(a)<- a[,1]
      a<- a[,-1]
      return(a)
    }
    exprSet2<-rmDupID(exprSet1)
    # ##分组
    # desMatx <- function(){
    #   group_list <- rep(c('0Gy', '1.25Gy'), 8)
    #   ##制作设计矩阵
    #   design <- model.matrix(~0 + factor(group_list))
    #   colnames(design) <- levels(factor(group_list))
    #   rownames(design) <- rownames(pdata)
    #   return(design)
    # }
    # design <- desMatx()
    # groups <- colnames(design)
    # print(groups)
    # 
    
    
    # remake design matrix
    desMatx <- function(){
      ind <- rep(c('1w0','1w24','1w48','7w0','7w24','7w48'), each = 4)# individual
      ##制作设计矩阵
      design <- model.matrix(~0 + ind)
      rownames(design) <- rownames(pdata)
      return(design)
    }
    design <- desMatx()
    groups <- colnames(design)
    print(groups)
    # ##制作差异比较矩阵
    contrast_m1 <- makeContrasts(
      ind1w24-ind1w0, ind1w48-ind1w0, ind1w48-ind1w24,
      levels = design)
    contrast_m2 <- makeContrasts(
      ind7w24-ind7w0, ind7w48-ind7w0, ind7w48-ind7w24,
      levels = design)
    #limma包进行差异分析
    fit <- lmFit(exprSet2, design)#使用去重后的表达矩阵进行linear model
    fit2 <- contrasts.fit(fit, contrast_m1)
    fit2 <- eBayes(fit2)
    
    # tempOut <-  topTable(fit2, coef = 'treatR', n = 2000, adjust.method = 'BH') #jin bijiao liangzu zhijian
    tempOut <-  topTableF(fit2, lfc = 1, n = 2000, adjust = "BH") #duozu zhijian bijiao
    results <- decideTests(fit2, method = 'separate')#duochong jianyan jiaozheng
    summary(results)
    #vennDiagram(results)
    write.csv(tempOut, paste0("genes1_", gse, ".csv"), quote = F)
    
    
    fit <- lmFit(exprSet2, design)#使用去重后的表达矩阵进行linear model
    fit2 <- contrasts.fit(fit, contrast_m2)
    fit2 <- eBayes(fit2)
    
    # tempOut <-  topTable(fit2, coef = 'treatR', n = 2000, adjust.method = 'BH') #jin bijiao liangzu zhijian
    tempOut <-  topTableF(fit2, lfc = 1, n = 2000, adjust = "BH") #duozu zhijian bijiao
    results <- decideTests(fit2, method = 'separate')#duochong jianyan jiaozheng
    summary(results)
    #vennDiagram(results)
    write.csv(tempOut, paste0("genes2_", gse, ".csv"), quote = F)
  }
  rm(list = ls())
}

#human and mouse genes
xh <- c("genes_GSE23393.csv", "genes1_GSE57059.csv", "genes2_GSE57059.csv")
xm <- c("genes1_GSE43310.csv", "genes1_GSE62623.csv", "genes1_GSE84041.csv",
        "genes2_GSE43310.csv", "genes2_GSE62623.csv", "genes2_GSE84041.csv")
yh <- lapply(xh, function(i) {z <- read.csv(i)[,c('X', 'adj.P.Val')]; return(z[z[,2] <= 0.05,])})
yh2 <- Reduce(function(x, y) merge(x, y, by = 'X', all = T), yh)
ym <- lapply(xm, function(i) {z <- read.csv(i)[,c('X', 'adj.P.Val')]; return(z[z[,2] <= 0.05,])})
ym2 <- Reduce(function(x, y) merge(x, y, by = 'X', all = T), ym)

# mouse genes to human genes
library(biomaRt)
convertMouseGeneList <- function(x){
  require("biomaRt")
  # blocking human & mouse in the function will slowing down the program.
  human <- useMart("ensembl", dataset = "hsapiens_gene_ensembl")
  mouse <- useMart("ensembl", dataset = "mmusculus_gene_ensembl")
  # but still, we put them in this func, to be good-looking
  genes <- as.character(x[,1])
  genesV2 <- getLDS(attributes = c("mgi_symbol"),
                    filters = "mgi_symbol",
                    values = genes , mart = mouse,
                    attributesL = c("hgnc_symbol"),
                    martL = human, uniqueRows=T)
  #humanx <- unique(genesV2[, 2])
  # Print the first 6 genes found to the screen
  #print(head(genes))
  y <- merge(x, genesV2, by.x = 'X', by.y = 'MGI.symbol', all.x = T)
  return(y)
}
ym3 <- convertMouseGeneList(ym2)
ym4 <- ym3[!duplicated(ym3[,8]),]
ym4[,1] <- ym4[,8]
ym4 <- ym4[-1,-8]

y2 <- merge(yh2, ym4, by = 'X', all = T)
colnames(y2) <- c('X', xh, xm)
y2[,'count'] <- apply(y2, 1, function(x2) x2['count'] <- length(x2[!is.na(x2)]) - 1)

write.csv(y2, "genes_overlap.csv", quote = F, row.names = F)
write.table(y2[y2[,11]>2, 1], "genes_omics_3+.txt", quote = F, row.names = F, col.names = F)



## GET gene_all
gene_om <- read.table('genes_omics_3+.txt')
gene_om2 <- read.csv('genes_overlap.csv')
gene_mc <- read.table('../IR_yes_genes.txt')
gene_om2 <- merge(gene_om2,gene_mc, by.x = 'X', by.y = 'V1', all = F)
gene_om2 <- as.data.frame(gene_om2[,1])
gene_om3 <- merge(gene_om, gene_om2, by = 1, all = T)
rm(gene_om,gene_om2)

gene_mc[,'xx'] <- 1
gene_om3[,'xx'] <- 2
genes_a <- merge(gene_mc, gene_om3, by = 'V1', all = T)
genes_a[is.na(genes_a)] <- 0
genes_a[,'tag'] <- genes_a[,'xx.x'] + genes_a[,'xx.y']
genes_a <- genes_a[,c(1,4)]
write.table(genes_a, "../genes_all.txt", quote = F, row.names = F, col.names = F)



## PART 2: tables
setwd('../')
## 2. get gene_table
all_ano <- read.table('autoantigen_to_hpa_v2.txt', sep = '\t', header = T, quote = "")
genes <- read.table("genes_all.txt")
genes[,'initial'] <- substr(genes[,1],1,1)
anos <- merge(genes, all_ano, by.x = 'V1', by.y = 'id', all.x = T, all.y = F)
colnames(anos) <- c('id', 'tag', 'initial', 'info_table')
# anos2 <- anos[!is.na(anos[,4]) | anos[,2] != 2,]
write.csv(anos, 'gene_table1.csv', row.names = F)


## 3. jisuan danchun zuxueshuju jiyin de shumu
all <- read.csv('../results/gene_table1.csv') #jingguo dui queshaode gene shoudong chuchong dedao
# gene_om <- read.table('./datasets/genes_omics_3+.txt')
# a <- merge(all, gene_om, by.x = 'id', by.y = 'V1', all = F)
gene_om_a <- all[all[,2]>1,][,1]
write(as.character(all[,1]), 'genes_all2.txt')
write(as.character(gene_om_a), 'gene_omics.txt')


## 4. gene_dis_pmid_sent.csv
tb1 <- read.csv('gene_dis_pmid_sent1.csv', stringsAsFactors = F)
tb2 <- read.csv('../results/gene_table.csv', stringsAsFactors = F)[,c(1,2)]
# s <- read.table('20190708 datasets/genes_a.txt')
# tb4 <- merge(s, tb2, by.x = 'V1', by.y = 'id', all.y = T)
# colnames(tb4) <- c('id', 'tag', 'initial', 'info_table')
# tb3 <- merge(tb4[,-3], tb1, by.y = 'gene', by.x = 'id', all = T)
tb3 <- merge(tb2, tb1, by.y = 'gene', by.x = 'id', all = T)
tb3 <- tb3[,c(1,2,4,3,7,5,6)]
tb3[is.na(tb3[,3]), 3] <- ' '
tb3[is.na(tb3[,4]), 4] <- ' '
tb3[is.na(tb3[,5]), 5] <- ' '
tb3[is.na(tb3)]<- '\\N'
write.csv(tb3, '../results/gene_dis_pmid_sent.csv', row.names = F)



