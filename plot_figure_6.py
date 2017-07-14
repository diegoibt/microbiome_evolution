# Within-snp gene changes

import matplotlib  
matplotlib.use('Agg') 
import config
import parse_midas_data
###
#
# For today while the new data processes
#
import os
#parse_midas_data.data_directory = os.path.expanduser("~/ben_nandita_hmp_data_062517/")
#########################################
import parse_HMP_data


import pylab
import sys
import numpy

import diversity_utils
import gene_diversity_utils
import sfs_utils
import calculate_substitution_rates
import calculate_temporal_changes

import stats_utils
import matplotlib.colors as colors
import matplotlib.cm as cmx
from math import log10,ceil
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from numpy.random import randint, choice

mpl.rcParams['font.size'] = 5
mpl.rcParams['lines.linewidth'] = 0.5
mpl.rcParams['legend.frameon']  = False
mpl.rcParams['legend.fontsize']  = 'small'

species_name = "Bacteroides_vulgatus_57955"

################################################################################
#
# Standard header to read in argument information
#
################################################################################
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="Loads only a subset of SNPs for speed", action="store_true")
parser.add_argument("--chunk-size", type=int, help="max number of records to load", default=1000000000)
parser.add_argument('--other-species', type=str, help='Run the script for a different species')

args = parser.parse_args()

debug = args.debug
chunk_size = args.chunk_size
other_species = args.other_species

if other_species:
    species_name = other_species
    other_species_str = "_%s" % species_name
else:
    other_species_str = ""
    
################################################################################

min_coverage = config.min_median_coverage
clade_divergence_threshold = 1e-02
modification_divergence_threshold = 1e-03

# Load subject and sample metadata
sys.stderr.write("Loading sample metadata...\n")
subject_sample_map = parse_HMP_data.parse_subject_sample_map()
sample_country_map = parse_HMP_data.parse_sample_country_map()
sample_order_map = parse_HMP_data.parse_sample_order_map()
sys.stderr.write("Done!\n")
       
# Only plot samples above a certain depth threshold that are "haploids"
snp_samples = diversity_utils.calculate_haploid_samples(species_name, debug=debug)

####################################################
#
# Set up Figure (4 panels, arranged in 2x2 grid)
#
####################################################

pylab.figure(1,figsize=(5,2))
fig = pylab.gcf()


# make three panels panels
outer_grid  = gridspec.GridSpec(1,2, width_ratios=[2,1], wspace=0.25)

differences_grid = gridspec.GridSpecFromSubplotSpec(2, 2, height_ratios=[1,1],
                subplot_spec=outer_grid[0], hspace=0.05, width_ratios=[1,1], wspace=0.025)
                
gene_grid = gridspec.GridSpecFromSubplotSpec(2, 1, height_ratios=[1,1],
                subplot_spec=outer_grid[1], hspace=0.45)


## Supp figure
pylab.figure(2,figsize=(3,2))
supplemental_fig = pylab.gcf()

supplemental_outer_grid  = gridspec.GridSpec(1,1)

###################
#
# SNP change panel
#
###################

snp_axis = plt.Subplot(fig, differences_grid[0,0])
fig.add_subplot(snp_axis)

#snp_axis.set_title("%s %s (%s)" % tuple(species_name.split("_")),fontsize=7)

snp_axis.set_ylabel('SNP changes')
snp_axis.set_ylim([2e-01,1e05])

snp_axis.semilogy([1e-09,1e-09],[1e08,1e08],'b-',label='Within host')
snp_axis.semilogy([1e-09,1e-09],[1e08,1e08],'r-',label='Between host')

snp_axis.spines['top'].set_visible(False)
snp_axis.spines['right'].set_visible(False)
snp_axis.get_xaxis().tick_bottom()
snp_axis.get_yaxis().tick_left()


within_snp_axis = plt.Subplot(fig, differences_grid[0,1])
fig.add_subplot(within_snp_axis)

#snp_axis.set_title("%s %s (%s)" % tuple(species_name.split("_")),fontsize=7)

within_snp_axis.set_ylim([2e-01,1e05])

within_snp_axis.spines['top'].set_visible(False)
within_snp_axis.spines['right'].set_visible(False)
within_snp_axis.spines['left'].set_visible(False)

