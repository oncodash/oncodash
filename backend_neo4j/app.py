import os
import re
import sys
import json
import toml
import flask
import neo4j
import logging
from markupsafe import escape
from werkzeug.exceptions import HTTPException, NotFound

app = flask.Flask(__name__)

config = {
    "neo4j": {
        "uri": "neo4j://localhost:7687",
        "user": "neo4j",
        "base": "oncodash",
    }
}
if os.path.isfile("oncodash_neo4j.toml"):
    config.update(toml.load("oncodash_neo4j.toml"))
app.logger.info(config)

with open("neo4j.pass") as fd:
    config["neo4j"]["passwd"] = fd.readline().strip()
config["neo4j"]["auth"] = (config["neo4j"]["user"], config["neo4j"]["passwd"])


def fields(cls):
    for f in dir(cls):
        if not re.match(r'^__', f):
            yield f

def cast(cls, key, val):
    return getattr(cls, key)(val)

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
    patient_id = int
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
    actionable_aberrations = str
    putative_functionally_relevant_variants = str
    other_variants = str

class GenomicData:
    genomic = Genomic
    actionable_aberrations = GeneData
    putative_functionally_relevant_variants = GeneData
    other_variants = GeneData
    samples_info = SampleInfoList


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    app.logger.debug(f"ERROR [{e.code}] {e.name} ⮧")
    return response


def endpoints():
    links = {}
    module = sys.modules[__name__]
    for rule in app.url_map.iter_rules():
        func = rule.endpoint
        if hasattr(module, func):
            doc = getattr(module, func).__doc__
            url = str(rule)
            links[url] = doc
    return links


@app.route("/")
def root():
    """Map of this website."""
    app.logger.debug(f"Asking for {root.__doc__}...")
    html = "<ul>"
    for url,doc in endpoints().items():
        if url == '/':
            continue
        a = escape(url)
        html += f"<li><a href='{url}'>{a}</a>: {doc}</li>"
    html += "</ul>"
    app.logger.debug("└OK")
    return html


@app.route("/map")
def map():
    """API map as JSON"""
    app.logger.debug(f"Asking for {map.__doc__}...")
    links = endpoints()
    app.logger.debug("└OK")
    return flask.jsonify(links)


@app.route("/ping")
def ping():
    """metadata about the Oncodash API"""
    app.logger.debug(f"Asking for {ping.__doc__}...")
    api_info = {
        "title": "Oncodash API",
        "summary": "Virtual Molecular Tumor Board Data access",
        "contact": {
            "name": "Johann Dreo",
            "email": "johann.dreo@pasteur.fr",
        },
        "version": "0.1.0",
    }
    app.logger.debug("└OK")
    return flask.jsonify({"info": api_info})


def cypher(query):
    with neo4j.GraphDatabase.driver(config["neo4j"]["uri"], auth=config["neo4j"]["auth"]) as db:
        app.logger.debug(f"│ {query}")
        records, _, _ = db.execute_query(
            query,
            name=config["neo4j"]["user"], database_ = config["neo4j"]["database"])
    return records


@app.route("/api/clinical-overview/data/<patient_id>")
def patient(patient_id):
    """data about a specific patient"""
    app.logger.debug(f"Asking for {patient.__doc__}: `{patient_id}`...")
    records = cypher(
        f"MATCH (p:Patient)"             \
        f" WHERE p.id = '{patient_id}'"  \
         " RETURN ALL *")
    if len(records) == 0:
        msg = f"│ Found no patient with id: `{patient_id}`."
        app.logger.error(msg)
        raise NotFound(msg)
    elif len(records) > 1:
        msg = f"│ Found {len(records)} patients with id: `{patient_id}`, but there can be only one."
        app.logger.error(msg)
        raise NotFound(msg)
    else:
        app.logger.error("│ Found a patient")
        r = records[0]
        rp = r["p"]
        patientDTO = {}
        for key,val in rp._properties.items():
            if key in fields(PatientDTO):
                patientDTO[key] = cast(PatientDTO,key,val)
        app.logger.debug("└OK")
        return flask.jsonify(patientDTO)


@app.route("/api/clinical-overview/data")
def patients():
    """all patients at once"""
    app.logger.debug(f"Asking for {patients.__doc__}...")
    records = cypher(
        "MATCH (p:Patient)"  \
        " RETURN ALL *")
    data = []
    app.logger.debug(f"│ {len(records)} records")
    for r in records:
        patient = r["p"]
        patientDTO = {}
        for key,val in patient._properties.items():
            if key in fields(PatientDTO):
                patientDTO[key] = cast(PatientDTO,key,val)
        data.append({
            "id": patient["id"],
            "DTO": patientDTO
        })
    app.logger.debug("└OK")
    return flask.jsonify(data)


@app.route("/api/genomic-overview/data/<patient_id>")
def genomic(patient_id):
    """genomic data of one patient"""
    app.logger.debug(f"Asking for {genomic.__doc__}...")
    data = {}

    samples = {
        "name": "unknown",
        "row": [],
    }
    records = cypher(
        f"MATCH (p:Patient)-[pcs]->(s:Sample) "
        f"WHERE p.id = '{patient_id}:patient' "
        f"RETURN s ;"
    )
    samples = {
        "name": "Unknown",
        "row": []
    }
    for r in records:
        sample = r["s"]
        app.logger.debug(sample)
        sampleInfo = {}
        for key,val in sample._properties.items():
            if key in fields(SampleInfo):
                sampleInfo[key] = cast(sampleInfo,key,val)
                app.logger.debug(sampleInfo)
        samples["row"].append( sampleInfo )

    app.logger.debug(f"│ {len(samples['row'])} samples")
    app.logger.debug("└OK")
    return flask.jsonify(samples)


if __name__ == "__main__":
    app.run()

