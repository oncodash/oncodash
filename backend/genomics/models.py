from django.db import models
from enum import Enum

class AlterationType(Enum):
    AMP = "AMPLIFICATION"
    DEL = "DELETION"
    GAIN = "GAIN"
    LOSS = "LOSS"
    TRANS = "TRANSLOCATION"
    DUP = "DUPLICATION"
    INS = "INSERTION"
    FUS = "FUSION"
    UNK = "UNKNOWN"

class ActionableTargets:
    def targets_as_list(self):
        return ["ARAF","BRAF","CDK4","CDK6","CDKN2A","EGFR","ERBB2","FGFR1","FGFR2","FGFR3","FLT1","FLT4","KDR","KIT","KRAS","MAP2K1","MAP2K2","NRAS","NTRK1","NTRK2","NTRK3","PDGFRA","PDGFRB","PTCH1","RAF1","RET","ROS1","TEK"]


class CopyNumberAlteration(models.Model):
    ### "ID"			  "Gene"		"chr"	"start"		"end"		"strand"  "band"		"type"		"sample"	"nProbesCr"	"nProbesAf"  	"logR"     "baf"	    "nAraw"	    "nBraw"	 "nMajor"	"nMinor"	"purifiedLogR"	"purifiedBaf"	"purifiedLoh"	"CNstatus"	"LOHstatus"	"minPurifiedLogR"	"maxPurifiedLogR"	"breaksInGene"
    ### "ENSG00000177757"	"FAM87B"	"chr1"	"817371"	"819837"	"1"	    "p36.33"	"lincRNA"	"D327_BDNA13411"	"196557"	"114286"	"-0.0059"	"0.4998"	"0.9964"	"0.9955"	"1"	        "1"	        "-0.0059"	"0.4998"	        "4e-04" 	"Normal"	"HET"	    "-0.0059"	            "-0.0059"       	"0"

    patient_id = models.IntegerField()
    gene_id = models.CharField(max_length=30, default=None, blank=True, null=True) #primarily Ensemble ID (must be converted to entrez ID (or HUGO symbol))
    gene = models.CharField(max_length=15, default=None, blank=True, null=True)
    sample_id = models.CharField(max_length=15, default=None, blank=True, null=True)
    chromosome = models.CharField(max_length=6, default=None, blank=True, null=True)
    start = models.CharField(max_length=15, default=None, blank=True, null=True)
    end = models.CharField(max_length=15, default=None, blank=True, null=True)
    strand = models.CharField(max_length=15, default=None, blank=True, null=True)
    band = models.CharField(max_length=15, default=None, blank=True, null=True)
    type = models.CharField(max_length=15, default=None, blank=True, null=True)
    nProbesCr = models.CharField(max_length=15, default=None, blank=True, null=True)
    nProbesAf = models.CharField(max_length=15, default=None, blank=True, null=True)
    logR = models.CharField(max_length=15, default=None, blank=True, null=True)
    baf = models.CharField(max_length=15, default=None, blank=True, null=True)
    nAraw = models.CharField(max_length=15, default=None, blank=True, null=True)
    nBraw = models.CharField(max_length=15, default=None, blank=True, null=True)
    nMajor = models.CharField(max_length=15, default=None, blank=True, null=True)
    purifiedLogR = models.CharField(max_length=15, default=None, blank=True, null=True)
    purifiedBaf = models.CharField(max_length=15, default=None, blank=True, null=True)
    purifiedLoh = models.CharField(max_length=15, default=None, blank=True, null=True)
    CNstatus = models.CharField(max_length=15, default=None, blank=True, null=True)
    LOHstatus = models.CharField(max_length=15, default=None, blank=True, null=True)
    minPurifiedLogR = models.CharField(max_length=15, default=None, blank=True, null=True)
    maxPurifiedLogR = models.CharField(max_length=15, default=None, blank=True, null=True)
    breaksInGene = models.CharField(max_length=15, default=None, blank=True, null=True)

