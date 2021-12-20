import itertools

import pyAgrum as gm
import pyAgrum.lib.image as gimg

# Example data structure
oncausal = {
    "nodes" : {
        "samples"    : ['Ascites', 'Peritoneum', 'Tuba 1', 'Mesenterium 1'],
        "lines"      : ['KMM-1', '293A', 'A549'],
        "alterations": ['FANCA del', 'CDKN1B del'],
        "cancers"    : ['High-grade', 'Low-grade'],
        "drugs"      : ['PARP', 'CDK2/4', 'CDK4/6'],
        "effects"    : [
                'Platelet drop',
                'Blood drop',
                'Vomiting',
                'Stomach',
                'Nausea',
                'Fatigue',
            ],
    },
    "links" : {
        "lines" : [
            { "source": 'Ascites',       "target": 'KMM-1', "certainty": 0.5, "strength": 0.5 },
            { "source": 'Peritoneum',    "target": '293A',  "certainty": 0.8, "strength": 0.2 },
            { "source": 'Tuba 1',        "target": 'KMM-1', "certainty": 0.1, "strength": 0.1 },
            { "source": 'Mesenterium 1', "target": '293A',  "certainty": 0.9, "strength": 0.1 },
            { "source": 'Ascites',       "target": 'A549',  "certainty": 0.5, "strength": 0.5 },
            { "source": 'Tuba 1',        "target": 'A549',  "certainty": 0.5, "strength": 0.5 },
            { "source": 'Mesenterium 1', "target": 'KMM-1', "certainty": 0.1, "strength": 0.9 },
        ],
        "alterations" : [
            { "source": 'KMM-1', "target": 'FANCA del',  "certainty": 0.8, "strength": 0.1 },
            { "source": 'KMM-1', "target": 'CDKN1B del', "certainty": 0.4, "strength": 0.3 },
            { "source": '293A',  "target": 'CDKN1B del', "certainty": 0.8, "strength": 1.0 },
            { "source": 'A549',  "target": 'FANCA del',  "certainty": 0.2, "strength": 0.9 },
        ],
        "cancers": [
            { "source": 'FANCA del',  "target": 'High-grade', "certainty": 1.0, "strength": 0.9 },
            { "source": 'FANCA del',  "target": 'Low-grade',  "certainty": 0.1, "strength": 0.5 },
            { "source": 'CDKN1B del', "target": 'High-grade', "certainty": 0.3, "strength": 0.3 },
        ],
        "drugs" : [
            { "source": 'High-grade', "target": 'PARP',   "certainty": 0.8, "strength": 0.2 },
            { "source": 'Low-grade',  "target": 'PARP',   "certainty": 0.8, "strength": 0.2 },
            { "source": 'High-grade', "target": 'CDK2/4', "certainty": 0.2, "strength": 0.1 },
            { "source": 'Low-grade',  "target": 'CDK2/4', "certainty": 0.4, "strength": 0.8 },
            { "source": 'High-grade', "target": 'CDK4/6', "certainty": 0.8, "strength": 0.2 },
            { "source": 'Low-grade',  "target": 'CDK4/6', "certainty": 0.9, "strength": 0.6 },
        ],
        "effects" : [
            { "source": 'PARP',   "target": 'Platelet drop', "certainty": 0.2, "strength": 0.3  },
            { "source": 'CDK2/4', "target": 'Platelet drop', "certainty": 0.1, "strength": 0.9  },
            { "source": 'CDK4/6', "target": 'Platelet drop', "certainty": 0.8, "strength": 0.2  },
            { "source": 'PARP',   "target": 'Blood drop',    "certainty": 0.2, "strength": 0.4  },
            { "source": 'CDK2/4', "target": 'Blood drop',    "certainty": 0.1, "strength": 0.1  },
            { "source": 'CDK4/6', "target": 'Blood drop',    "certainty": 0.8, "strength": 0.3  },
            { "source": 'PARP',   "target": 'Vomiting',      "certainty": 0.4, "strength": 0.7  },
            { "source": 'CDK2/4', "target": 'Vomiting',      "certainty": 0.5, "strength": 0.6  },
            { "source": 'CDK4/6', "target": 'Vomiting',      "certainty": 0.1, "strength": 0.8  },
            { "source": 'PARP',   "target": 'Stomach',       "certainty": 0.7, "strength": 0.2  },
            { "source": 'CDK2/4', "target": 'Stomach',       "certainty": 0.4, "strength": 0.1  },
            { "source": 'CDK4/6', "target": 'Stomach',       "certainty": 0.3, "strength": 0.05 },
            { "source": 'PARP',   "target": 'Nausea',        "certainty": 0.9, "strength": 0.95 },
            { "source": 'CDK2/4', "target": 'Nausea',        "certainty": 0.1, "strength": 0.8  },
            { "source": 'CDK4/6', "target": 'Nausea',        "certainty": 0.2, "strength": 0.2  },
            { "source": 'PARP',   "target": 'Fatigue',       "certainty": 0.1, "strength": 0.45 },
            { "source": 'CDK2/4', "target": 'Fatigue',       "certainty": 0.9, "strength": 0.2  },
            { "source": 'CDK4/6', "target": 'Fatigue',       "certainty": 0.9, "strength": 0.1  },
        ],
    }
}


