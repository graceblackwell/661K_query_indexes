# 661K_query_indexes

661K_query_indexes contains a number of bash, python and R notebooks to utilise the databases associated with the 661K manucript https://doi.org/10.1371/journal.pbio.3001421

## Requirements
-Singularity or Docker to use Docker://leandroishilima/661k_query_indexes:0.0.1

-Have downloaded the contents of the [ftp](http://ftp.ebi.ac.uk/pub/databases/ENA2018-bacteria-661k/)

-R

## Usage

On Sanger clusters load singularity and start an interactive job.
```bash
module load ISG/singularity/3.6.4
bsub -Is -R"select[mem>80000] rusage[mem=80000]" -M80000 bash
```

### Query COBS index - DNA search via a kmer based approach
 
```bash
query_COBS_image.sh <query.fasta> <threshold> #query.fasta can be a multifasta
```
The `_results_table.txt` file provides the results of the search. 

### Sketch and query a genome agains the sourmash index

```bash
sourmash_search.sh <input.fasta> <prefix_for_outfiles> #input can be fastq files as well
```
The `_genome_similarity.txt` file provides the results of the similarity search and `_related_sample_ids.txt` is just the sample_ids and can be used as the subset input for pp_sketch. 

### Extract core and accessory distances of a subset of genomes in the pp_sketch index
```bash
sourmash_search.sh <input.fasta> <prefix_for_outfiles> #input can be fastq files as well
```
The `_genome_similarity.txt` file provides the results of the similarity search and `_related_sample_ids.txt` is just the sample_ids and can be used as the subset input for pp_sketch. 



