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

class AlterationTypeLCase(Enum):
    AMP = "Amplification"
    DEL = "Deletion"
    UNK = "Unknown"
    def __str__(self):
        return str(self.value)

class CGI2OncoKBLevels(Enum):
    A = "LEVEL_1"
    B = "LEVEL_2"
    C = "LEVEL_3A"
    D = "LEVEL_3B"
    E = "LEVEL_4"
    R1 = "LEVEL_R1"
    R2 = "LEVEL_R2"
    def __str__(self):
        return str(self.value)

class ActionableTarget(models.Model):

    gene = models.CharField(max_length=15, primary_key=True, default=None, blank=False, null=False)
class CopyNumberAlteration(models.Model):

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

    class Meta:
        unique_together = ['sample_id', 'gene_id']

class Translocation(models.Model):
    patient_id = models.IntegerField()
    sample = models.CharField(max_length=64, default=None, blank=True, null=True)
    fusiongene =  models.CharField(max_length=64, default=None, blank=True, null=True)
    type = AlterationType

class CNAscatEstimate(models.Model):
    patient_id = models.IntegerField()
    sample = models.CharField(max_length=64, default=None, blank=True, null=True)
    aberrant = models.BooleanField(default=False, blank=False, null=True)
    purity = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    psi = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    ploidy = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    TP53_purity_mean = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    TP53_VAF = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    goodnessOfFit = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    penalizedGoodnessOfFit = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)

class SomaticVariant(models.Model):

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

    class Meta:
        unique_together = ['patient_id', 'chromosome', 'position']

class CGIMutation(models.Model):

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

    class Meta:
        unique_together = ['patient_id', 'mutation']

class CGICopyNumberAlteration(models.Model):

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

    class Meta:
        unique_together = ['sample', 'gene', 'cnatype']

class CGIFusionGene(models.Model):

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

    class Meta:
        unique_together = ['patient_id', 'sample', 'alterations', 'biomarker', 'evidence']

class OncoKBAnnotation(models.Model):

    patient_id = models.IntegerField()
    sample_id = models.CharField(max_length=64, default=None, blank=True, null=True)
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
    vus = models.BooleanField(default=False, blank=True, null=True)
    nMinor = models.IntegerField(null=True)
    nMajor = models.IntegerField(null=True)
    ad0 = models.IntegerField(null=True)
    ad1 = models.IntegerField(null=True)
    af = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=4)
    dp = models.IntegerField(null=True)
    lohstatus = models.CharField(max_length=16, default=None, blank=True, null=True)
    exphomci = models.BooleanField(default=False, blank=False, null=True)
    readcount = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['sample_id', 'hugoSymbol', 'alteration']

class cna_annotation(models.Model):

    patient_id = models.CharField(max_length=64, default=None, blank=True, null=True)
    sample_id = models.CharField(max_length=64, default=None, blank=True, null=True)
    referenceGenome = models.CharField(max_length=16, default=None, blank=True, null=True)
    hugoSymbol = models.CharField(max_length=32, default=None, blank=True, null=True)
    entrezGeneId = models.CharField(max_length=32, default=None, blank=True, null=True)
    alteration = models.CharField(max_length=16, default=None, blank=True, null=True)
    tumorType = models.CharField(max_length=16, default=None, blank=True, null=True)
    consequence = models.CharField(max_length=16, default=None, blank=True, null=True)
    proteinStart = models.CharField(max_length=16, default=None, blank=True, null=True)
    proteinEnd = models.CharField(max_length=16, default=None, blank=True, null=True)
    oncogenic = models.CharField(max_length=32, default=None, blank=True, null=True)
    mutationEffectDescription = models.CharField(max_length=1024, default=None, blank=True, null=True)
    gene_role = models.CharField(max_length=64, default=None, blank=True, null=True) #oncokb knowneffect
    citationPMids = models.CharField(max_length=1024, default=None, blank=True, null=True)
    geneSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    variantSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    tumorTypeSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    diagnosticSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    diagnosticImplications = models.CharField(max_length=512, default=None, blank=True, null=True)
    prognosticImplications = models.CharField(max_length=512, default=None, blank=True, null=True)
    prognosticSummary = models.CharField(max_length=512, default=None, blank=True, null=True)
    treatments = models.CharField(max_length=1024, default=None, blank=True, null=True)
    ploidy = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=16)
    nMinor = models.IntegerField(null=True)
    nMajor = models.IntegerField(null=True)
    lohstatus = models.CharField(max_length=16, default=None, blank=True, null=True)
    oncokb_level = models.CharField(max_length=32, default=None, blank=True, null=True)
    cgi_level = models.CharField(max_length=32, default=None, blank=True, null=True)
    rank = models.IntegerField(null=True)

    #class Meta:
    #    unique_together = ['sample_id', 'hugoSymbol', 'alteration']

