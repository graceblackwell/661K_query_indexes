#!/usr/bin/env bash
#Usage:  query_COBS_image.sh <query.fasta> <threshold>
query=$1
threshold=$2

image="docker://leandroishilima/661k_query_indexes:0.0.1"
#update relevant paths
cobs_index="661k.cobs_compact"
cobs_to_table="cobs_to_table.py"

#query COBS index
singularity exec -B /lustre $image cobs query -i $cobs_index -f ${query} -t ${threshold} > ${query}_${threshold}_results.txt

#run samtools faidx to get length of each query sequence
singularity exec -B /lustre $image samtools faidx $query

#calculate percentage of kmers present rather than number of kmers present
$cobs_to_table --cobs_outfile ${query}_${threshold}_results.txt --fai_file ${query}.fai --outname ${query}_${threshold}_results_table.txt 

