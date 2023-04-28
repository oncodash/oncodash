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
    def __str__(self):
        return str(self.value)

class CopyNumberAlteration(models.Model):
    ### "ID"			  "Gene"		"chr"	"start"		"end"		"strand"  "band"		"type"		"sample"	"nProbesCr"	"nProbesAf"  	"logR"     "baf"	    "nAraw"	    "nBraw"	 "nMajor"	"nMinor"	"purifiedLogR"	"purifiedBaf"	"purifiedLoh"	"CNstatus"	"LOHstatus"	"minPurifiedLogR"	"maxPurifiedLogR"	"breaksInGene"
    ### "ENSG00000177757"	"FAM87B"	"chr1"	"817371"	"819837"	"1"	    "p36.33"	"lincRNA"	"D327_BDNA13411"	"196557"	"114286"	"-0.0059"	"0.4998"	"0.9964"	"0.9955"	"1"	        "1"	        "-0.0059"	"0.4998"	        "4e-04" 	"Normal"	"HET"	    "-0.0059"	            "-0.0059"       	"0"

    patient_id = models.IntegerField()
    gene_id = models.CharField(max_length=15, default=None, blank=True, null=True) #primarily Ensemble ID (must be converted to entrez ID (or HUGO symbol))
    gene = models.CharField(max_length=15, default=None, blank=True, null=True)
    sample_id = models.CharField(max_length=30, default=None, blank=True, null=True)
    chromosome = models.CharField(max_length=6, default=None, blank=True, null=True)
    start = models.BigIntegerField(blank=True, null=True)
    end = models.BigIntegerField(blank=True, null=True)
    strand = models.IntegerField(blank=True, null=True)
    band = models.CharField(max_length=15, default=None, blank=True, null=True)
    type = models.CharField(max_length=15, default=None, blank=True, null=True)
    nProbesCr = models.IntegerField(blank=True, null=True)
    nProbesAf = models.IntegerField(blank=True, null=True)
    logR = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=6)
    baf = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=6)
    nAraw = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=6)
    nBraw = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=6)
    nMajor = models.IntegerField(blank=True, null=True)
    nMinor = models.IntegerField(blank=True, null=True)
    purifiedLogR = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=6)
    purifiedBaf = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=6)
    purifiedLoh = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=6)
    CNstatus = models.CharField(max_length=15, default=None, blank=True, null=True)
    LOHstatus = models.CharField(max_length=15, default=None, blank=True, null=True)
    minPurifiedLogR = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=6)
    maxPurifiedLogR = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=6)
    breaksInGene = models.IntegerField(blank=True, null=True)

# TODO: No internal data available. Translocations are discovered manually by geneticist, but can be automated by querying eg. Pfam database (need knowledge about protein domains in fusion gene)
class Translocation(models.Model):
    patient_id = models.IntegerField()
    sample = models.CharField(max_length=64, default=None, blank=True, null=True)
    fusiongene =  models.CharField(max_length=64, default=None, blank=True, null=True)
    type = AlterationType
class SomaticVariant(models.Model):
    # see https://brb.nci.nih.gov/seqtools/colexpanno.html
    #patient	CHROM	POS	    REF	ALT	ID	FILTER	    cytoBand	Func.MANE	Gene.MANE	    GeneDetail.MANE	        ExonicFunc.MANE	AAChange.MANE	Func.refGene	Gene.refGene	GeneDetail.refGene	ExonicFunc.refGene	AAChange.refGene	genomicSuperDups	dbscSNV_ADA_SCORE	dbscSNV_RF_SCORE	COSMIC_ID	COSMIC_OCCURRENCE	COSMIC_TOTAL_OCC	COSMIC_CONF_SOMA	CLNSIG	CLNSIGCONF	CLNDN	CLNREVSTAT	CLNALLELEID	CLNDISDB	Interpro_domain	regulomeDB	CADD_raw	CADD_phred	1000G_ALL	1000G_EUR	gnomAD_genome_ALL	gnomAD_genome_NFE	gnomAD_genome_FIN	gnomAD_genome_max	gnomAD_exome_nc_ALL	gnomAD_exome_nc_NFE	gnomAD_exome_nc_NFE_SWE	gnomAD_exome_nc_FIN	gnomAD_exome_nc_max	Truncal	readCounts	samples
    #D327	    chr1	632680	T	A	.	alignment	1p36.33	    intergenic	OR4F29;OR4F16	dist=181002;dist=53036.	.	                       ncRNA_exonic	MIR12136	.	.	.	Score=0.995665;Name=chr5:181319945	.	.	..	.	.	.	.	.	.	.	.	.	.	0.91238	10.57	.	.	.	..	.	.	.	.	.	.	heterogeneous	52,1;30,0;48,3;36,0;45,13;32,10;54,2	D327_BDNA13411;D327_oPlf1_DNA2;D327_p2Asc1_DNA1;D327_p2Ome1_DNA1;D327_p2OvaL1_DNA1;D327_p2OvaR1_DNA2;D327_p2Per2_DNA1

    patient_id = models.IntegerField()
    ref_id = models.CharField(max_length=15, default=None, blank=True, null=True)  # Reference database identifier (dbSNP)
    chromosome = models.CharField(max_length=2, default=None, blank=True, null=True) # Chromosome number
    position = models.BigIntegerField(blank=True, null=True) # Position in reference genome
    reference_allele = models.CharField(max_length=15, default=None, blank=True, null=True)
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
    dbscSNV_ADA_SCORE = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    dbscSNV_RF_SCORE = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
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
    cadd_raw = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    cadd_phred = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    thousandG_ALL	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    thousandG_EUR	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    gnomAD_genome_ALL	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    gnomAD_genome_NFE	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    gnomAD_genome_FIN	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    gnomAD_genome_max	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    gnomAD_exome_nc_ALL	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    gnomAD_exome_nc_NFE	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    gnomAD_exome_nc_NFE_SWE	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    gnomAD_exome_nc_FIN	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    gnomAD_exome_nc_max	 = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    truncal	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    readCounts	 = models.CharField(max_length=15, default=None, blank=True, null=True)
    samples = models.CharField(max_length=15, default=None, blank=True, null=True)