class Translocation(models.Model):
    patient_id = models.IntegerField()
    fusiongene = models.TextField()  # General gene name
    type = AlterationType
class SomaticVariant(models.Model):

    #patient	CHROM	POS	    REF	ALT	ID	FILTER	    cytoBand	Func.MANE	Gene.MANE	    GeneDetail.MANE	        ExonicFunc.MANE	AAChange.MANE	Func.refGene	Gene.refGene	GeneDetail.refGene	ExonicFunc.refGene	AAChange.refGene	genomicSuperDups	dbscSNV_ADA_SCORE	dbscSNV_RF_SCORE	COSMIC_ID	COSMIC_OCCURRENCE	COSMIC_TOTAL_OCC	COSMIC_CONF_SOMA	CLNSIG	CLNSIGCONF	CLNDN	CLNREVSTAT	CLNALLELEID	CLNDISDB	Interpro_domain	regulomeDB	CADD_raw	CADD_phred	1000G_ALL	1000G_EUR	gnomAD_genome_ALL	gnomAD_genome_NFE	gnomAD_genome_FIN	gnomAD_genome_max	gnomAD_exome_nc_ALL	gnomAD_exome_nc_NFE	gnomAD_exome_nc_NFE_SWE	gnomAD_exome_nc_FIN	gnomAD_exome_nc_max	Truncal	readCounts	samples
    #D327	    chr1	632680	T	A	.	alignment	1p36.33	    intergenic	OR4F29;OR4F16	dist=181002;dist=53036.	.	                       ncRNA_exonic	MIR12136	.	.	.	Score=0.995665;Name=chr5:181319945	.	.	..	.	.	.	.	.	.	.	.	.	.	0.91238	10.57	.	.	.	..	.	.	.	.	.	.	heterogeneous	52,1;30,0;48,3;36,0;45,13;32,10;54,2	D327_BDNA13411;D327_oPlf1_DNA2;D327_p2Asc1_DNA1;D327_p2Ome1_DNA1;D327_p2OvaL1_DNA1;D327_p2OvaR1_DNA2;D327_p2Per2_DNA1

    patient_id = models.IntegerField()
    ref_id = models.CharField(max_length=15, default=None, blank=True, null=True)  # Reference database identifier (dbSNP)
    chromosome = models.CharField(max_length=2, default=None, blank=True, null=True) # Chromosome number
    position = models.CharField(max_length=15, default=None, blank=True, null=True) # Position in reference genome
    reference_allele = models.CharField(max_length=15, default=None, blank=True, null=True)  # Allele in reference genome
    sample_allele = models.CharField(max_length=15, default=None, blank=True, null=True)  # Allele in sample genome
    filter = models.CharField(max_length=15, default=None, blank=True, null=True)
    cytoBand = models.CharField(max_length=15, default=None, blank=True, null=True)
    funcMANE = models.CharField(max_length=15, default=None, blank=True, null=True)
    geneMANE = models.CharField(max_length=15, default=None, blank=True, null=True)
    geneDetailMANE = models.CharField(max_length=15, default=None, blank=True, null=True)
    exonicFuncMANE = models.CharField(max_length=15, default=None, blank=True, null=True)
    aaChangeMANE = models.CharField(max_length=15, default=None, blank=True, null=True)
    funcRefGene = models.CharField(max_length=15, default=None, blank=True, null=True)
    geneRefGene = models.CharField(max_length=15, default=None, blank=True, null=True)
    geneDetailRefGene = models.CharField(max_length=15, default=None, blank=True, null=True)
    exonicFuncRefGene = models.CharField(max_length=15, default=None, blank=True, null=True)
    aaChangeRefGene = models.CharField(max_length=15, default=None, blank=True, null=True)
    genomicSuperDups = models.CharField(max_length=15, default=None, blank=True, null=True)
    dbscSNV_ADA_SCORE = models.CharField(max_length=15, default=None, blank=True, null=True)
    dbscSNV_RF_SCORE = models.CharField(max_length=15, default=None, blank=True, null=True)
    cosmic_id = models.CharField(max_length=15, default=None, blank=True, null=True)
    cosmic_occurrence = models.CharField(max_length=15, default=None, blank=True, null=True)
    cosmic_total_occ = models.CharField(max_length=15, default=None, blank=True, null=True)
    cosmic_conf_soma = models.CharField(max_length=15, default=None, blank=True, null=True)
    clnsig = models.CharField(max_length=15, default=None, blank=True, null=True)
    clnsigconf = models.CharField(max_length=15, default=None, blank=True, null=True)
    clndn = models.CharField(max_length=15, default=None, blank=True, null=True)
    clnrevstat = models.CharField(max_length=15, default=None, blank=True, null=True)
    clnalleleid = models.CharField(max_length=15, default=None, blank=True, null=True)
    clndisdb = models.CharField(max_length=15, default=None, blank=True, null=True)
    interpro_domain = models.CharField(max_length=15, default=None, blank=True, null=True)
    regulomeDB = models.CharField(max_length=15, default=None, blank=True, null=True)
    cadd_raw = models.CharField(max_length=15, default=None, blank=True, null=True)
    cadd_phred = models.CharField(max_length=15, default=None, blank=True, null=True)
    thousandG_ALL	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    thousandG_EUR	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    gnomAD_genome_ALL	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    gnomAD_genome_NFE	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    gnomAD_genome_FIN	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    gnomAD_genome_max	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    gnomAD_exome_nc_ALL	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    gnomAD_exome_nc_NFE	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    gnomAD_exome_nc_NFE_SWE	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    gnomAD_exome_nc_FIN	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    gnomAD_exome_nc_max	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    truncal	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    readCounts	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    samples = models.CharField(max_length=15, default=None, blank=True, null=True)

