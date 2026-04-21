import os
import re
import sys
import json
import toml
import neo4j
import flask
import flask_cors
import logging


class PatientDTO:
    """Properties of `patient` nodes"""
    age_at_diagnosis = int
    bmi_at_diagnosis = float  # FIXME was int, but generated an error in Neo4j import, being unable to interpret floating point as int
    brca_mutation_status = str
    chronic_illnesses_at_dg = bool
    chronic_illnesses_type = str
    clinical_trial = bool
    cohort_code = str
    current_treatment_phase = str
    days_from_beva_maintenance_end_to_progression = int
    days_to_death = int
    days_to_progression = int
    debulking_surgery_ids = bool
    drug_trial_name = str
    drug_trial_unblinded = bool
    event_series = str
    followup_time = int
    germline_pathogenic_variant = str
    height_at_diagnosis = int
    histology = str
    hr_signature_per_patient = str
    hr_signature_pretreatment_wgs = str
    hrd_myriad_status = str
    maintenance_therapy = str
    operation1_cancelled = bool
    operation2_cancelled = bool
    paired_fresh_samples_available = bool
    patient_id = str
    platinum_free_interval = int
    platinum_free_interval_at_update = int
    previous_cancer = bool
    previous_cancer_diagnosis = str
    primary_therapy_outcome = str
    progression = bool
    residual_tumor_ids = str
    residual_tumor_pds = str
    sequencing_available = bool
    stage = str
    survival = str  # FIXME should be bool
    time_series = str
    treatment_strategy = str
    weight_at_diagnosis = int
    wgs_available = bool


class SampleInfo:
    """properties attached to `sample` nodes"""
    sample = str
    purity = str # FIXME only for SNV
    ploidy = str # FIXME only for AMP
    tumor_site = str # OK
    sample_time = str # OK
    sample_type = str # FIXME _sside_ or sord ?

class SampleInfoList:
    name = str
    row = list  # of SampleInfo

class AlterationSampleDataSV:
    sample = str

class AlterationSampleDataCNV:
    """Properties of `samples_carries_variant` edges from `sample` to `copy_number_amplification`"""
    sample = str
    nMajor = str # OK
    nMinor = str # OK

class AlterationSampleDataSNP:
    """Properties of `samples_carries_variant` edges from `sample` to `short_mutation`"""
    samples = str # FIXME
    AD__0 = str  # __ => .  # OK
    AD__1 = str  # __ => .  # OK
    DP = str  # OK
    AF = str  # OK
    nMajor = str # OK
    nMinor = str # OK
    LOHstatus = str # OK
    expHomCI__cover = str  # __ => .  # OK

class AlterationData:
    name = str
    description = str
    reported_sensitivity = str
    row = list  # of AlterationSampleData*

class GeneData:
    description = str
    alterations = list  # of AlterationData

class Genomic:
    actionable_aberrations = (int, str)
    putative_functionally_relevant_variants = (int, str)
    other_variants = (int, str)

class GenomicData:
    genomic = Genomic
    actionable_aberrations = GeneData
    putative_functionally_relevant_variants = GeneData
    other_variants = GeneData
    samples_info = SampleInfoList


