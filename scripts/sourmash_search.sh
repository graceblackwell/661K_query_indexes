#!/usr/bin/env bash
#Usage:  sourmash_search.sh <input.fasta> <prefix_for_outfiles>

input=$1
prefix=$2

image="docker://leandroishilima/661k_query_indexes:0.0.1"
minhash_index="/lustre/scratch118/infgen/pathogen/pathpipe/ENA2018-bacteria-661k/661K_sourmash_index_scaled.sbt.zip"

#sketch query fasta
singularity exec -B /lustre $image sourmash compute -k 31 -n 5000 ${input} -o ${prefix}.sig

#search for relatives of the query sketch
singularity exec -B /lustre $image sourmash search ${prefix}.sig $minhash_index -o ${prefix}_hits

#extracting sample_ids from output
awk -F"," '(NR>1){print $2}' ${prefix}_hits | awk -F"/" '{print $4}' | awk -F"." 'BEGIN{print "sample_id"};{print $1}' > ${prefix}_related_sample_ids.txt

#extracting just the similarity column from output
awk -F"," '{print $1}' ${prefix}_hits > tmp.similarity

#creating clean output with just two columns; sample_id and similarity
paste ${prefix}_related_sample_ids.txt tmp.similarity > ${prefix}_genome_similarity.txt

#cleaning up
rm tmp.similarity
rm ${prefix}_hits