within_snp_axis.get_xaxis().tick_bottom()
within_snp_axis.get_yaxis().tick_left()



###################
#
# Gene change panel
#
###################

gene_axis = plt.Subplot(fig, differences_grid[1,0])
fig.add_subplot(gene_axis)

gene_axis.set_ylabel('Gene changes')
gene_axis.set_ylim([2e-01,1e04])

gene_axis.set_xlabel('Between-host')

gene_axis.spines['top'].set_visible(False)
gene_axis.spines['right'].set_visible(False)
gene_axis.get_xaxis().tick_bottom()
gene_axis.get_yaxis().tick_left()


within_gene_axis = plt.Subplot(fig, differences_grid[1,1])
fig.add_subplot(within_gene_axis)

within_gene_axis.set_ylim([2e-01,1e04])

within_gene_axis.spines['top'].set_visible(False)
within_gene_axis.spines['right'].set_visible(False)
within_gene_axis.spines['left'].set_visible(False)
within_gene_axis.get_xaxis().tick_bottom()
within_gene_axis.get_yaxis().tick_left()

within_gene_axis.set_xlabel('Within-host')

##############################################################################
#
# Gene change prevalence panel
#
##############################################################################

prevalence_axis = plt.Subplot(fig, gene_grid[0])
fig.add_subplot(prevalence_axis)

prevalence_axis.set_ylabel('Fraction gene changes ')
prevalence_axis.set_xlabel('Gene prevalence, $p$')
prevalence_axis.set_xlim([0,1])
#prevalence_axis.set_ylim([0,1.1])

prevalence_axis.spines['top'].set_visible(False)
prevalence_axis.spines['right'].set_visible(False)
prevalence_axis.get_xaxis().tick_bottom()
prevalence_axis.get_yaxis().tick_left()


##############################################################################
#
# Gene change multiplicity panel
#
##############################################################################

#multiplicity_axis = plt.Subplot(fig, gene_grid[1])
#fig.add_subplot(multiplicity_axis)
multiplicity_axis = plt.Subplot(supplemental_fig, supplemental_outer_grid[0])
supplemental_fig.add_subplot(multiplicity_axis)


multiplicity_axis.set_ylabel('Fraction gene changes')
multiplicity_axis.set_xlabel('Gene multiplicity, $m$')
multiplicity_axis.set_xlim([0.5,3.5])
multiplicity_axis.set_ylim([0,1.05])

multiplicity_axis.set_xticks([1,2,3])

multiplicity_axis.spines['top'].set_visible(False)
multiplicity_axis.spines['right'].set_visible(False)
multiplicity_axis.get_xaxis().tick_bottom()
multiplicity_axis.get_yaxis().tick_left()

##############################################################################
#
# Gene change parallelism panel
#
##############################################################################

parallelism_axis = plt.Subplot(fig, gene_grid[1])
fig.add_subplot(parallelism_axis)
#parallelism_axis = plt.Subplot(supplemental_fig, supplemental_outer_grid[0])
#supplemental_fig.add_subplot(parallelism_axis)


parallelism_axis.set_ylabel('Fraction genes >= c')
parallelism_axis.set_xlabel('Copynum foldchange, $c$')
#parallelism_axis.set_xlim([0,5])
parallelism_axis.set_ylim([0,1.05])

parallelism_axis.spines['top'].set_visible(False)
parallelism_axis.spines['right'].set_visible(False)
parallelism_axis.get_xaxis().tick_bottom()
parallelism_axis.get_yaxis().tick_left()

reference_genes = parse_midas_data.load_reference_genes(species_name)

# Analyze SNPs, looping over chunk sizes. 
# Clunky, but necessary to limit memory usage on cluster

import sfs_utils
sys.stderr.write("Loading SFSs for %s...\t" % species_name)
samples, sfs_map = parse_midas_data.parse_within_sample_sfs(species_name, allowed_variant_types=set(['1D','2D','3D','4D'])) 
sys.stderr.write("Done!\n")


sys.stderr.write("Loading pre-computed substitution rates for %s...\n" % species_name)
substitution_rate_map = calculate_substitution_rates.load_substitution_rate_map(species_name)
sys.stderr.write("Calculating matrix...\n")
dummy_samples, snp_difference_matrix, snp_opportunity_matrix = calculate_substitution_rates.calculate_matrices_from_substitution_rate_map(substitution_rate_map, 'all', allowed_samples=snp_samples)
snp_samples = dummy_samples
sys.stderr.write("Done!\n")

