import wiring_rs
import json


def ldtab_2_ofn_demo():
    # ldtab contains columns 'subject','predicate','object'
    subject = "obo:OBI_0001636"
    predicate = "rdfs:subClassOf"
    object = {
        "owl:someValuesFrom": [{"datatype": "_IRI", "object": "obo:OBI_0500000"}],
        "rdf:type": [{"datatype": "_IRI", "object": "owl:Restriction"}],
        "owl:onProperty": [{"datatype": "_IRI", "object": "obo:BFO_0000050"}],
    }
    # NB: the converstion to JSON is not necessary when working with an LDTab table
    object_string = json.dumps(object)
    print("======")
    print("DEMO: LDTab to OFN-S expression")
    print("-------------------------------")
    print("Input: ")
    print("")
    print("Subject: " + subject)
    print("Predicate: " + predicate)
    print("Object: " + str(object))
    print("")
    print("Output: ")
    print(wiring_rs.ldtab_2_ofn(subject, predicate, object_string))
    print("======")


def thick_2_ofn_demo():
    triple = {
        "subject": "obo:OBI_0001636",
        "predicate": "rdfs:subClassOf",
        "object": {
            "owl:someValuesFrom": [{"object": "obo:OBI_0500000"}],
            "rdf:type": [{"object": "owl:Restriction"}],
            "owl:onProperty": [{"object": "obo:BFO_0000050"}],
        },
    }
    triple_string = json.dumps(triple)
    print("======")
    print("DEMO: Thick to OFN-S expression")
    print("-------------------------------")
    print("Input: ")
    print(triple_string)
    print("Output: ")
    print(wiring_rs.thick_2_ofn(triple_string))
    print("======")


def typing_demo():

    # The handling of quotes is somewhat ugly.
    # Wiring uses JSON under the hood.
    # So, '"s"' is a string containing a JSON string
    m = {
        "obo:CHEBI_33262": {"owl:Class"},
        "obo:RO_0000052": {"owl:ObjectProperty"},
    }

    # m = wiring_rs.extract_types(
    #     "path/to/rdf-graph"
    # )

    ofn = (
        '["SubClassOf","obo:OBI_2100378",'
        '["ObjectIntersectionOf",'
        '["SomeValuesFrom",'  # not typed
        '"obo:BFO_0000055",'
        '["ObjectIntersectionOf","obo:OBI_0000275",'
        '["SomeValuesFrom","obo:RO_0000052","obo:CHEBI_33262"]]],'  # not typed
        '["SomeValuesFrom","obo:OBI_0000293","obo:CHEBI_33262"]]]'  # not typed
    )

    print("======")
    print("DEMO: Typing of OFN-S expression")
    print("--------------------------------")
    print("Input: ")
    print(ofn)
    print("Output: ")
    print(
        wiring_rs.ofn_typing(
            ofn,
            m,
        )
    )
    print("======")


# def extract_labeling():
#    print(
#        wiring_rs.extract_labels(
#            "path/to/rdf-graph"
#        )
#    )


def labeling_demo():
    m = {
        "obo:CHEBI_33262": "test_label",
        "obo:RO_0000052": "test_label_2",
    }

    # get label information from file
    # m = wiring_rs.extract_labels(
    #     "path/to/rdf-graph"
    # )
    ofn = (
        '["SubClassOf","obo:OBI_2100378",'
        '["ObjectIntersectionOf",'
        '["ObjectSomeValuesFrom",'
        '"obo:BFO_0000055",'
        '["ObjectIntersectionOf","obo:OBI_0000275",'
        '["ObjectSomeValuesFrom","obo:RO_0000052","obo:CHEBI_33262"]]],'
        '["ObjectSomeValuesFrom","obo:OBI_0000293","obo:CHEBI_33262"]]]'
    )
    print("======")
    print("DEMO: Labeling of OFN-S expression")
    print("----------------------------------")
    print("Input: ")
    print(ofn)
    print("Output: ")
    print(
        wiring_rs.ofn_labeling(
            ofn,
            m,
        )
    )
    print("======")


def manchester_demo():
    ofn = (
        '["SubClassOf","obo:OBI_2100378",'
        '["ObjectIntersectionOf",'
        '["ObjectSomeValuesFrom",'
        '"obo:BFO_0000055",'
        '["ObjectIntersectionOf","obo:OBI_0000275",'
        '["ObjectSomeValuesFrom","obo:RO_0000052","obo:CHEBI_33262"]]],'
        '["ObjectSomeValuesFrom","obo:OBI_0000293","obo:CHEBI_33262"]]]'
    )

    print("======")
    print("DEMO: OFN-S expression to Manchester")
    print("------------------------------------")
    print("Input: ")
    print(ofn)
    print("Output: ")
    print(wiring_rs.ofn_2_man(ofn))

    # m = wiring_rs.extract_labels(
    #    "path/to/rdf-graph"
    # )

    m = {
        "obo:CHEBI_33262": "test_label",
        "obo:RO_0000052": "test_label_2",
    }

    labeled = wiring_rs.ofn_labeling(ofn, m)
    print(wiring_rs.ofn_2_man(labeled))
    print("======")


def ofn_2_thick_demo():
    ofn = (
        '["SubClassOf","obo:OBI_2100378",'
        '["ObjectIntersectionOf",'
        '["ObjectSomeValuesFrom",'
        '"obo:BFO_0000055",'
        '["ObjectIntersectionOf","obo:OBI_0000275",'
        '["ObjectSomeValuesFrom","obo:RO_0000052","obo:CHEBI_33262"]]],'
        '["ObjectSomeValuesFrom","obo:OBI_0000293","obo:CHEBI_33262"]]]'
    )

    print("======")
    print("DEMO: OFN-S expression to Thick Triple")
    print("--------------------------------------")
    print("Input: ")
    print(ofn)
    print("Output: ")
    print(wiring_rs.ofn_2_thick(ofn))
    print("======")


def ofn_2_ldtab_demo():
    ofn = (
        '["SubClassOf","obo:OBI_2100378",'
        '["ObjectIntersectionOf",'
        '["ObjectSomeValuesFrom",'
        '"obo:BFO_0000055",'
        '["ObjectIntersectionOf","obo:OBI_0000275",'
        '["ObjectSomeValuesFrom","obo:RO_0000052","obo:CHEBI_33262"]]],'
        '["ObjectSomeValuesFrom","obo:OBI_0000293","obo:CHEBI_33262"]]]'
    )

    print("======")
    print("DEMO: OFN-S expression to LDTab JSON")
    print("--------------------------------------")
    print("Input: ")
    print(ofn)
    print("Output: ")
    print(wiring_rs.ofn_2_ldtab(ofn))
    print("======")


if __name__ == "__main__":
    thick_2_ofn_demo()
    print("")
    typing_demo()
    print("")
    labeling_demo()
    print("")
    manchester_demo()
    print("")
    ofn_2_thick_demo()
    print("")
    ldtab_2_ofn_demo()
    print("")
    ofn_2_ldtab_demo()