class CGIMutation(models.Model):

    # MUTATION	START	POS_HG19	END	CHR	ALT	REF	STRAND	INFO	TYPE	SYMBOL	TRANSCRIPT	PROTEIN_CHANGE	BOOSTDM_DS	BOOSTDM_SCORE	ONCOGENIC_CLASSIFICATION	SOURCE	CONSEQUENCE	IS_CANCER_GENE	CONSENSUS_ROLE
    # chr3:178936091 G>A	178936091	178653879	178936091	3	A	G	+	input02	SNV	KCNMB2-AS1	ENST00000668466	--	non-protein affecting		non-protein affecting		non_coding_transcript_exon_variant	NO

    patient_id = models.IntegerField()
    sample = models.CharField(max_length=15, default=None, blank=True, null=True)
    gene = models.CharField(max_length=15, default=None, blank=True, null=True)
    protein_change = models.CharField(max_length=128, default=None, blank=True, null=True)
    oncogenic_summary = models.CharField(max_length=128, default=None, blank=True, null=True)
    oncogenic_prediction = models.CharField(max_length=128, default=None, blank=True, null=True)
    ext_oncogenic_annotation = models.CharField(max_length=128, default=None, blank=True, null=True)
    mutation = models.CharField(max_length=128, default=None, blank=True, null=True)
    consequence = models.CharField(max_length=128, default=None, blank=True, null=True)
    transcript = models.CharField(max_length=128, default=None, blank=True, null=True)
    strand = models.CharField(max_length=15, default=None, blank=True, null=True)
    type = models.CharField(max_length=15, default=None, blank=True, null=True)