sys.stderr.write("Loading pre-computed temporal changes for %s...\n" % species_name)
temporal_change_map = calculate_temporal_changes.load_temporal_change_map(species_name)
sys.stderr.write("Done!\n")

snp_substitution_rate = snp_difference_matrix*1.0/(snp_opportunity_matrix+(snp_opportunity_matrix==0))
sys.stderr.write("Done!\n")   

# Load gene coverage information for species_name
sys.stderr.write("Loading pangenome data for %s...\n" % species_name)
gene_samples, gene_names, gene_presence_matrix, gene_depth_matrix, marker_coverages, gene_reads_matrix = parse_midas_data.parse_pangenome_data(species_name,allowed_samples=snp_samples)
sys.stderr.write("Done!\n")

sys.stderr.write("Loaded gene info for %d samples\n" % len(gene_samples))

gene_copynum_matrix = gene_depth_matrix*1.0/(marker_coverages+(marker_coverages==0))

clipped_gene_copynum_matrix = numpy.clip(gene_depth_matrix,0.1,1e09)/(marker_coverages+0.1*(marker_coverages==0))

low_copynum_matrix = (gene_copynum_matrix<=3)
good_copynum_matrix = (gene_copynum_matrix>=0.5)*(gene_copynum_matrix<=3)

prevalence_idxs = (parse_midas_data.calculate_unique_samples(subject_sample_map, gene_samples))*(marker_coverages>=min_coverage)
    
prevalences = gene_diversity_utils.calculate_fractional_gene_prevalences(gene_depth_matrix[:,prevalence_idxs], marker_coverages[prevalence_idxs])

pangenome_prevalences = numpy.array(prevalences,copy=True)
pangenome_prevalences.sort()
        
# Calculate matrix of number of genes that differ
sys.stderr.write("Calculating matrix of gene differences...\n")
gene_gain_matrix, gene_loss_matrix, gene_opportunity_matrix = gene_diversity_utils.calculate_coverage_based_gene_hamming_matrix_gain_loss(gene_reads_matrix, gene_depth_matrix, marker_coverages)

gene_difference_matrix = gene_gain_matrix + gene_loss_matrix

# Now need to make the gene samples and snp samples match up
desired_samples = gene_samples

num_haploids = len(desired_samples)
     
# Calculate which pairs of idxs belong to the same sample, which to the same subject
# and which to different subjects
desired_same_sample_idxs, desired_same_subject_idxs, desired_diff_subject_idxs = parse_midas_data.calculate_ordered_subject_pairs(sample_order_map, desired_samples)

sys.stderr.write("%d temporal samples\n" % len(desired_same_subject_idxs[0]))

snp_sample_idx_map = parse_midas_data.calculate_sample_idx_map(desired_samples, snp_samples)
gene_sample_idx_map = parse_midas_data.calculate_sample_idx_map(desired_samples, gene_samples)
  
same_subject_snp_idxs = parse_midas_data.apply_sample_index_map_to_indices(snp_sample_idx_map, desired_same_subject_idxs)  
same_subject_gene_idxs = parse_midas_data.apply_sample_index_map_to_indices(gene_sample_idx_map, desired_same_subject_idxs)  

diff_subject_snp_idxs = parse_midas_data.apply_sample_index_map_to_indices(snp_sample_idx_map, desired_diff_subject_idxs)  
diff_subject_gene_idxs = parse_midas_data.apply_sample_index_map_to_indices(gene_sample_idx_map, desired_diff_subject_idxs)  

# Calculate median between-host differences
#modification_divergence_threshold = numpy.median(snp_substitution_rate[diff_subject_snp_idxs])/4.0

# Calculate subset of "modification timepoints" 
modification_pair_idxs = set([])

for sample_pair_idx in xrange(0,len(same_subject_snp_idxs[0])):
#    
    snp_i = same_subject_snp_idxs[0][sample_pair_idx]
    snp_j = same_subject_snp_idxs[1][sample_pair_idx]

    if snp_substitution_rate[snp_i, snp_j] < modification_divergence_threshold:
        modification_pair_idxs.add( sample_pair_idx ) 