bn = gm.BayesNet("Oncausal_min")

print("Create nodes")
nodes = {}
for column in oncausal["nodes"]:
    print("\t",column, end=" : ")
    for label in oncausal["nodes"][column]:
        # Binary variable (label, description, cardinality)
        node = bn.add( gm.LabelizedVariable( label, "{}:{}".format(column[0], 2) ) )
        nodes[label] = node
        print(label,end=", ")
    print()

print("Create arcs")
for column in oncausal["links"]:
    print("\t>",column,end=" : ")
    for link in oncausal["links"][column]:
        print(link["source"],">",link["target"], end=", ")
        bn.addArc(nodes[link["source"]],nodes[link["target"]])
    print()

print("Create CPTs")
for column in oncausal["nodes"]:
    print("\t>",column, end=" : ")
    for label in oncausal["nodes"][column]:
        # Conditional Probability Table
        if column in oncausal["links"]:
            incomings = [ l for l in oncausal["links"][column] if l["target"] == label ]
            print("> {} ({})".format(label,len(incomings)))

            print("Links:")
            links = {}
            for i in incomings:
                links[i["source"]] = { "strength":i["strength"], "certainty" : i["certainty"] }
            print("\t",links)

            print("CPT (with P[False]<1):")
            # Cartesian product of all (links:booleans):
            cp = list(itertools.product( *[ itertools.product([i["source"]],[0,1]) for i in incomings ] ))
            # print(cp)
            for prod in cp:

                def non_zeros(p):
                    r = []
                    for i in p:
                        if i[1] == 1:
                            r.append(i[0])
                    return r

                def minmax(p):
                    return  max(0, min(1, p))

                def probability(strength, certainty):
                    return 1 - minmax( strength - (1-certainty)/2 )
                    
                sources = non_zeros(prod)
                proba = 0
                if len(sources) > 0:
                    p = probability(links[sources[0]]["strength"], links[sources[0]]["certainty"])
                    for i in range(1,len(sources)):
                        p *= probability(links[sources[0]]["strength"], links[sources[0]]["certainty"])

                    proba = 1-p
                if 1-proba < 1.0:
                    print("\t",dict(prod),"=","[ False=",1-proba,", True=",proba,"]")
                    
                node = nodes[label]
                bn.cpt(node)[dict(prod)] = [1-proba,proba]
                    
            # for i in incomings:
            #     print("\t\t",i["source"],">",i["target"])
            #     prev = nodes[i["source"]]
            #     node = nodes[i["target"]]
                
            #     # Probabilities of being [False, True] if previous node is False:
            #     bn.cpt(node)[{prev:0}] = [0,0]
            #     # Probabilities of being [False, True] if previous node is True:
            #     p = max(0, min(1, i["strength"] - (1 - i["certainty"]/2)))
            #     bn.cpt(node)[{prev:1}] = [1-p, p]
    print()

print(bn)


print("Export diagram in demo.png")
def nodevalue(n):
    return 0.5
def arcvalue(a):
    return (10-a[0])*a[1]
def arcvalue2(a):
    return (a[0]+a[1]+5)/22

gimg.export(bn, "demo.png", size="2000" ,
           nodeColor={n:nodevalue(n) for n in bn.names()},
           arcWidth={a:arcvalue(a) for a in bn.arcs()},
           arcColor={a:arcvalue2(a) for a in bn.arcs()})

what = "Low-grade"
observed = ["Ascites","Tuba 1","Mesenterium 1","Peritoneum"]
print("Minimal conditioning set of:", what, observed)
# For a variable and a list of variables, one can find the sublist that effectively impacts the variable if the list of variables was observed.
print("\t", [bn.variable(i).name() for i in bn.minimalCondSet(what,observed)])

print("Independency tests:")
def test_indep(bn,x,y,knowing):
    res="" if bn.isIndependent(x,y,knowing) else " NOT"
    giv="." if len(knowing)==0 else f" given {knowing}."
    print(f"\t{x} and {y} are{res} independent{giv}")

test_indep(bn, "High-grade", "Low-grade", ["Peritoneum"])
test_indep(bn, "High-grade", "Low-grade", ["Ascites"])
test_indep(bn, "Tuba 1", "Ascites", ["293A"])

what = "Low-grade"
print("Markov blanket of:", what)
# The Markov blanket of a node X is the set of nodes MB(X) such that X is independent from the rest of the nodes given MB(X).
mb = gm.MarkovBlanket(bn, what)
print("\t", mb.toDot())

# computes P(target|evidence) but reduces as much as possible the set of needed evidence for the result
ie=gm.LazyPropagation(bn)
ie.evidenceImpact("Nausea",["Peritoneum"])

