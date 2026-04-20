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
        app.logger.debug("└OK")

        return flask.jsonify(patientDTO)


@app.route("/api/genomic-overview/data/<patient_id>/")
def genomic(patient_id):
    """genomic data of one patient"""
    app.logger.debug(f"Asking for {genomic.__doc__}: {patient_id}...")
    
    # # if ":patient" not in patient_id:
    # #     patient_id = f"{patient_id}:patient"

    # # Actionable alterations
    # actionable_alteration_query = \
    #     f"MATCH path = (start:Patient)-[*1]->()-[scv:SampleCarriesVariant]->(sv:SequenceVariant)-[]->(gs:GeneStatus)-[vbt:VariantBiomarkerForTreatment]->(end:Treatment) "\
    #     f"WHERE (start.id = '{patient_id}')"\
    #     f"AND (vbt.fda_level IN ['1.0','2.0']) "\
    #     f"RETURN DISTINCT scv, sv "

    # # Putative relevant alterations
    # putative_alteration_query = \
    #     f"MATCH path = (start:Patient)-[*1]->()-[scv:SampleCarriesVariant]->(sv:SequenceVariant)-[]->(gs:GeneStatus)-[vbt:VariantBiomarkerForTreatment]->(end:Treatment) "\
    #     f"WHERE (start.id = '{patient_id}:patient') "\
    #     f"AND (vbt.fda_level IN ['3.0','4.0']) "\
    #     f"RETURN DISTINCT scv, sv "


    # // Actionable alterations lists
    # MATCH path = (start:Patient)-[*1]->(s:Sample)-[scv:SampleCarriesVariant]->(sv:SequenceVariant)-[]->(gs:GeneStatus)-[vbt:VariantBiomarkerForTreatment]->(end:Treatment)
    # WHERE (start.id = '{patient_id}:patient')
    # AND (vbt.fda_level IN ['1.0','2.0'])
    # RETURN DISTINCT s, scv, sv

    # // Putative relevant alterations lists
    # MATCH path = (start:Patient)-[*1]->(s:Sample)-[scv:SampleCarriesVariant]->(sv:SequenceVariant)-[]->(gs:GeneStatus)-[vbt:VariantBiomarkerForTreatment]->(end:Treatment)
    # WHERE (start.id = '{patient_id}:patient')
    # AND (vbt.fda_level IN ['1.0','2.0'])
    # RETURN DISTINCT s, scv, sv

    # // Other variants lists
    # MATCH path = (start:Patient)-[*1]->(s:Sample)-[scv:SampleCarriesVariant]->(sv:SequenceVariant)-[]->(end:GeneStatus)
    # WHERE not (end)--(:Treatment)
    # AND (start.id = '{patient_id}:patient')
    # RETURN DISTINCT s, scv, sv


        # f"MATCH (p:Patient)"
        #     "-[pcs]->(s:Sample)"
        #     "-[scv:SampleCarriesVariant]->(sv:SequenceVariant)"
        #     "-[]->(gs:GeneStatus)"
        #     "-[:GeneStatusAffectsGene]->(g:Gene)"
        #     "-[vbt:VariantBiomarkerForTreatment]->(end:Treatment)"
        # f" WHERE (p.id = '{patient_id}')"
        #  " AND (vbt.fda_level IN ['1.0','2.0'])"
        #  " RETURN DISTINCT s, scv, sv, g ;"
        #  
    # Actionable aberrations
    # 
    actionable_genome, actionable_samples, nb_actionable_alterations = \
        api.actionables(patient_id)
    app.logger.debug(f"│ Found {nb_actionable_alterations} alterations on {len(actionable_genome.keys())} genes in {len(actionable_samples)} samples.")

    # relevant_genome, relevant_samples, nb_relevant_alterations = \
    #     api.relevants(patient_id)
    # app.logger.debug(f"│ Found {nb_relevant_alterations} alterations on {len(relevant_genome.keys())} genes in {len(relevant_samples)} samples.")

    other_genome, other_samples, nb_other_alterations = \
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
        # "putative_functionally_relevant_variants": [nb_relevant_alterations, 'PUTATIVE FUNCTIONALLY RELEVANT'] ,
        "other_variants": [nb_other_alterations, 'OTHER VARIANTS'],
    }

    genomic_data = {
        "genomic" : genomic_sub_data,
        "actionable_aberrations": actionable_genome,
        # "putative_functionally_relevant_variants": relevant_genome,
        "other_variants": other_genome,
        "samples_info": samples,
    }

    # with open("genomic_data.json", 'w') as fd:
    #     json.dump(genomic_data, fd)
    # response = app.response_class(
    #     response=json.dumps(genomic_data),
    #     mimetype='application/json'
    # )
    # return response

    app.logger.debug("└OK")
    return flask.jsonify(genomic_data)


if __name__ == "__main__":
    app.run()

