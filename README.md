# 661K_query_indexes

661K_query_indexes contains a number of bash, python and R notebooks to utilise the databases associated with the 661K manucript https://doi.org/10.1371/journal.pbio.3001421

## Requirements
* Singularity or Docker to use `Docker://leandroishilima/661k_query_indexes:0.0.1` _(cluster)_

* Have downloaded the contents of the [ftp](http://ftp.ebi.ac.uk/pub/databases/ENA2018-bacteria-661k/) _(cluster)_
  * On sanger clusters: `/lustre/scratch118/infgen/pathogen/pathpipe/ENA2018-bacteria-661k`

* Download the [figshare](https://doi.org/10.6084/m9.figshare.16437939.v1) repository which includes metadata and characterisation data for the genomes _(local)_

* R _(local)_

## Usage

Load singularity and start an interactive job (e.g. specific for Sanger cluster)
```bash
module load ISG/singularity/3.6.4
bsub -Is -R"select[mem>80000] rusage[mem=80000]" -M80000 bash
```

### Query COBS index - DNA search via a kmer based approach
Note: update path for `cobs_to_table` in `query_COBS_image.sh` 
```bash
query_COBS_image.sh <query.fasta> <threshold> #query.fasta can be a multifasta
```
The `_results_table.txt` file provides the results of the search. 

### Sketch and query a genome agains the sourmash index
```bash
sourmash_search.sh <input.fasta> <prefix_for_outfiles> #input can be fastq files as well
```
The `<prefix_for_outfiles>_genome_similarity.txt` file provides the results of the similarity search and `<prefix_for_outfiles>_related_sample_ids.txt` is just the sample_ids and can be used as the subset input for pp_sketch. 

### Extract core and accessory distances of a subset of genomes using the pp_sketch index
This script extracts the distances and generates a NJ tree based on the core distances. The script for producing the tree (`ppsketch_tree.py`) is adapted from John Lees. 
Note: update path for `generate_tree` in `extract_distances.sh` 
Current issue using the pp_sketch index hosted by pathogen informatics. Had no trouble using an rsync'd version in the same directory. 

```bash
extract_distances.sh <list_of_sample_ids_to_subset> 
```
The distance tree is `out/outtree`. 

### R notebooks for general plotting
These have been designed for use on local computer and just require updated paths to 
* Plotting_cobs_hits.Rmd
* Plotting_against_tree.Rmd

## References
1. Bingmann T, Bradley P, Gauger F, Iqbal Z. COBS: a Compact Bit-Sliced Signature Index. arXiv:190509624. 2019. Available: http://arxiv.org/abs/1905.09624

2. Pierce NT, Irber L, Reiter T, Brooks P, Brown CT. Large-scale sequence comparisons with sourmash. F1000Res. 2019;8: 1006. doi:10.12688/f1000research.19675.1

3. Lees JA, Harris SR, Tonkin-Hill G, Gladstone RA, Lo SW, Weiser JN, et al. Fast and flexible bacterial genomic epidemiology with PopPUNK. Genome Res. 2019;29: 304–316. doi:10.1101/gr.241455.118

