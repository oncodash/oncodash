
import flask

app = flask.Flask(__name__)

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


if __name__ == "__main__":
    app.run()

