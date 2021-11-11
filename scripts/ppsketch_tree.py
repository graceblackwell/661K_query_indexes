#!/usr/bin/env python3

###Code written by John Lees and adapted for purpose here###

import sys
import os
import subprocess
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
mpl.rcParams.update({'font.size': 18})
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import itertools
import pandas as pd
import dendropy
import pickle
import pp_sketchlib

def buildRapidNJ(rapidnj, refList, coreMat, outPrefix, tree_filename):
    """Use rapidNJ for more rapid tree building
    Creates a phylip of core distances, system call to rapidnj executable, loads tree as
    dendropy object (cleaning quotes in node names), removes temporary files.
    Args:
        rapidnj (str)
            Location of rapidnj executable
        refList (list)
            Names of sequences in coreMat (same order)
        coreMat (numpy.array)
            NxN core distance matrix produced in :func:`~outputsForMicroreact`
        outPrefix (int)
            Output prefix for temporary files
        outPrefix (str)
            Prefix for all generated output files, which will be placed in `outPrefix` subdirectory
        tree_filename (str)
            Filename for output tree (saved to disk)
    Returns:
        tree (dendropy.Tree)
            NJ tree from core distances
    """
    # generate phylip matrix
    print("generating phylip matrix")
    phylip_name = outPrefix + "/" + os.path.basename(outPrefix) + "_core_distances.phylip"
    print(phylip_name)
    with open(phylip_name, 'w') as pFile:
        pFile.write(str(len(refList))+"\n")
        for coreDist, ref in zip(coreMat, refList):
            pFile.write(ref)
            pFile.write(' '+' '.join(map(str, coreDist)))
            pFile.write("\n")

    # construct tree
    rapidnj_cmd = rapidnj + " " + phylip_name + " -n -i pd -o t -x " + tree_filename + ".raw"
    print(rapidnj_cmd)
    try:
        # run command
        subprocess.run(rapidnj_cmd, shell=True, check=True)

        # remove quotation marks for microreact
        with open(tree_filename + ".raw", 'r') as f, open(tree_filename, 'w') as fo:
            for line in f:
                fo.write(line.replace("'", ''))
        # tidy unnecessary files
        os.remove(tree_filename+".raw")
        os.remove(phylip_name)

    # record errors
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Could not run command " + rapidnj_cmd + "; returned code: " + str(e.returncode) + "\n")
        sys.exit(1)

    # read tree and return
    tree = dendropy.Tree.get(path=tree_filename, schema="newick")
    return tree

def generate_phylogeny(coreMat, seqLabels, outPrefix, tree_suffix, rapidnj, overwrite):
    """Generate phylogeny using dendropy or RapidNJ
    Writes a neighbour joining tree (.nwk) from core distances.
    Args:
        coreMat (numpy.array)
            n x n array of core distances for n samples.
        seqLabels (list)
            Processed names of sequences being analysed.
        outPrefix (str)
            Prefix for all generated output files, which will be placed in `outPrefix` subdirectory
        tree_suffix (str)
            String to append to tree file name
        rapidnj (str)
            A string with the location of the rapidnj executable for tree-building. If None, will
            use dendropy by default
        overwrite (bool)
            Overwrite existing output if present (default = False)
    """
    # Save distances to file
    core_dist_file = outPrefix + "/" + os.path.basename(outPrefix) + "_core_dists.csv"
    np.savetxt(core_dist_file, coreMat, delimiter=",", header = ",".join(seqLabels), comments="")

    # calculate phylogeny
    tree_filename = outPrefix + "/" + os.path.basename(outPrefix) + tree_suffix
    if overwrite or not os.path.isfile(tree_filename):
        sys.stderr.write("Building phylogeny\n")
        if rapidnj is not None:
            tree = buildRapidNJ(rapidnj, seqLabels, coreMat, outPrefix, tree_filename)
        else:
            pdm = dendropy.PhylogeneticDistanceMatrix.from_csv(src=open(core_dist_file),
                                                               delimiter=",",
                                                               is_first_row_column_names=True,
                                                               is_first_column_row_names=False)
            tree = pdm.nj_tree()

        # Not sure why, but seems that this needs to be run twice to get
        # what I would think of as a midpoint rooted tree
        tree.reroot_at_midpoint(update_bipartitions=True, suppress_unifurcations=False)
        tree.reroot_at_midpoint(update_bipartitions=True, suppress_unifurcations=False)
        tree.write(path=tree_filename,
                   schema="newick",
                   suppress_rooting=True,
                   unquoted_underscores=True)
    else:
        sys.stderr.write("NJ phylogeny already exists; add --overwrite to replace\n")

    # remove file as it can be large
    os.remove(core_dist_file)



def readPickle(pklName):
    """Loads core and accessory distances saved by :func:`~storePickle`
    Called during ``--fit-model``
    Args:
        pklName (str)
            Prefix for saved files
    Returns:
        rlist (list)
            List of reference sequence names (for :func:`~iterDistRows`)
        qlist (list)
            List of query sequence names (for :func:`~iterDistRows`)
        self (bool)
            Whether an all-vs-all self DB (for :func:`~iterDistRows`)
        X (numpy.array)
            n x 2 array of core and accessory distances
    """
    with open(pklName + ".pkl", 'rb') as pickle_file:
        rlist, qlist, self = pickle.load(pickle_file)
    X = np.load(pklName + ".npy")
    return rlist, qlist, self, X

def update_distance_matrices(refList, distMat, queryList = None, query_ref_distMat = None,
                             query_query_distMat = None, threads = 1):
    """Convert distances from long form (1 matrix with n_comparisons rows and 2 columns)
    to a square form (2 NxN matrices), with merging of query distances if necessary.
    Args:
        refList (list)
            List of references
        distMat (numpy.array)
            Two column long form list of core and accessory distances
            for pairwise comparisons between reference db sequences
        queryList (list)
            List of queries
        query_ref_distMat (numpy.array)
            Two column long form list of core and accessory distances
            for pairwise comparisons between queries and reference db
            sequences
        query_query_distMat (numpy.array)
            Two column long form list of core and accessory distances
            for pairwise comparisons between query sequences
        threads (int)
            Number of threads to use
    Returns:
        seqLabels (list)
            Combined list of reference and query sequences
        coreMat (numpy.array)
            NxN array of core distances for N sequences
        accMat (numpy.array)
            NxN array of accessory distances for N sequences
    """
    seqLabels = refList
    if queryList is not None:
        seqLabels = seqLabels + queryList

    if queryList == None:
        coreMat = pp_sketchlib.longToSquare(distMat[:, [0]], threads)
        accMat = pp_sketchlib.longToSquare(distMat[:, [1]], threads)
    else:
        coreMat = pp_sketchlib.longToSquareMulti(distMat[:, [0]],
                                                 query_ref_distMat[:, [0]],
                                                 query_query_distMat[:, [0]],
                                                 threads)
        accMat = pp_sketchlib.longToSquareMulti(distMat[:, [1]],
                                                 query_ref_distMat[:, [1]],
                                                 query_query_distMat[:, [1]],
                                                 threads)

    # return outputs
    return seqLabels, coreMat, accMat


results =  readPickle("ppsketch")
updated_mat = update_distance_matrices(results[1], results[3])
generate_phylogeny(updated_mat[1], updated_mat[0], "out", "tree", "rapidnj", "True")