# pos_hg38 = models.CharField(max_length=15, default=None, blank=True, null=True)
    # pos_hg19 = models.CharField(max_length=15, default=None, blank=True, null=True)
    # chromosome = models.CharField(max_length=2) # Chromosome number
    # startpos = models.CharField(max_length=15, default=None, blank=True, null=True) # Position in reference genome
    # endpos = models.CharField(max_length=15, default=None, blank=True, null=True) # Position in reference genome
    # reference_allele = models.CharField(max_length=15, default=None, blank=True, null=True)  # Allele in reference genome
    # sample_allele = models.CharField(max_length=15, default=None, blank=True, null=True)  # Allele in sample genome
    # strand = models.CharField(max_length=2,default=None, blank=True, null=True)  # Allele in sample genome
    # type = models.CharField(max_length=8, default=None, blank=True, null=True)
    # symbol = models.CharField(max_length=15, default=None, blank=True, null=True)
    # transcript = models.CharField(max_length=15, default=None, blank=True, null=True)
    # protein_change = models.CharField(max_length=15, default=None, blank=True, null=True)
    # oncogenicity = models.CharField(max_length=15, default=None, blank=True, null=True)
    # boostdm_ds = models.CharField(max_length=15, default=None, blank=True, null=True)
    # boostdm_score = models.CharField(max_length=15, default=None, blank=True, null=True)
    # consequence = models.CharField(max_length=15, default=None, blank=True, null=True)
    # is_cancer_gene = models.CharField(max_length=15, default=None, blank=True, null=True)
    # consensus_role = models.CharField(max_length=15, default=None, blank=True, null=True)
    # source = models.CharField(max_length=15, default=None, blank=True, null=True)

class CGICopyNumberAlteration(models.Model):

    # sample	    gene	cna	predicted_in_tumors	                known_in_tumors	                                    gene_role	cancer	internal_id	driver	driver_statement	predicted_match	    known_match
    # single_sample	ERBB2	AMP	CESC;ESCA;HNSC;LUAD;PAAD;STAD;UCEC	BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED	Act	        OVE	     0	                known	            known in:           BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED

    patient_id = models.IntegerField()
    sample = models.CharField(max_length=15, default=None, blank=True, null=True)
    gene = models.CharField(max_length=15, default=None, blank=True, null=True)
    cnatype = models.CharField(max_length=15, default=None, blank=True, null=True)
    predicted_in_tumors = models.CharField(max_length=15, default=None, blank=True, null=True)
    known_in_tumors = models.CharField(max_length=15, default=None, blank=True, null=True)
    gene_role = models.CharField(max_length=15, default=None, blank=True, null=True)
    cancer = models.CharField(max_length=15, default=None, blank=True, null=True)
    driver = models.CharField(max_length=15, default=None, blank=True, null=True)
    driver_statement = models.CharField(max_length=15, default=None, blank=True, null=True)
    predicted_match = models.CharField(max_length=15, default=None, blank=True, null=True)
    known_match = models.CharField(max_length=15, default=None, blank=True, null=True)


class CGIFusionGene(models.Model):

    # sample	fus	effector_gene	gene_role	known_in_tumors	internal_id	cancer	driver	driver_statement	known_match
    # single_sample	ABL1__BCR	ABL1	Act	ALL;CML;CLL;AML;TCALL	0	OVE	known	known in: ALL;CML;CLL;AML;TCALL

    patient_id = models.IntegerField()
    sample = models.CharField(max_length=15, default=None, blank=True, null=True)
    fusiongene = models.CharField(max_length=15, default=None, blank=True, null=True)
    effector_gene = models.CharField(max_length=15, default=None, blank=True, null=True)
    gene_role = models.CharField(max_length=15, default=None, blank=True, null=True)
    known_in_tumors = models.CharField(max_length=15, default=None, blank=True, null=True)
    cancer = models.CharField(max_length=15, default=None, blank=True, null=True)
    driver = models.CharField(max_length=15, default=None, blank=True, null=True)
    driver_statement = models.CharField(max_length=15, default=None, blank=True, null=True)
    known_match = models.CharField(max_length=15, default=None, blank=True, null=True)

