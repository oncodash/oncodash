import json
import toml
import flask
import neo4j
import logging
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


class schema:
    PatientDTO = {
        "age_at_diagnosis": int,
        "bmi_at_diagnosis": int,
        "brca_mutation_status": str,
        "chronic_illnesses_at_dg": bool,
        "chronic_illnesses_type": str,
        "clinical_trial": bool,
        "cohort_code": str,
        "current_treatment_phase": str,
        "days_from_beva_maintenance_end_to_progression": int,
        "days_to_death": int,
        "days_to_progression": int,
        "debulking_surgery_ids": bool,
        "drug_trial_name": str,
        "drug_trial_unblinded": bool,
        "event_series": str,
        "followup_time": int,
        "germline_pathogenic_variant": str,
        "height_at_diagnosis": int,
        "histology": str,
        "hr_signature_per_patient": str,
        "hr_signature_pretreatment_wgs": str,
        "hrd_myriad_status": str,
        "maintenance_therapy": str,
        "operation1_cancelled": bool,
        "operation2_cancelled": bool,
        "paired_fresh_samples_available": bool,
        "patient_id": int,
        "platinum_free_interval": int,
        "platinum_free_interval_at_update": int,
        "previous_cancer": bool,
        "previous_cancer_diagnosis": str,
        "primary_therapy_outcome": str,
        "progression": bool,
        "residual_tumor_ids": str,
        "residual_tumor_pds": str,
        "sequencing_available": bool,
        "stage": str,
        "survival": str,  # FIXME should be bool
        "time_series": str,
        "treatment_strategy": str,
        "weight_at_diagnosis": int,
        "wgs_available": bool,
    }


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
    return response


@app.route("/ping")
def ping():
    api_info = {
        "title": "Oncodash API",
        "summary": "Virtual Molecular Tumor Board Data access",
        "contact": {
            "name": "Johann Dreo",
            "email": "johann.dreo@pasteur.fr",
        },
        "version": "0.1.0",
    }
    return flask.jsonify({"info": api_info})


@app.route("/api/clinical-overview/data/<patient_id>")
def patient(patient_id):
    app.logger.debug(f"Asked for patient `{patient_id}`.")
    with neo4j.GraphDatabase.driver(config["neo4j"]["uri"], auth=config["neo4j"]["auth"]) as db:
        records, _, _ = db.execute_query(
            f"MATCH (p:Patient)"
            " WHERE p.id = '{patient_id}'"
            " RETURN ALL *",
            name="neo4j", database_ = "oncodash")
    patients = []
    app.logger.debug(f"{len(records)} patient")
    if len(records) == 0:
        msg = f"Found no patient with id: `{patient_id}`."
        raise NotFound(msg)
    elif len(records) > 1:
        msg = f"Found {len(records)} patients with id: `{patient_id}`, but there can be only one."
        raise NotFound(msg)
    else:
        for r in records:
            rp = r["p"]
            patient = {"id": rp["id"]}
            patientDTO = {}
            for key,val in rp._properties.items():
                if key in schema.PatientDTO:
                    patientDTO[key] = schema.PatientDTO[key](val)
            patientDTOs.append(patientDTO)
        return flask.jsonify(patientDTOs)


@app.route("/api/clinical-overview/data")
def patients():
    with neo4j.GraphDatabase.driver(config["neo4j"]["uri"], auth=config["neo4j"]["auth"]) as db:
        records, _, _ = db.execute_query(
            "MATCH (p:Patient)"
            " RETURN ALL *",
            name="neo4j", database_ = "oncodash")
    patients = []
    app.logger.debug(f"{len(records)} records")
    for r in records:
        rp = r["p"]
        patient = {"id": rp["id"]}
        patientDTO = {}
        for key,val in rp._properties.items():
            if key in schema.PatientDTO:
                patientDTO[key] = schema.PatientDTO[key](val)
        patientDTOs.append(patientDTO)
    return flask.jsonify(patientDTOs)


if __name__ == "__main__":
    app.run()

