import os
import re
import sys
import json
import toml
import neo4j
import flask
import flask_cors
import logging

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


    def genome_of(self, patient_id, records):

        alterations = []
        genome = {}

        self.app.logger.debug(f"Found {len(records)} records")
        for r in records:
            sample = r["s"]
            sampleInfo = self.cast_as(sample, SampleInfo)
            # sample_info_list["row"].append( sampleInfo )

            sample_carries_variant = r["scv"]

            alterationData = {}
            alterationData["name"] = "FIXME"
            alterationData["description"] = "FIXME"
            alterationData["reported_sensitivity"] = "FIXME"

            alterationSampleData = self.cast_as(samples_carries_variant, AlterationSampleDataCNV)
            # TODO SNP

            alterationSampleData["sample"] = sample["id"]
            if "row" not in alterationData.keys():
                alterationData["row"] = []
            alterationData["row"].append(alterationSampleData)
            alterations.append(alterationData)

            gene = r["g"]._properties["gene_symbol"]
            if gene not in genome.keys():
                gene_data = {
                    "description": "FIXME",
                    "alterations": [],
                }
                genome[gene] = gene_data

            genome[gene]["alterations"] += alterations

        self.app.logger.debug(f"│ {len(sample_info_list['row'])} sample_info_list")
        self.app.logger.debug(f"│ {len(alterations)} alterations")

        return genome