between_host_gene_idxs = [] # indexes of genes that changed between hosts
low_divergence_between_host_gene_idxs = [] # indexes of genes that changed between particularly low divergence hosts

diff_subject_snp_changes = []
diff_subject_gene_changes = []

for sample_pair_idx in xrange(0,len(diff_subject_snp_idxs[0])):
    
    snp_i = diff_subject_snp_idxs[0][sample_pair_idx]
    snp_j = diff_subject_snp_idxs[1][sample_pair_idx]

    diff_subject_snp_changes.append( snp_difference_matrix[snp_i, snp_j] )
    
    # Now do genes
    i = diff_subject_gene_idxs[0][sample_pair_idx]
    j = diff_subject_gene_idxs[1][sample_pair_idx]
    
    if (marker_coverages[i]<min_coverage) or (marker_coverages[j]<min_coverage):
        diff_subject_gene_changes.append( -1 )
    else:
        diff_subject_gene_changes.append( gene_difference_matrix[i,j] )
        
        
        if snp_substitution_rate[snp_i, snp_j] < clade_divergence_threshold:
        
            # Now actually calculate genes that differ! 
            gene_idxs = gene_diversity_utils.calculate_gene_differences_between_idxs(i,j, gene_reads_matrix, gene_depth_matrix, marker_coverages)
        
            between_host_gene_idxs.extend(gene_idxs)
        
            if snp_substitution_rate[snp_i, snp_j] < modification_divergence_threshold:
                low_divergence_between_host_gene_idxs.extend(gene_idxs)

diff_subject_snp_changes = numpy.array(diff_subject_snp_changes)
diff_subject_gene_changes = numpy.array(diff_subject_gene_changes)

diff_subject_snp_changes, diff_subject_gene_changes =  (numpy.array(x) for x in zip(*sorted(zip(diff_subject_snp_changes, diff_subject_gene_changes))))


same_subject_snp_changes = []
same_subject_snp_mutations = []
same_subject_snp_reversions = []

same_subject_gene_changes = []
same_subject_gene_gains = []
same_subject_gene_losses = []


within_host_gene_idxs = [] # the indexes of genes that actually changed between samples
within_host_null_gene_idxs = [] # a null distribution of gene indexes. chosen randomly from genes "present" in genome

within_host_next_fold_changes = []
within_host_null_next_fold_changes = []
within_host_between_next_fold_changes = []

total_modification_error_rate = 0
total_modifications = 0

