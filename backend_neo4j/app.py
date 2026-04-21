import os
import re
import sys
import json
import toml
import neo4j
import flask
import flask_cors
import logging
from markupsafe import escape
from werkzeug.exceptions import HTTPException, NotFound

import oncodashapi

app = flask.Flask(__name__)
flask_cors.CORS(app)

if 'ONCODASH_NEO4J_HOST' in os.environ:
    neo4j_host = os.environ['ONCODASH_NEO4J_HOST']
else:
    neo4j_host = "neo4j://localhost:7687"

config = {
    "neo4j": {
        "uri": neo4j_host,
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

api = oncodashapi.API(app, config)

@app.before_request
def handle_preflight():
    if flask.request.method == "OPTIONS":
        res = flask.Response()
        res.headers['X-Content-Type-Options'] = '*'
        return res


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
    app.logger.debug(f"ERROR [{e.code}] {e.name}:")
    return response


@app.route("/")
def root():
    """Map of this website."""
    app.logger.debug(f"Asking for {root.__doc__}...")
    html = "<ul>"
    for url,doc in api.endpoints().items():
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
    links = api.endpoints()
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


@app.route("/api/clinical-overview/data/")
def patients():
    """all patients at once"""
    app.logger.debug(f"Asking for {patients.__doc__}...")
    records = api.cypher(
        "MATCH (p:Patient)"  \
        " RETURN ALL *")
    data = []
    app.logger.debug(f"│ {len(records)} records")
    for r in records:
        patient = r["p"]

        patientDTO = api.cast_as(patient, oncodashapi.PatientDTO)
        patientDTO["patient_id"] = patient["id"]
        patientDTO = api.calc_patient_details(patientDTO)
        data.append(patientDTO)

    app.logger.debug("└OK")
    return flask.jsonify(data)


@app.route("/api/clinical-overview/data/<patient_id>/")
def patient(patient_id):
    """data about a specific patient"""
    app.logger.debug(f"Asking for {patient.__doc__}: `{patient_id}`...")

    records = api.cypher(
        f"MATCH (p:Patient)"             \
        f" WHERE p.id = '{patient_id}' "  \
         " RETURN ALL *")
    if len(records) == 0:
        msg = f"│ Found no patient with id: `{patient_id}`."
        app.logger.error(msg)
        flask.abort(422, description = msg)
    elif len(records) > 1:
        msg = f"│ Found {len(records)} patients with id: `{patient_id}`, but there can be only one."
        app.logger.error(msg)
        flask.abort(422, description = msg)
    else:
        app.logger.debug("│ Found a patient")
        r = records[0]
        pat = r["p"]

        patientDTO = api.cast_as(pat, oncodashapi.PatientDTO)
        patientDTO["patient_id"] = pat["id"]
        patientDTO = api.calc_patient_details(patientDTO)
        app.logger.debug("└OK")

        return flask.jsonify(patientDTO)


@app.route("/api/genomic-overview/data/<patient_id>/")
def genomic(patient_id):
    """genomic data of one patient"""
    app.logger.debug(f"Asking for {genomic.__doc__}: {patient_id}...")

    # Actionable aberrations
    actionable_genome, actionable_samples, nb_actionable_alterations, actionable_ordered = \
        api.actionables(patient_id)
    app.logger.debug(f"│ Found {nb_actionable_alterations} alterations on {len(actionable_genome.keys())} genes in {len(actionable_samples)} samples.")

    other_genome, other_samples, nb_other_alterations, other_ordered = \
        api.others(patient_id)
    app.logger.debug(f"│ Found {nb_other_alterations} alterations on {len(other_genome.keys())} genes in {len(other_samples)} samples.")

    seen_samples = []
    for s in actionable_samples + other_samples: #+ relevant_samples:
        if s not in seen_samples:
            seen_samples.append(s)

    samples = {
        "name": f"{patient_id}",
        "row": seen_samples,
    }

    genomic_sub_data = {
        "actionable_aberrations": [nb_actionable_alterations, 'ACTIONABLE ABERRATIONS'],
        "other_variants": [nb_other_alterations, 'OTHER VARIANTS'],
    }

    genomic_data = {
        "genomic" : genomic_sub_data,
        "actionable_aberrations": actionable_genome,
        "other_variants": other_genome,
        "order": {
            "actionable_aberrations": actionable_ordered,
            "other_variants": other_ordered,
        },
        "samples_info": samples,
    }

    app.logger.debug("└OK")
    return flask.jsonify(genomic_data)


if __name__ == "__main__":
    app.run()

