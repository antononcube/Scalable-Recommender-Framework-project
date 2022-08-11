#!/usr/local/bin/lr

##===========================================================
## Launching of Sparse Matrix Recommenders (SMRs) R script
##
## BSD 3-Clause License
##
## Copyright (c) 2022, Anton Antonov
## (See the complete license below)
##===========================================================

# load docopt package from CRAN
suppressMessages(library(docopt))       # we need docopt (>= 0.3) as on CRAN

## configuration for docopt
doc <-
  'Usage:
    invoke-smr.R -h|--help
    invoke-smr.R -v|--version
    invoke-smr.R [-f|--file=FILE] [--profile=PROF] [--must=MUST] [--mustnot=MUSTNOT] [--nrecs=NRECS] [--smr=SMRID] [--type=TYPE]
    invoke-smr.R --pipe
    invoke-smr.R <text>... [--profile=PROF] [--must=MUST] [--mustnot=MUSTNOT] [--nrecs=NRECS] [--smr=SMRID] [--type=TYPE]

  Options:
    -v --version              Show version
    -h --help                 Show this help text
    -e --error                Throw error and halt instead of a warning [default: FALSE]
    -d --dir DIR              Directory (folder) with SMR objects [default: NULL].
    -p --profile=PROF         Profile tags [default : ""]
    --must=MUST               Must profile tags [default : ""]
    --mustnot=MUSTNOT         Must not profile tags [default : ""]
    -s --smr=SMRID            SMR identifier [default: NULL]
    -t --type=TYPE            Type of the output, one of "CSV", "DF", "JSON". [default: DF]
    -n --nrecs=NRECS          Number of recommendations. [default: 12]
    -f --file=FILE            File with text [default: NULL]
    --pipe                    Pipeline input'

## docopt parsing
opt <- docopt(doc)

#print(docopt(doc))

## ----pipeline--------------------------------------------------------------------
# File Read ##

OpenRead <- function(arg) {
  if (arg %in% c("-", "/dev/stdin")) {
    file("stdin", open = "r")
  } else if (grepl("^/dev/fd/", arg)) {
    fifo(arg, open = "r")
  } else {
    file(arg, open = "r")
  }
}

if ( opt$pipe ) {

  con <- OpenRead("-")
  pipeArgs <- read.table(con, sep = " ", header = FALSE)
  opt <- docopt(doc, args = as.character(pipeArgs))
}

## ----pre-process--------------------------------------------------------------------

if (opt$dir == "NA" ||
  opt$dir == "NULL" ||
  is.null(opt$dir)) {
  opt$dir <- "./"
}

if (opt$smr == "NA" ||
  opt$smr == "NULL" ||
  is.null(opt$smr)) {
  opt$smr <- "ZefEcosystem"
}

opt$nrecs <- as.numeric(opt$nrecs)
if (is.na(opt$nrecs) ||
  opt$nrecs == "NA" ||
  opt$nrecs == "NULL" ||
  is.null(opt$nrecs)) {
  opt$nrecs <- 12
}

if (is.na(opt$type) ||
  opt$type == "NA" ||
  opt$type == "NULL" ||
  is.null(opt$type)) {
  opt$type <- "DF"
}

if (opt$error) {

}

params <- list(dir = opt$dir,
               smrID = opt$smr,
               nrecs = opt$nrecs,
               profile = opt$profile,
               must = opt$must,
               mustNot = opt$mustnot,
               type = opt$type)

## ----setup--------------------------------------------------------------------
suppressWarnings(suppressPackageStartupMessages(library(SparseMatrixRecommender)))
suppressWarnings(suppressPackageStartupMessages(library(SMRMon)))
suppressWarnings(suppressPackageStartupMessages(library(magrittr)))

## ----load--------------------------------------------------------------------

fileName <- file.path(params$dir, paste0("smrObj-", params$smrID, ".RData"))

if (!file.exists(fileName)) {
  stop(paste("The file name:", fileName), ", does not exist.", call. = TRUE)
}

load(file = fileName)

## ----recommendations--------------------------------------------------------------------

if ( is.character(params$must) && nchar(params$must) > 0 || is.character(params$mustNot) && nchar(params$mustNot) > 0) {

  shouldLocal = if ( is.character(params$profile) && nchar(params$profile) ) { trimws(strsplit(x = params$profile, split = ";")[[1]]) } else { NULL }
  mustLocal = if ( is.character(params$must) && nchar(params$must) ) { trimws(strsplit(x = params$must, split = ";")[[1]]) } else { NULL }
  mustNotLocal = if ( is.character(params$mustNot) && nchar(params$mustNot) ) { trimws(strsplit(x = params$mustNot, split = ";")[[1]]) } else { NULL }

  shouldLocal = intersect(shouldLocal, colnames(smrObj$M))
  mustLocal = intersect(mustLocal, colnames(smrObj$M))
  mustNotLocal = intersect(mustNotLocal, colnames(smrObj$M))

  if ( length(shouldLocal) == 0 ) { shouldLocal = NULL }
  if ( length(mustLocal) == 0 ) { mustLocal = NULL }
  if ( length(mustNotLocal) == 0 ) { mustNotLocal = NULL }

  recs <-
    smrObj %>%
    SMRMonRetrieveByQueryElements(should = shouldLocal,
                                  must = mustLocal,
                                  mustNot = mustNotLocal,
                                  mustType = 'intersection',
                                  mustNotType = 'union' ) %>%
    SMRMonTakeValue

  if(nrow(recs) > 0) { rownames(recs) <- NULL }

} else if ( is.character(params$profile) && nchar(params$profile) > 0) {

  profileLocal = trimws(strsplit(x = params$profile, split = ";")[[1]])

  recs <-
    smrObj %>%
    SMRMonRecommendByProfile(profileLocal, nrecs = params$nrecs, ignoreUnknownTags = T, normalize = T) %>%
    SMRMonTakeValue

  if(nrow(recs) > 0) {
    rownames(recs) <- NULL
    recs <- recs[, -2]
  }

} else {
  print("Do not know what to do without profile or text arguments.")
  recs = NULL
}

## ----result--------------------------------------------------------------------

if (tolower(params$type) == "df") {
  print(recs)
} else if (tolower(params$type) == "csv") {
  write.csv(x = recs, file = "invoke-smr.csv")
} else {
  print(recs)
}

##===========================================================
## Launching of Time Series Search Engine (TSSE) R script
##
## BSD 3-Clause License
##
## Copyright (c) 2022, Anton Antonov
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
## * Redistributions of source code must retain the above copyright notice, this
## list of conditions and the following disclaimer.
##
## * Redistributions in binary form must reproduce the above copyright notice,
## this list of conditions and the following disclaimer in the documentation
## and/or other materials provided with the distribution.
##
## * Neither the name of the copyright holder nor the names of its
## contributors may be used to endorse or promote products derived from
## this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
## FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
## SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
## CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
## OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
## Written by Anton Antonov,
## ʇǝu˙oǝʇsod@ǝqnɔuouoʇuɐ,
## Windermere, Florida, USA.
##===========================================================