for sample_pair_idx in xrange(0,len(same_subject_snp_idxs[0])):
#    
    snp_i = same_subject_snp_idxs[0][sample_pair_idx]
    snp_j = same_subject_snp_idxs[1][sample_pair_idx]
    
    sample_i = snp_samples[snp_i]
    sample_j = snp_samples[snp_j]
    
    
    perr, mutations, reversions = calculate_temporal_changes.calculate_mutations_reversions_from_temporal_change_map(temporal_change_map, sample_i, sample_j)    
    
    num_mutations = len(mutations)
    num_reversions = len(reversions)
    num_snp_changes = num_mutations+num_reversions
    
    if perr>1:
        num_mutations = 0
        num_reversions = 0
        num_snp_changes = -1
    
    same_subject_snp_changes.append(num_snp_changes)
    same_subject_snp_mutations.append(num_mutations)
    same_subject_snp_reversions.append(num_reversions)
    
    if snp_substitution_rate[snp_i, snp_j] < modification_divergence_threshold:
        if perr<=1:
            total_modification_error_rate += perr
            total_modifications += num_snp_changes
            
    if num_snp_changes>-1:
        print sample_i, sample_j, num_snp_changes, num_mutations, num_reversions, perr
    
    i = same_subject_gene_idxs[0][sample_pair_idx]
    j = same_subject_gene_idxs[1][sample_pair_idx]
    
    if marker_coverages[i]<min_coverage or marker_coverages[j]<min_coverage:
        # can't look at gene changes!

        same_subject_gene_changes.append(-1)
        same_subject_gene_gains.append(-1)
        same_subject_gene_losses.append(-1)
        gene_perr = 1
    else:
       
        gene_perr, gains, losses = calculate_temporal_changes.calculate_gains_losses_from_temporal_change_map(temporal_change_map, sample_i, sample_j)
        
        print sample_i, sample_j, gene_difference_matrix[i,j], gene_gain_matrix[i,j], gene_loss_matrix[i,j], gene_perr
       
        same_subject_gene_changes.append(gene_difference_matrix[i,j])
        same_subject_gene_gains.append(gene_gain_matrix[i,j])
        same_subject_gene_losses.append(gene_loss_matrix[i,j])
        
        if sample_pair_idx in modification_pair_idxs:
        
            # Calculate set of genes that are present in at least one sample
            present_gene_idxs = []
            present_gene_idxs.extend( numpy.nonzero( (gene_copynum_matrix[:,i]>0.5)*(gene_copynum_matrix[:,i]<2))[0] )
            present_gene_idxs.extend( numpy.nonzero( (gene_copynum_matrix[:,j]>0.5)*(gene_copynum_matrix[:,j]<2))[0] )
        
            pair_specific_gene_idxs = gene_diversity_utils.calculate_gene_differences_between_idxs(i, j, gene_reads_matrix, gene_depth_matrix, marker_coverages)

            if len(pair_specific_gene_idxs)==0:
                continue

            pair_specific_null_gene_idxs = choice(present_gene_idxs, len(pair_specific_gene_idxs)*10 )
            pair_specific_between_gene_idxs = choice(between_host_gene_idxs, len(pair_specific_gene_idxs)*10 )
            
            within_host_gene_idxs.extend(pair_specific_gene_idxs)
            within_host_null_gene_idxs.extend(pair_specific_null_gene_idxs)            
            
            other_fold_changes = []
            null_other_fold_changes = []
            between_other_fold_changes = []
            
            for other_sample_pair_idx in xrange(0,len(same_subject_snp_idxs[0])):
           
                other_i = same_subject_gene_idxs[0][other_sample_pair_idx]
                other_j = same_subject_gene_idxs[1][other_sample_pair_idx]
     
                # Make sure we don't count the same thing twice! 
                if other_sample_pair_idx == sample_pair_idx:
                    continue
                
                # Make sure it is not a replacement!    
                if other_sample_pair_idx not in modification_pair_idxs:
                    continue
                    
                if (marker_coverages[other_i]<min_coverage) or (marker_coverages[other_j]<min_coverage):
                    continue     
                
                # calculate log-fold change
                logfoldchanges = numpy.fabs( numpy.log2(clipped_gene_copynum_matrix[pair_specific_gene_idxs,other_j] / clipped_gene_copynum_matrix[pair_specific_gene_idxs,other_i] ) )
                
                good_idxs = numpy.logical_or( good_copynum_matrix[pair_specific_gene_idxs, other_i], good_copynum_matrix[pair_specific_gene_idxs, other_j] ) 
                good_idxs *= numpy.logical_and( low_copynum_matrix[pair_specific_gene_idxs, other_i], low_copynum_matrix[pair_specific_gene_idxs, other_j] ) 
                
                bad_idxs = numpy.logical_not( good_idxs ) 
                logfoldchanges[bad_idxs] = -1
                
                other_fold_changes.append(logfoldchanges)
                
                # calculate log-fold change
                logfoldchanges = numpy.fabs( numpy.log2(clipped_gene_copynum_matrix[pair_specific_null_gene_idxs,other_j] / clipped_gene_copynum_matrix[pair_specific_null_gene_idxs,other_i] ) )
                
                # only include genes that are at low copynum at both timepoints
                # and have a "good" copynum at at least one point
                good_idxs = numpy.logical_or( good_copynum_matrix[pair_specific_null_gene_idxs, other_i], good_copynum_matrix[pair_specific_null_gene_idxs, other_j] ) 
                good_idxs *= numpy.logical_and( low_copynum_matrix[pair_specific_null_gene_idxs, other_i], low_copynum_matrix[pair_specific_null_gene_idxs, other_j] ) 
                bad_idxs = numpy.logical_not( good_idxs ) 
                
                logfoldchanges[bad_idxs] = -1
                
                null_other_fold_changes.append( logfoldchanges )
                
                # calculate log-fold change
                logfoldchanges = numpy.fabs( numpy.log2(clipped_gene_copynum_matrix[pair_specific_between_gene_idxs,other_j] / clipped_gene_copynum_matrix[pair_specific_between_gene_idxs,other_i] ) )
                good_idxs = numpy.logical_or( good_copynum_matrix[pair_specific_between_gene_idxs, other_i], good_copynum_matrix[pair_specific_between_gene_idxs, other_j] ) 
                good_idxs *= numpy.logical_and( low_copynum_matrix[pair_specific_between_gene_idxs, other_i], low_copynum_matrix[pair_specific_between_gene_idxs, other_j] ) 
                 
                bad_idxs = numpy.logical_not( good_idxs ) 
                logfoldchanges[bad_idxs] = -1
                
                between_other_fold_changes.append( logfoldchanges )
                
            other_fold_changes = numpy.array(other_fold_changes)
            null_other_fold_changes = numpy.array(null_other_fold_changes)
            between_other_fold_changes = numpy.array(between_other_fold_changes)
            
            for gene_idx in xrange(0,other_fold_changes.shape[1]):
                fold_changes = other_fold_changes[:,gene_idx]
                fold_changes = fold_changes[fold_changes>-0.5]
                if len(fold_changes)>0:
                    #print "Observed biggest change: %g, median change %g" % (fold_changes.max(), numpy.median(fold_changes))
                    #print fold_changes
                    within_host_next_fold_changes.append( (fold_changes).max() )

            for gene_idx in xrange(0,null_other_fold_changes.shape[1]):
                fold_changes = null_other_fold_changes[:,gene_idx]
                fold_changes = fold_changes[fold_changes>-0.5]
                if len(fold_changes)>0:
                    within_host_null_next_fold_changes.append( (fold_changes).max() )
                
            for gene_idx in xrange(0, between_other_fold_changes.shape[1]):
                fold_changes = between_other_fold_changes[:,gene_idx]
                fold_changes = fold_changes[fold_changes>-0.5]
                if len(fold_changes)>0:
                    within_host_between_next_fold_changes.append( (fold_changes).max() )