class snv_annotation(models.Model):

    # generic
    patient_id = models.CharField(max_length=64, default=None, blank=True, null=True)
    sample_id = models.CharField(max_length=64, default=None, blank=True, null=True)
    ref_id = models.CharField(max_length=15, default=None, blank=True, null=True)  # Reference database identifier (dbSNP)
    chromosome = models.CharField(max_length=2, default=None, blank=True, null=True)  # Chromosome number
    position = models.BigIntegerField(blank=True, null=True)  # Position in reference genome
    reference_allele = models.CharField(max_length=15, default=None, blank=True, null=True)
    sample_allele = models.CharField(max_length=15, default=None, blank=True, null=True)  # Allele in sample genome
    referenceGenome = models.CharField(max_length=16, default=None, blank=True, null=True)
    hugoSymbol = models.CharField(max_length=32, default=None, blank=True, null=True)
    entrezGeneId = models.CharField(max_length=32, default=None, blank=True, null=True)
    alteration = models.CharField(max_length=16, default=None, blank=True, null=True)
    tumorType = models.CharField(max_length=16, default=None, blank=True, null=True)
    consequence = models.CharField(max_length=16, default=None, blank=True, null=True)
    proteinStart = models.CharField(max_length=16, default=None, blank=True, null=True)
    proteinEnd = models.CharField(max_length=16, default=None, blank=True, null=True)
    oncogenic = models.CharField(max_length=32, default=None, blank=True, null=True)
    mutationEffectDescription = models.CharField(max_length=1024, default=None, blank=True, null=True)
    gene_role = models.CharField(max_length=64, default=None, blank=True, null=True) #oncokb knowneffect
    citationPMids = models.CharField(max_length=1024, default=None, blank=True, null=True)
    geneSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    variantSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    tumorTypeSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    diagnosticSummary = models.CharField(max_length=1024, default=None, blank=True, null=True)
    diagnosticImplications = models.CharField(max_length=512, default=None, blank=True, null=True)
    prognosticImplications = models.CharField(max_length=512, default=None, blank=True, null=True)
    prognosticSummary = models.CharField(max_length=512, default=None, blank=True, null=True)
    treatments = models.CharField(max_length=1024, default=None, blank=True, null=True)
    nMinor = models.IntegerField(null=True)
    nMajor = models.IntegerField(null=True)
    oncokb_level = models.CharField(max_length=32, default=None, blank=True, null=True)
    cgi_level = models.CharField(max_length=32, default=None, blank=True, null=True)
    rank = models.IntegerField(null=True)

    # sample specific
    ad0 = models.IntegerField(null=True)
    ad1 = models.IntegerField(null=True)
    af = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=4)
    readcount = models.IntegerField(blank=True, null=True, default=None)
    depth = models.IntegerField(null=True)
    lohstatus = models.CharField(max_length=16, default=None, blank=True, null=True)
    hom_lo = models.DecimalField(default=None, blank=True, null=True, max_digits=10, decimal_places=2)
    hom_hi = models.DecimalField(default=None, blank=True, null=True, max_digits=10, decimal_places=2)
    hom_pbinom_lo = models.DecimalField(default=None, blank=True, null=True, max_digits=10, decimal_places=2)
    homogenous = models.BooleanField(default=False, blank=False, null=True)  # truncal field??

    # SNV specific
    funcMane = models.CharField(max_length=32, default=None, blank=True, null=True)
    funcRefgene = models.CharField(max_length=32, default=None, blank=True, null=True)
    exonicFuncMane = models.CharField(max_length=32, default=None, blank=True, null=True)
    cadd_score = models.DecimalField(default=None, blank=True, null=True, max_digits=10, decimal_places=3)
    ada_score = models.DecimalField(default=None, blank=True, null=True, max_digits=10, decimal_places=3)
    rf_score = models.DecimalField(default=None, blank=True, null=True, max_digits=10, decimal_places=3)
    sift_cat = models.CharField(max_length=32, default=None, blank=True, null=True)
    sift_val = models.DecimalField(default=None, blank=True, null=True, max_digits=10, decimal_places=3)
    polyphen_cat = models.CharField(max_length=32, default=None, blank=True, null=True)
    polyphen_val = models.DecimalField(default=None, blank=True, null=True, max_digits=10, decimal_places=3)
    amis_score = models.DecimalField(default=None, blank=True, null=True, max_digits=10, decimal_places=3)
    cosmic_id = models.CharField(max_length=32, default=None, blank=True, null=True)
    clinvar_id = models.CharField(max_length=32, default=None, blank=True, null=True)
    clinvar_sig = models.CharField(max_length=32, default=None, blank=True, null=True)
    clinvar_status = models.CharField(max_length=32, default=None, blank=True, null=True)
    clinvar_assoc = models.CharField(max_length=32, default=None, blank=True, null=True)
    pathogenecity = models.CharField(max_length=32, default=None, blank=True, null=True)
    classification = models.CharField(max_length=32, default=None, blank=True, null=True)


    #class Meta:
    #    unique_together = ['sample_id', 'hugoSymbol', 'alteration']