class CGIMutation(models.Model):

    # Sample ID	Gene	    Protein Change	Oncogenic Summary	    Oncogenic Prediction	External oncogenic annotation	Mutation	        Consequence	                        Transcript	    Strand	Type
    # input02	KCNMB2-AS1	--	            non-protein affecting	non-protein affecting	                            	chr3:178936091 G>A	non_coding_transcript_exon_variant	ENST00000668466	+	    SNV

    patient_id = models.IntegerField()
    sample = models.CharField(max_length=32, default=None, blank=True, null=True)
    gene = models.CharField(max_length=32, default=None, blank=True, null=True)
    protein_change = models.CharField(max_length=64, default=None, blank=True, null=True)
    oncogenic_summary = models.CharField(max_length=128, default=None, blank=True, null=True)
    oncogenic_prediction = models.CharField(max_length=128, default=None, blank=True, null=True)
    ext_oncogenic_annotation = models.CharField(max_length=128, default=None, blank=True, null=True)
    mutation = models.CharField(max_length=128, default=None, blank=True, null=True)
    consequence = models.CharField(max_length=128, default=None, blank=True, null=True)
    transcript = models.CharField(max_length=64, default=None, blank=True, null=True)
    strand = models.CharField(max_length=2, default=None, blank=True, null=True)
    type = models.CharField(max_length=16, default=None, blank=True, null=True)

class CGICopyNumberAlteration(models.Model):

    # sample	    gene	cna	predicted_in_tumors	                known_in_tumors	                                    gene_role	cancer	internal_id	driver	driver_statement	predicted_match	    known_match
    # single_sample	ERBB2	AMP	CESC;ESCA;HNSC;LUAD;PAAD;STAD;UCEC	BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED	Act	        OVE	     0	                known	            known in:           BRCA;OV;CANCER;NSCLC;ST;BT;COREAD;BLCA;GEJA;HNC;ED

    patient_id = models.IntegerField()
    sample = models.CharField(max_length=32, default=None, blank=True, null=True)
    gene = models.CharField(max_length=32, default=None, blank=True, null=True)
    cnatype = models.CharField(max_length=16, default=None, blank=True, null=True)
    predicted_in_tumors = models.CharField(max_length=128, default=None, blank=True, null=True)
    known_in_tumors = models.CharField(max_length=128, default=None, blank=True, null=True)
    gene_role = models.CharField(max_length=32, default=None, blank=True, null=True)
    cancer = models.CharField(max_length=16, default=None, blank=True, null=True)
    driver = models.CharField(max_length=64, default=None, blank=True, null=True)
    driver_statement = models.CharField(max_length=128, default=None, blank=True, null=True)
    predicted_match = models.CharField(max_length=128, default=None, blank=True, null=True)
    known_match = models.CharField(max_length=128, default=None, blank=True, null=True)


class CGIFusionGene(models.Model):

    # sample	fus	effector_gene	gene_role	known_in_tumors	internal_id	cancer	driver	driver_statement	known_match
    # single_sample	ABL1__BCR	ABL1	Act	ALL;CML;CLL;AML;TCALL	0	OVE	known	known in: ALL;CML;CLL;AML;TCALL

    patient_id = models.IntegerField()
    sample = models.CharField(max_length=32, default=None, blank=True, null=True)
    fusiongene = models.CharField(max_length=32, default=None, blank=True, null=True)
    effector_gene = models.CharField(max_length=32, default=None, blank=True, null=True)
    gene_role = models.CharField(max_length=32, default=None, blank=True, null=True)
    known_in_tumors = models.CharField(max_length=128, default=None, blank=True, null=True)
    cancer = models.CharField(max_length=16, default=None, blank=True, null=True)
    driver = models.CharField(max_length=64, default=None, blank=True, null=True)
    driver_statement = models.CharField(max_length=128, default=None, blank=True, null=True)
    known_match = models.CharField(max_length=128, default=None, blank=True, null=True)

