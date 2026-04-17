#!/usr/bin/env bash

echo "Starting Neo4j database..." >&2

case "$(uname)" in
    FreeBSD)   OS=FreeBSD ;;
    DragonFly) OS=FreeBSD ;;
    OpenBSD)   OS=OpenBSD ;;
    Darwin)    OS=Darwin  ;;
    SunOS)     OS=SunOS   ;;
    *)         OS=Linux   ;;
esac

echo "Running under $OS" >&2
if [[ "$OS" == "Linux" ]] ; then
    # When using Neo4j installed on system (like Ubuntu's packaged version),
    # the current directory must be writable by user "neo4j",
    # and all parent directories must be executable by "other".
    # Every interaction with the database must be done by user "neo4j",
    # and the import will try to write reports in the current directory.
    NEO_USER="sudo -u neo4j"
    # export JAVA_HOME="/usr/lib/jvm/java-21-openjdk-amd64"
else
    NEO_USER=""
fi

${NEO_USER} neo4j-admin server status

if [[ $? ]] ; then
    echo "Access Neo4j browser at: http://localhost:7474" >&2
else
    neo_version=$(neo4j-admin --version | cut -d. -f 1)
    if [[ "$neo_version" -eq 4 ]]; then
        server="${NEO_USER} neo4j"
    else
        server="${NEO_USER} neo4j-admin server"
    fi
    $server start
fi

# echo "Send a test query..." >&2
# ${NEO_USER} cypher-shell --username neo4j --database oncodash --password "$(cat neo4j.pass)" "MATCH (p:Patient) RETURN p LIMIT 5;"


echo "Starting Flask API..." >&2

echo "###############################################" >&2
echo "Neo4j  browser: http://localhost:7474/browser/" >&2
echo "Flask REST API: http://127.0.0.1:5000/" >&2
echo "###############################################" >&2

export FLASK_APP="app.py"
uv run flask --app app run --debug

