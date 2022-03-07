#!/usr/bin/env bash
#Usage:  extract_distance.sh <list_of_sample_ids_to_subset> 
queries=$1

image="docker://leandroishilima/661k_query_indexes:0.0.1"
#update to relevant paths 
#Note: for some reason when the ppsketch index is not in the directory where the job is launched it throws an error
ppsketch_index="661_ppsketch_v1.5"
generate_tree="ppsketch_tree.py"

#extract core and accessory distance of subset of samples. If you just want the txt file with the core and accessory distances add "--print" to the command
singularity exec -B /lustre ${image} poppunk_sketch --query --ref-db ${ppsketch_index} --query-db ${ppsketch_index} --subset $queries --cpus 4

#making out directory for tree
mkdir out

#calculate NJ tree from core distances
singularity exec -B /lustre ${image} $generate_tree