# CGI drug prescriptions

# Sample ID	Alterations	Biomarker	Drugs	Diseases	Response	Evidence	Match	Source	BioM	Resist.	Tumor type
# single_sample	ABL1__BCR 	ABL1 (T315I,V299L,G250E,F317L)	Bosutinib (BCR-ABL inhibitor 3rd gen)	Acute lymphoblastic leukemia, Chronic myeloid leukemia	Resistant	A	NO	cgi	only gene		ALL, CML

class CGIDrugPrescriptions(models.Model):
    patient_id = models.IntegerField()
    sample = models.CharField(max_length=32, default=None, blank=True, null=True)
    alterations = models.CharField(max_length=128, default=None, blank=True, null=True)
    biomarker = models.CharField(max_length=256, default=None, blank=True, null=True)
    drugs = models.CharField(max_length=256, default=None, blank=True, null=True)
    diseases = models.CharField(max_length=256, default=None, blank=True, null=True)
    response = models.CharField(max_length=32, default=None, blank=True, null=True)
    evidence = models.CharField(max_length=32, default=None, blank=True, null=True) # one letter
    match = models.BooleanField(default=False, blank=False, null=False) #Yes/NO
    source = models.CharField(max_length=32, default=None, blank=True, null=True)
    biom = models.CharField(max_length=256, default=None, blank=True, null=True)
    resistance = models.CharField(max_length=128, default=None, blank=True, null=True) # co-occurring alteration
    tumor_type = models.CharField(max_length=32, default=None, blank=True, null=True)

class OncoKBAnnotation(models.Model):

    patient_id = models.IntegerField()
    referenceGenome = models.CharField(max_length=16, default=None, blank=True, null=True)
    hugoSymbol = models.CharField(max_length=32, default=None, blank=True, null=True)
    entrezGeneId = models.CharField(max_length=32, default=None, blank=True, null=True)
    alteration = models.CharField(max_length=16, default=None, blank=True, null=True)
    alterationType = models.CharField(max_length=16, default=None, blank=True, null=True)
    svType = models.CharField(max_length=16, default=None, blank=True, null=True)
    tumorType = models.CharField(max_length=16, default=None, blank=True, null=True)
    consequence = models.CharField(max_length=16, default=None, blank=True, null=True)
    proteinStart = models.CharField(max_length=16, default=None, blank=True, null=True)
    proteinEnd = models.CharField(max_length=16, default=None, blank=True, null=True)
    hgvs = models.CharField(max_length=16, default=None, blank=True, null=True) # human reference genome version
    geneExist = models.BooleanField(default=False, blank=False, null=True)
    variantExist = models.BooleanField(default=False, blank=False, null=True)
    alleleExist = models.BooleanField(default=False, blank=False, null=True)
    oncogenic = models.CharField(max_length=32, default=None, blank=True, null=True)
    mutationEffectDescription = models.CharField(max_length=1024, default=None, blank=True, null=True)
    knownEffect = models.CharField(max_length=64, default=None, blank=True, null=True)
    citationPMids = models.CharField(max_length=1024, default=None, blank=True, null=True)
    citationAbstracts = models.CharField(max_length=1024, default=None, blank=True, null=True)
    highestSensitiveLevel = models.CharField(max_length=16, default=None, blank=True, null=True)
    highestResistanceLevel = models.CharField(max_length=16, default=None, blank=True, null=True)
    highestDiagnosticImplicationLevel = models.CharField(max_length=16, default=None, blank=True, null=True)
    highestPrognosticImplicationLevel = models.CharField(max_length=16, default=None, blank=True, null=True)
    highestFdaLevel = models.CharField(max_length=16, default=None, blank=True, null=True)
    otherSignificantSensitiveLevels = models.CharField(max_length=16, default=None, blank=True, null=True)
    otherSignificantResistanceLevels = models.CharField(max_length=16, default=None, blank=True, null=True)
    hotspot = models.BooleanField(default=False, blank=False, null=True)
    geneSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    variantSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    tumorTypeSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    prognosticSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    diagnosticSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    diagnosticImplications = models.CharField(max_length=512, default=None, blank=True, null=True)
    prognosticImplications = models.CharField(max_length=512, default=None, blank=True, null=True)
    treatments = models.CharField(max_length=1024, default=None, blank=True, null=True)
    dataVersion = models.CharField(max_length=16, default=None, blank=True, null=True)
    lastUpdate = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    vus = models.BooleanField(default=False, blank=False, null=True)