# CGI drug prescriptions
# SAMPLE	DISEASES	CTYPE	SAMPLE_ALTERATION	ALTERATION_MATCH	CTYPE_MATCH	DRUGS	BIOMARKER	RESPONSE	BIOMARKER_IDX	RESISTANCE_LIST	RESISTANCE_TYPE	EVIDENCE_LABEL	SOURCE	SOURCE_DETAILS
# sample	diseases	ctype	sample_alteration	alteration_match	ctype_match	drugs	biomarker	response	biomarker_idx	resistance_list	resistance_type	evidence_label	source	source_details

#Sample ID	Alterations	Biomarker	Drugs	Diseases	Response	Evidence	Match	Source	BioM	Resist.	Tumor type
class CGIDrugPrescriptions(models.Model):
    patient_id = models.IntegerField()
    sample = models.CharField(max_length=15, default=None, blank=True, null=True)
    alterations = models.CharField(max_length=15, default=None, blank=True, null=True)
    biomarker = models.CharField(max_length=15, default=None, blank=True, null=True)
    drugs = models.CharField(max_length=15, default=None, blank=True, null=True)
    diseases = models.CharField(max_length=15, default=None, blank=True, null=True)
    response = models.CharField(max_length=15, default=None, blank=True, null=True)
    evidence = models.CharField(max_length=15, default=None, blank=True, null=True)
    match = models.CharField(max_length=15, default=None, blank=True, null=True)
    source = models.CharField(max_length=15, default=None, blank=True, null=True)
    biom = models.CharField(max_length=15, default=None, blank=True, null=True)
    resistance = models.CharField(max_length=15, default=None, blank=True, null=True)
    tumor_type = models.CharField(max_length=15, default=None, blank=True, null=True)

