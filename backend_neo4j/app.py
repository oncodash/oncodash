import flask
import neo4j
import logging

app = flask.Flask(__name__)

neo4j_uri = "neo4j://localhost:7687"

with open("neo4j.pass") as fd:
    neo4j_passwd = fd.readline().strip()
neo4j_auth = ("neo4j", neo4j_passwd)

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


@app.route("/patients")
def patients():
    with neo4j.GraphDatabase.driver(neo4j_uri, auth=neo4j_auth) as db:
        records, _, _ = db.execute_query(
            "MATCH (p:Patient) RETURN ALL * LIMIT 5",
            name="neo4j", database_ = "oncodash")
    patients = []
    app.logger.debug(f"{len(records)} records")
    for r in records:
        app.logger.debug(r)
        rp = r["p"]
        patient = {}
        for key,val in rp._properties.items():
            patient[key] = val
        patients.append(patient)
    return flask.jsonify(patients)


if __name__ == "__main__":
    app.run()