within_host_next_fold_changes = numpy.array(within_host_next_fold_changes)
within_host_between_next_fold_changes = numpy.array(within_host_between_next_fold_changes)
within_host_null_next_fold_changes = numpy.array(within_host_null_next_fold_changes)

within_host_next_fold_changes = numpy.power(2, within_host_next_fold_changes)
within_host_between_next_fold_changes = numpy.power(2, within_host_between_next_fold_changes)
within_host_null_next_fold_changes = numpy.power(2, within_host_null_next_fold_changes)

print "%g modifications, %g expected" % (total_modifications, total_modification_error_rate)


# Sort all lists by ascending lower bound on SNP changes, then gene changes
same_subject_snp_changes, same_subject_gene_changes, same_subject_snp_reversions, same_subject_snp_mutations, same_subject_gene_gains, same_subject_gene_losses = (numpy.array(x) for x in zip(*sorted(zip(same_subject_snp_changes, same_subject_gene_changes, same_subject_snp_reversions, same_subject_snp_mutations, same_subject_gene_gains, same_subject_gene_losses))))


# Construct site frequency spectra

within_host_gene_idx_counts = {}
for gene_idx in within_host_gene_idxs:
    if gene_idx not in within_host_gene_idx_counts:
        within_host_gene_idx_counts[gene_idx] = 0
    within_host_gene_idx_counts[gene_idx] += 1

within_host_gene_sfs = list(within_host_gene_idx_counts.values())

within_host_gene_prevalences = []
within_host_gene_multiplicities = []    
for gene_idx in within_host_gene_idxs:    
    within_host_gene_multiplicities.append( within_host_gene_idx_counts[gene_idx] )
    within_host_gene_prevalences.append(prevalences[gene_idx])

        
within_host_null_gene_prevalences = []
for gene_idx in within_host_null_gene_idxs:
    within_host_null_gene_prevalences.append(prevalences[gene_idx])    

within_host_gene_sfs.sort()
within_host_gene_sfs = numpy.array(within_host_gene_sfs)
within_host_gene_prevalences.sort()
within_host_gene_prevalences = numpy.array(within_host_gene_prevalences)
within_host_null_gene_prevalences.sort()
within_host_null_gene_prevalences = numpy.array(within_host_null_gene_prevalences)