class API:

    def __init__(self, app, config):
        self.app = app
        self.config = config

    def endpoints(self, ):
        links = {}
        module = sys.modules[__name__]
        for rule in self.app.url_map.iter_rules():
            func = rule.endpoint
            if hasattr(module, func):
                doc = getattr(module, func).__doc__
                url = str(rule)
                links[url] = doc
        return links


    def cypher(self, query):
        with neo4j.GraphDatabase.driver(self.config["neo4j"]["uri"], auth=self.config["neo4j"]["auth"]) as db:
            self.app.logger.debug(f"│ {query}")
            records, _, _ = db.execute_query(
                query,
                name=self.config["neo4j"]["user"], database_ = self.config["neo4j"]["database"])
        return records


    def fields(self, cls):
        for f in dir(cls):
            if not re.match(r'^__', f):
                yield f


    def cast(self, cls, key, val):
        return getattr(cls, key)(val)


    def cast_as(self, record, cls):
        dic = {}
        for key,val in record._properties.items():
            if key in self.fields(cls):
                dic[key] = self.cast(cls, key, val)
        return dic

    def search_alteration(self, name, alterations):
        for a in alterations:
            if a["name"] == name:
                return a
        return None

    def search_sample(self, id, samples):
        for s in samples:
            if s["sample"] == id:
                return s
        return None

    def genome_of(self, patient_id, records):

        self.app.logger.debug(f"│ Parse {len(records)} records of patient {patient_id}")

        genome = {}
        samples = []

        for r in records:
            # self.app.logger.debug("##### RECORDS #####")
            # for k in r.keys():
            #     self.app.logger.debug(f"{k}: {r[k]}")
            gene = r["g"]._properties["gene_symbol"]
            if gene not in genome.keys():
                if "name" in r["g"]._properties: 
                    gene_data = {
                        "description": r["g"]._properties["name"],
                        "alterations": [],
                    }
                else:
                    gene_data = {
                        "description": "",
                        "alterations": [],
                    }
                genome[gene] = gene_data

            sample = r["s"]
            existing = self.search_sample(sample["id"], samples)
            if not existing:
                sampleInfo = self.cast_as(sample, SampleInfo)
                sampleInfo["sample"] = sample._properties["id"]
                samples.append( sampleInfo )

            sample_carries_variant = r["scv"]

            labels = r["sv"]._labels
            alterationSampleData = {}
            alt_type = "unknown"
            if "ShortMutation" in labels:
                alterationSampleData = self.cast_as(sample_carries_variant, AlterationSampleDataSNP)
                alterationSampleData["sample"] = sample["id"]
                alterationSampleData["AD.1"] = alterationSampleData["AD__1"]
                del alterationSampleData["AD__1"]
                alterationSampleData["AD.0"] = alterationSampleData["AD__0"]
                del alterationSampleData["AD__0"]
                alterationSampleData["sample"] = alterationSampleData["sample"].replace(":sample", "")
                alt_type = "short mutation"
            elif "StructuralVariant" in labels:
                alterationSampleData = self.cast_as(sample_carries_variant, AlterationSampleDataSV)
                alterationSampleData["sample"] = sample["id"]
                alterationSampleData["sample"] = alterationSampleData["sample"].replace(":sample", "")
                alt_type = "structural variant"
            elif "CopyNumberAmplification" in labels:
                alterationSampleData = self.cast_as(sample_carries_variant, AlterationSampleDataCNV)
                alterationSampleData["sample"] = sample["id"]
                alterationSampleData["sample"] = alterationSampleData["sample"].replace(":sample", "")
                alt_type = "copy number amplification"
            else:
                self.app.logger.error(f"I don't know what kind of mutation has labels: {labels}")


            alteration_name = r["sv"]._properties["id"]
            existing = self.search_alteration(alteration_name, genome[gene]["alterations"])
            effect = "Responsive" # FIXME extract effect from data
            if existing:
                existing_sample = self.search_sample(alterationSampleData["sample"], existing["row"])
                if not existing_sample:
                    existing["row"].append(alterationSampleData)
                if "t" in r.keys():
                    drug = r["t"]._properties["id"].split(":")[0]
                    existing["drugs"].append(drug)
            else:
                alterationData = {}
                alterationData["name"] = alteration_name
                if "mutation_effect_description" in r['sv']._properties:
                    alterationData["description"] = r['sv']._properties["mutation_effect_description"] #FIXME description"
                    self.app.logger.debug(f"Found a SV description : {r['sv']._properties["mutation_effect_description"]}")
                else:
                    alterationData["description"] = "Unknown"
                alterationData["row"] = [alterationSampleData]
                alterationData["alt_type"] = alt_type
                if "t" in r.keys():
                    drug = r["t"]._properties["id"].split(":")[0]
                    alterationData["effect"] = effect
                    alterationData["drugs"] = [drug]
                else:
                    alterationData["effect"] = ""
                    alterationData["drugs"] = []

                genome[gene]["alterations"].append(alterationData)

        for gene in genome:
            for alt in genome[gene]["alterations"]:
                drugs = []
                for drug in set(alt["drugs"]):
                    drugs.append(drug.strip().replace(" "," ").replace(":"," "))
                if drugs:
                    alt["reported_sensitivity"] = f"{alt['effect']}: {' '.join(drugs)}"
                else:
                    alt["reported_sensitivity"] = "none"

        self.app.logger.debug(f"│ │ {len(samples)} samples")
        self.app.logger.debug(f"│ │ {len(genome.keys())} genes")
        self.app.logger.debug( "│ └OK")

        return genome, samples


    def actionables(self, patient_id):
  # #     Actionable mutations
        # query = \
        #     " MATCH (start:Patient)" \
        #         "-[*1]->(s:Sample)" \
        #         "-[scv:SampleCarriesVariant]->(sv:SequenceVariant)" \
        #         "-[]->(gs:GeneStatus)" \
        #         "-[]->(t:Treatment)" \
        #     f" WHERE (start.id = '{patient_id}')" \
        #         "AND (gs.gene_role = 'loss' AND scv.homogenous = true)" \
        #     " RETURN DISTINCT s, scv, sv, t" \
        #     " UNION" \
        #     " MATCH (start:Patient)" \
        #         "-[*1]->(s:Sample)" \
        #         "-[scv:SampleCarriesVariant]->(sv:SequenceVariant)" \
        #         "-[]->(gs:GeneStatus)" \
        #         "-[]->(t:Treatment)" \
        #     f" WHERE (start.id = '{patient_id}')" \
        #     " AND (gs.gene_role = 'gain' AND scv.expressed = true)" \
        #     " RETURN DISTINCT s, scv, sv, t" \
        #     " NEXT" \
        #     " MATCH (start)-[]->(s)-[scv]->(sv)-[]->(gs)-[:GeneStatusAffectsGene]-> (g:Gene)" \
        #     " RETURN DISTINCT s, scv, sv, g, t" 

