<a  href="https://oncodash.github.io/oncodash/"><img  src="https://github.com/oncodash/oncodash/actions/workflows/build-docs.yml/badge.svg"  alt="Build Status"/></a></td>

# Oncodash

Oncodash is a decision support system that help tumour boards to come up with to the best decisions for their patients.
Oncodash is currently developed within the DECIDER project and targets high-grade serous ovarian cancer.
For more information, see the [public website](https://oncodash.github.io/oncodash/).


# Software Architecture

Oncodash is a web application:

- Its frontend is built with the [Vue.js](https://vuejs.org/) framework.
- The frontend requests data from a REST backend built with [Flask](https://flask.palletsprojects.com/en/stable/).
- The backend queries data from a Semantic Knowledge Graph (reproducibly)
  built with the [OncodashKB](https://github.com/oncodash/oncodashkb) project,
  and running on the [Neo4j](https://neo4j.com/) graph database engine.

Oncodash is a proof of concept, without built-in security.
Do not use it in production with sensitive data!


# More information

You can find more information in the following files:

- [how to build, run and install](https://github.com/oncodash/oncodash/blob/main/INSTALL.md)
- [how to contribute](https://github.com/oncodash/oncodash/blob/main/CONTRIBUTING.md)