class OncoKBAnnotation(models.Model):
    # {"query":{"id":null,"referenceGenome":"GRCh38","hugoSymbol":"FGFR3","entrezGeneId":2261,"alteration":"Amplification","alterationType":null,"svType":null,"tumorType":"HGSOC",
    # "consequence":null,"proteinStart":null,"proteinEnd":null,"hgvs":null},"geneExist":true,"variantExist":false,"alleleExist":false,"oncogenic":"Unknown",
    # "mutationEffect":{"knownEffect":"Unknown","description":"","citations":{"pmids":[],"abstracts":[]}},"highestSensitiveLevel":null,"highestResistanceLevel":null,
    # "highestDiagnosticImplicationLevel":null,"highestPrognosticImplicationLevel":null,"highestFdaLevel":null,"otherSignificantSensitiveLevels":[],
    # "otherSignificantResistanceLevels":[],"hotspot":false,"geneSummary":"FGFR3, a receptor tyrosine kinase, is altered by mutation, chromosomal rearrangement or amplification
    # in various cancers, most frequently in bladder cancer.","variantSummary":"The biologic significance of the FGFR3 amplification is unknown.",
    # "tumorTypeSummary":"There are no FDA-approved or NCCN-compendium listed treatments specifically for patients with FGFR3-amplified high-grade serous ovarian cancer.",
    # "prognosticSummary":"","diagnosticSummary":"","diagnosticImplications":[],"prognosticImplications":[],"treatments":[],"dataVersion":"v4.2","lastUpdate":"01/10/2017","vus":false}
    patient_id = models.IntegerField()
    referenceGenome = models.CharField(max_length=15, default=None, blank=True, null=True)
    hugoSymbol = models.CharField(max_length=15, default=None, blank=True, null=True)
    entrezGeneId = models.CharField(max_length=15, default=None, blank=True, null=True)
    alteration = models.CharField(max_length=15, default=None, blank=True, null=True)
    alterationType = models.CharField(max_length=15, default=None, blank=True, null=True)
    svType = models.CharField(max_length=15, default=None, blank=True, null=True)
    tumorType = models.CharField(max_length=15, default=None, blank=True, null=True)
    consequence = models.CharField(max_length=15, default=None, blank=True, null=True)
    proteinStart = models.CharField(max_length=15, default=None, blank=True, null=True)
    proteinEnd = models.CharField(max_length=15, default=None, blank=True, null=True)
    hgvs = models.CharField(max_length=15, default=None, blank=True, null=True)
    geneExist = models.CharField(max_length=15, default=None, blank=True, null=True)
    variantExist = models.CharField(max_length=15, default=None, blank=True, null=True)
    alleleExist = models.CharField(max_length=15, default=None, blank=True, null=True)
    oncogenic = models.CharField(max_length=15, default=None, blank=True, null=True)
    mutationEffectDescription = models.CharField(max_length=15, default=None, blank=True, null=True)
    knownEffect = models.CharField(max_length=15, default=None, blank=True, null=True)
    citationPMids = models.CharField(max_length=15, default=None, blank=True, null=True)
    citationAbstracts = models.CharField(max_length=15, default=None, blank=True, null=True)
    highestSensitiveLevel = models.CharField(max_length=15, default=None, blank=True, null=True)
    highestResistanceLevel = models.CharField(max_length=15, default=None, blank=True, null=True)
    highestDiagnosticImplicationLevel = models.CharField(max_length=15, default=None, blank=True, null=True)
    highestPrognosticImplicationLevel = models.CharField(max_length=15, default=None, blank=True, null=True)
    highestFdaLevel = models.CharField(max_length=15, default=None, blank=True, null=True)
    otherSignificantSensitiveLevels = models.CharField(max_length=15, default=None, blank=True, null=True)
    otherSignificantResistanceLevels = models.CharField(max_length=15, default=None, blank=True, null=True)
    hotspot = models.CharField(max_length=15, default=None, blank=True, null=True)
    geneSummary = models.CharField(max_length=15, default=None, blank=True, null=True)
    variantSummary = models.CharField(max_length=15, default=None, blank=True, null=True)
    tumorTypeSummary = models.CharField(max_length=15, default=None, blank=True, null=True)
    prognosticSummary = models.CharField(max_length=15, default=None, blank=True, null=True)
    diagnosticSummary = models.CharField(max_length=15, default=None, blank=True, null=True)
    diagnosticImplications = models.CharField(max_length=15, default=None, blank=True, null=True)
    prognosticImplications = models.CharField(max_length=15, default=None, blank=True, null=True)
    treatments = models.CharField(max_length=15, default=None, blank=True, null=True)
    dataVersion = models.CharField(max_length=15, default=None, blank=True, null=True)
    lastUpdate = models.CharField(max_length=15, default=None, blank=True, null=True)
    vus = models.CharField(max_length=15, default=None, blank=True, null=True)


# class DrugTarget(models.Model):
#
#     #Gene	ENSGID	RefSeq	RefSeq_Clinical	UniProtKB	UniProtKB_version
#     gene = models.TextField()  # General gene name
#     ensembleid = models.CharField(max_length=15, default=None, blank=True, null=True)  # Ensemble id
#     refseqid = models.CharField(max_length=15, default=None, blank=True, null=True)  # RefSeq id
#     rsclinical = models.CharField(max_length=15, default=None, blank=True, null=True)  # RefSeq clinical id
#     uniprotid = models.CharField(max_length=15, default=None, blank=True, null=True)  # UniProt id
#     uniprotver = models.CharField(max_length=15, default=None, blank=True, null=True)  # UniProt version
#     synonyms = models.TextField() # Alternative gene names separated with comma(,)
#
#     class Meta:
#         constraints = [models.UniqueConstraint(fields=["drug_target_id"], name='did')]

#class FinproveActionableAberrations(models.Model):

    # Patient	Targeted_therapy	Actionable_change	Consequence	Consequence_certainty	Indication_for_Finprove	Tier	Suggested_if_available


# class HRRPathogenicMutations(models.Model):
    # patient	HR_gene_mutation_LOH	Origin	HR_gene_heterogeneous_loss_of_function_mutation	Origin

# class GermlinePathogenicVariants(models.Model):
    # Patient	Germline_pathogenic_variant