# Actionable 
        query = \
            " MATCH path = (start:Patient)" \
                "-[*1]->(s:Sample)" \
                "-[scv:SampleCarriesVariant]->(sv:SequenceVariant)" \
                "-[]->(gs:GeneStatus)" \
                "-[vbt:VariantBiomarkerForTreatment]->(t:Treatment)" \
            f"  WHERE (start.id = '{patient_id}')" \
            "  AND (gs.gene_role = 'loss' AND scv.homogenous = true)" \
            "  RETURN DISTINCT s, scv, sv, vbt, t" \
            "  UNION" \
            "  MATCH path = (start:Patient)" \
                "-[*1]->(s:Sample)" \
                "-[scv:SampleCarriesVariant]->(sv:SequenceVariant)" \
                "-[]->(gs:GeneStatus)" \
                "-[vbt:VariantBiomarkerForTreatment]->(t:Treatment)" \
            f"  WHERE (start.id = '{patient_id}') " \
            "  AND (gs.gene_role = 'gain' AND scv.expressed = true)" \
            "  RETURN DISTINCT s, scv, sv, vbt, t" \
            " NEXT " \
            " MATCH (sv)-[]->(gs)-[:GeneStatusAffectsGene]->(g:Gene)" \
            " RETURN DISTINCT s, scv, sv, vbt, t, gs, g" \
            " ORDER BY vbt.Tier, g.gene_symbol"
            
        records = self.cypher(query)
        genome, samples = self.genome_of(patient_id, records)

        nb_alterations = 0
        for gene in genome:
            nb_alterations += len(genome[gene]["alterations"])
            # for a in genome[gene]["alterations"]:
            #     self.app.logger.debug(a["reported_sensitivity"])

        return genome, samples, nb_alterations


    # def relevants(self, patient_id):
    #     records = self.cypher(
    #         " MATCH (p:Patient)"
    #             "-[pcs:PatientCarriesSample]->(s:Sample)"
    #             "-[scv:SampleCarriesVariant]->(sv:SequenceVariant)"
    #             "-[]->(gs:GeneStatus)"
    #             "-[vbt:VariantBiomarkerForTreatment]->(t:Treatment)"
    #         f" WHERE (p.id = '{patient_id}')"
    #             " AND (vbt.fda_level IN ['3.0','4.0'])"
    #         " RETURN DISTINCT s, scv, sv, t"
    #         " NEXT"
    #         " MATCH (sv)-[]->(gs)"
    #             "-[:GeneStatusAffectsGene]->(g:Gene)"
    #         " RETURN DISTINCT s, scv, sv, g, t"
    #     )
    #     genome, samples = self.genome_of(patient_id, records)

    #     nb_alterations = 0
    #     for gene in genome:
    #         nb_alterations += len(genome[gene]["alterations"])

    #     return genome, samples, nb_alterations


    def others(self, patient_id):
        # Not relevant
        records = self.cypher(
            " CALL {"
            "MATCH (start:Patient)"
                "-[*1]->()"
                "-[scv:SampleCarriesVariant]->(sv:SequenceVariant)"
                "-[]->(gs:GeneStatus)"
            f" WHERE (start.id = '{patient_id}')"
                " AND (gs.gene_role = 'loss' AND scv.homogenous = true)"
            " RETURN sv.id AS actionable_id"
            " UNION"
            " MATCH (start:Patient)"
                "-[*1]->(s:Sample)"
                "-[scv:SampleCarriesVariant]->(sv:SequenceVariant)"
                "-[]->(gs:GeneStatus)"
            f" WHERE (start.id = '{patient_id}')"
                " AND (gs.gene_role = 'gain' AND scv.expressed = true)"
            " RETURN sv.id AS actionable_id"
            " }"
            " WITH collect(actionable_id) AS actionable_ids"
            " MATCH (start:Patient)"
                "-[*1]->(s:Sample)"
                "-[scv:SampleCarriesVariant]->(sv:SequenceVariant)"
            f" WHERE (start.id = '{patient_id}')"
                " AND NOT sv.id IN actionable_ids"
            " RETURN DISTINCT s, scv, sv"
            " NEXT"
            " MATCH (start)-[]->(s)-[scv]->(sv)-[]->(gs)-[:GeneStatusAffectsGene]-> (g:Gene)"
            " RETURN DISTINCT s, scv, sv, g"
            )
        genome, samples = self.genome_of(patient_id, records)

        nb_alterations = 0
        for gene in genome:
            nb_alterations += len(genome[gene]["alterations"])

        return genome, samples, nb_alterations