within_host_gene_multiplicities.sort()
within_host_gene_multiplicities = numpy.array(within_host_gene_multiplicities)

print within_host_gene_sfs.mean(), within_host_gene_sfs.std(), within_host_gene_sfs.max()

# Calculate counts of between host gene changes
between_host_gene_idx_counts = {}
for gene_idx in between_host_gene_idxs:
    if gene_idx not in between_host_gene_idx_counts:
        between_host_gene_idx_counts[gene_idx] = 0
    between_host_gene_idx_counts[gene_idx] += 1


between_host_gene_sfs = list(between_host_gene_idx_counts.values())

between_host_gene_prevalences = []
for gene_idx in between_host_gene_idxs:
    between_host_gene_prevalences.append(prevalences[gene_idx])
    
between_host_gene_prevalences.sort()
between_host_gene_prevalences = numpy.array(between_host_gene_prevalences)

# Bootstrap between-host multiplicities
between_host_gene_multiplicities = []
between_host_gene_sfs = []
num_bootstraps = 1
for i in xrange(0,num_bootstraps):
    
    bootstrapped_gene_idxs = choice(between_host_gene_idxs,len(within_host_gene_idxs),replace=False)
    
    # Create idx map
    bootstrapped_gene_idx_map = {}
    for gene_idx in bootstrapped_gene_idxs:
        if gene_idx not in bootstrapped_gene_idx_map:
            bootstrapped_gene_idx_map[gene_idx]=0
            
        bootstrapped_gene_idx_map[gene_idx]+=1
        
    for gene_idx in bootstrapped_gene_idxs:
        between_host_gene_multiplicities.append( bootstrapped_gene_idx_map[gene_idx] )
    
    between_host_gene_sfs.extend( bootstrapped_gene_idx_map.values() )    
    
        
between_host_gene_multiplicities.sort()
between_host_gene_multiplicities = numpy.array(between_host_gene_multiplicities)

low_divergence_between_host_gene_prevalences = []
for gene_idx in low_divergence_between_host_gene_idxs:
    low_divergence_between_host_gene_prevalences.append(prevalences[gene_idx])

low_divergence_between_host_gene_prevalences.sort()
low_divergence_between_host_gene_prevalences = numpy.array(low_divergence_between_host_gene_prevalences)

# Done calculating... now plot figure!


y = 0
for snp_changes, snp_mutations, snp_reversions, gene_changes, gene_gains, gene_losses in zip(same_subject_snp_changes, same_subject_snp_mutations, same_subject_snp_reversions, same_subject_gene_changes, same_subject_gene_gains, same_subject_gene_losses):

    if snp_changes>-0.5 and snp_changes<0.5:
        snp_changes = 0.3
    
    if gene_changes>-0.5 and gene_changes<0.5:
        gene_changes = 0.3
    

    y-=2
    
    #within_snp_axis.semilogy([y,y], [snp_plower,snp_pupper],'g-',linewidth=0.25)
    within_snp_axis.semilogy([y], [snp_changes],'b.',markersize=1.5)
        
    #within_gene_axis.semilogy([y,y], [gene_plower,gene_pupper], 'g-',linewidth=0.25)
    within_gene_axis.semilogy([y],[gene_changes],  'b.',markersize=1.5)

    print "Mutations=%g, Reversions=%g, Gains=%g, Losses=%g" % (snp_mutations, snp_reversions, gene_gains, gene_losses)

y-=4

within_snp_axis.semilogy([y,y],[1e-09,1e09],'-',linewidth=0.25,color='k')
within_gene_axis.semilogy([y,y],[1e-09,1e09],'-',linewidth=0.25,color='k')


within_snp_axis.set_xlim([y-0.2,0])
within_gene_axis.set_xlim([y-0.2,0])    

within_snp_axis.set_xticks([])
within_gene_axis.set_xticks([])

within_snp_axis.set_yticks([])
within_snp_axis.minorticks_off()

within_gene_axis.set_yticks([])
within_gene_axis.minorticks_off()

#within_snp_axis.set_yticklabels([])
#within_gene_axis.set_yticklabels([])




y=0    
    
