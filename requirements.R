install.packages(c("arrow", "randomForest", "jsonlite", "BiocManager"))

BiocManager::install("sesame")
BiocManager::install("preprocessCore", configure.args = c(preprocessCore = "--disable-threading"), force= TRUE, update=TRUE, type = "source")

library(sesame)
sesameDataCache()
