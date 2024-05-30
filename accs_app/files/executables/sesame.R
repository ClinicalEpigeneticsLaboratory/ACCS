args = commandArgs(trailingOnly=TRUE)

if (length(args)==0) {
  stop("At least one argument must be supplied")
} else {
  data_path = args[1]  
}
library(randomForest)
library(jsonlite)
library(sesame)
library(arrow)

message("Running: ", data_path)
message("Loading idats from: ", file.path(data_path, "idats/"))

sdfs <- openSesame(file.path(data_path, "idats/"), func=NULL, prep="QCDPB")

# Infer sex and platform
sex <- inferSex(openSesame(sdfs))
platform <- sesameData_check_platform(probes = sdfs$Probe_ID)
options <- list("MALE" = "Male", "FEMALE" = "Female")

write(toJSON(list("PredictedSex" = options[[sex]], "Platform" = platform)), file.path(data_path, "predicted.json"))

# Cast type
name <- names(searchIDATprefixes(file.path(data_path, "idats/")))

temp_list <- list()
temp_list[[name]] <- sdfs %>% as.data.frame
sdfs <- temp_list

message("Converting to betas")
betas = do.call(cbind, BiocParallel::bplapply(sdfs, getBetas))
betas = betasCollapseToPfx(betas)
betas = betas %>% as.data.frame

betas$CpG <- rownames(betas)

message("Extracting total intensities")
intensities = do.call(cbind, BiocParallel::bplapply(sdfs, totalIntensities))
intensities = betasCollapseToPfx(intensities)
intensities = intensities %>% as.data.frame

intensities$CpG <- rownames(intensities)

message("Saving files")
message("N CpGs --> ", length(intensities$CpG))
message("N samples --> ", length(colnames(intensities)) - 1)

betas <- betas[grep("cg", rownames(betas)),]
write_parquet(betas, file.path(data_path, "mynorm.parquet"))

intensities <- intensities[grep("cg", rownames(intensities)),]
write_parquet(intensities, file.path(data_path, "intensity.parquet"))
message("DONE")