for snp_changes, gene_changes in zip(diff_subject_snp_changes, diff_subject_gene_changes)[0:50]:

    
    if snp_changes>-0.5 and snp_changes<0.5:
        snp_changes = 0.3
    
    if gene_changes>-0.5 and gene_changes<0.5:
        gene_changes = 0.3
    

    y-=1
    
    snp_axis.semilogy([y],[snp_changes],'r.',linewidth=0.35,markersize=1.5)
    gene_axis.semilogy([y],[gene_changes],'r.',linewidth=0.35,markersize=1.5)

y-=4

snp_axis.set_xlim([y-1,0])
gene_axis.set_xlim([y-1,0])    

snp_axis.set_xticks([])
gene_axis.set_xticks([])

#snp_axis.legend(loc='upper right',frameon=False)

#labels = snp_axis.get_yticklabels()
#print labels[0].get_text()
#labels[0].set_text('0')
#snp_axis.set_yticklabels(labels)

prevalence_bins = numpy.linspace(0,1,11)
prevalence_locations = prevalence_bins[:-1]+(prevalence_bins[1]-prevalence_bins[0])/2

#h = numpy.histogram(within_host_null_gene_prevalences,bins=prevalence_bins)[0]
#prevalence_axis.plot(prevalence_locations, h*1.0/h.sum(),'k-',label='Random')

h = numpy.histogram(between_host_gene_prevalences,bins=prevalence_bins)[0]
prevalence_axis.plot(prevalence_locations, h*1.0/h.sum(),'r.-',label='Between-host',markersize=3)

if len(low_divergence_between_host_gene_prevalences) > 0:
    print low_divergence_between_host_gene_prevalences
    print low_divergence_between_host_gene_prevalences.mean()
    print len(low_divergence_between_host_gene_prevalences), len(between_host_gene_prevalences)
    
    h = numpy.histogram(low_divergence_between_host_gene_prevalences,bins=prevalence_bins)[0]
    #prevalence_axis.plot(prevalence_locations, h*1.0/h.sum(),'r.-',label=('d<%g' % modification_divergence_threshold), alpha=0.5,markersize=3)

h = numpy.histogram(within_host_gene_prevalences,bins=prevalence_bins)[0]
prevalence_axis.plot(prevalence_locations, h*1.0/h.sum(),'b.-',label='Within-host',markersize=3)

print len(within_host_gene_prevalences), "within-host changes"

prevalence_axis.legend(loc='upper right',frameon=False,fontsize=4)

multiplicity_bins = numpy.arange(0,5)+0.5
multiplicity_locs = numpy.arange(1,5)

between_host_multiplicity_histogram = numpy.histogram(between_host_gene_multiplicities,bins=multiplicity_bins)[0]

within_host_multiplicity_histogram = numpy.histogram(within_host_gene_multiplicities,bins=multiplicity_bins)[0]



multiplicity_axis.bar(multiplicity_locs, between_host_multiplicity_histogram*1.0/between_host_multiplicity_histogram.sum(), width=0.3,color='r',linewidth=0)

multiplicity_axis.bar(multiplicity_locs-0.3, within_host_multiplicity_histogram*1.0/within_host_multiplicity_histogram.sum(), width=0.3,color='g',linewidth=0)


#prevalence_axis.set_ylim([0,0.6])

xs, ns = stats_utils.calculate_unnormalized_survival_from_vector(within_host_null_next_fold_changes)
parallelism_axis.step(xs,ns*1.0/ns[0],'k-',label='Random')

xs, ns = stats_utils.calculate_unnormalized_survival_from_vector(within_host_between_next_fold_changes)
parallelism_axis.step(xs,ns*1.0/ns[0],'r-',label='Between-host')

xs, ns = stats_utils.calculate_unnormalized_survival_from_vector(within_host_next_fold_changes)
parallelism_axis.step(xs,ns*1.0/ns[0],'b-',label='Within-host')

parallelism_axis.semilogx([1],[-1],'k.')
parallelism_axis.set_xlim([1,10])
sys.stderr.write("Saving figure...\t")
fig.savefig('%s/figure_6%s.pdf' % (parse_midas_data.analysis_directory, other_species_str),bbox_inches='tight')
sys.stderr.write("Done!\n")

    