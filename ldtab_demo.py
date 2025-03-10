import wiring_rs
import sqlite3
import sys


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_types(connection, subject):
    cur = connection.cursor()
    query = "SELECT * FROM statement WHERE subject = ? AND predicate = 'rdf:type'"
    types = set()
    for row in cur.execute(query, (subject,)):
        types.add(row["object"])

    return types


def get_labels(connection, subject):
    cur = connection.cursor()
    label = set()
    query = "SELECT * FROM statement WHERE subject = ? AND predicate = 'rdfs:label'"
    for row in cur.execute(query, (subject,)):
        label.add(row["object"])

    return label


def get_types_of_signature(connection, ofn):

    type_map = {}
    signature = wiring_rs.get_signature(ofn)
    for s in signature:
        types = get_types(connection, s)
        if types:
            type_map[s] = types

    return type_map


def get_labels_of_signature(connection, ofn):
    label_map = {}
    signature = wiring_rs.get_signature(ofn)
    for s in signature:
        labels = get_labels(connection, s)
        if labels:
            # just use one label (we assume labels are unique)
            label_map[s] = labels.pop()

    return label_map


def get_statements(connection, table, subject):
    connection.row_factory = dict_factory
    cur = connection.cursor()
    query = f"SELECT * FROM {table} WHERE subject = ?"
    return cur.execute(query, (subject,))



def object2rdfa(connection, table, json):
    # 1. convert json to OFN (wiring.rs)
    ofn = wiring_rs.object_2_ofn(json)
    # 2. get types from database (wiring.py)
    types = get_types_of_signature(connection, ofn)
    # 3. get labels from database (wiring.py)
    labels = get_labels_of_signature(connection, ofn)
    # 4. typing (wiring.rs)
    typed = wiring_rs.ofn_typing(ofn, types)

    # NO labelling
    # 5. labelling (wiring.rs)
    # labeled = wiring_rs.ofn_labeling(typed, labels)

    # NB: RDFa requires information about IRIs and their labels.
    # So, we need to pass typed OFN S-expressions AND labels separately.
    # 6. RDFa (wiring.rs)
    rdfa = wiring_rs.object_2_rdfa(typed, labels)

    return rdfa


def object2omn(connection, table, json):
    # 1. convert json to OFN (wiring.rs)
    ofn = wiring_rs.object_2_ofn(json)
    # 2. get types from database (wiring.py)
    types = get_types_of_signature(connection, ofn)
    # 3. get labels from database (wiring.py)
    labels = get_labels_of_signature(connection, ofn)
    # 4. typing (wiring.rs)
    typed = wiring_rs.ofn_typing(ofn, types)
    # 5. labelling (wiring.rs)
    labeled = wiring_rs.ofn_labeling(typed, labels)
    # 6. Manchester string (wiring.rs)
    man = wiring_rs.ofn_2_man(labeled)
    return man


# this results in duplicate database queries
# in the case different JSON objects contain the same named entities.
# This is a common case. So, we should avoid this.
# def objects2omn(connection, table, jsons):
#    mans = []
#    for json in jsons:
#        mans.append(object2omn(json))
#    return mans


# TODO: use type hints?
# from typing import List, Set, Dict, Tuple, Optional
# -> there are differences between type hints in Python versions 3.8 and 3.9
# -> ignore for now
def objects2omn(connection, table, jsons):
    ofns = []
    # 1. first convert everything to ofn
    for json in jsons:
        ofns.append(wiring_rs.object_2_ofn(json))

    # 2. get signature for all terms
    signature = set()
    for ofn in ofns:
        signature = signature.union(wiring_rs.get_signature(ofn))

    # 3. get typing information for signature
    type_map = {}
    for s in signature:
        types = get_types(connection, s)
        if types:
            type_map[s] = types

    # 4. get labelling information for signature
    label_map = {}
    for s in signature:
        labels = get_labels(connection, s)
        if labels:
            # just use one label (we assume labels are unique)
            label_map[s] = labels.pop()

    # 5. typing
    typed = []
    for ofn in ofns:
        typed.append(wiring_rs.ofn_typing(ofn, type_map))

    # 6. labelling (requires correctly typed OFN S-expressions)
    labelled = []
    for ofn in typed:
        labelled.append(wiring_rs.ofn_labeling(ofn, label_map))

    # 7. Manchester
    man = []
    for ofn in labelled:
        man.append(wiring_rs.ofn_2_man(ofn))

    return man


def run_demo_objects2omn(database, subject):
    con = sqlite3.connect(database, check_same_thread=False)

    # create list of JSON objects
    jsons = []
    for row in get_statements(con, "statement", subject):
        jsons.append(row["object"])

    # create Manchester stings
    mans = objects2omn(con, "statement", jsons)

    # print them side by side
    for i in range(len(jsons)):
        print("===")
        print(jsons[i])
        print(mans[i])
        print("===")


def run_demo_object2omn(database, subject):
    con = sqlite3.connect(database, check_same_thread=False)
    for row in get_statements(con, "statement", subject):
        print(object2omn(con, "statement", row["object"]))


def run_demo_object2rdfa(database, subject):
    con = sqlite3.connect(database, check_same_thread=False)
    for row in get_statements(con, "statement", subject):
        print("<====>")
        print("orig")
        print(row["object"])
        print("rdfa")
        print(object2rdfa(con, "statement", row["object"]))
        print("<====>")


def run_demo(database, subject):

    # connection to database
    con = sqlite3.connect(database, check_same_thread=False)

    # query for ThickTriples of the subject
    for row in get_statements(con, "statement", subject):

        # fetch data of a ThickTriple
        subject = row["subject"]
        predicate = row["predicate"]
        object = row["object"]

        # convert ThickTriple to an OFN S-expression
        # TODO provide support for datatypes
        ofn = wiring_rs.ldtab_2_ofn(subject, predicate, object)

        # fetch typing information relevant for the OFN S-expression
        types = get_types_of_signature(con, ofn)

        # fetch labelling information relevant for the OFN S-expression
        labels = get_labels_of_signature(con, ofn)

        # perform typing
        typed = wiring_rs.ofn_typing(ofn, types)

        # perform labelling (this requires a correctly typed OFN S-expression)
        labeled = wiring_rs.ofn_labeling(typed, labels)

        # convert to Manchester syntax
        man = wiring_rs.ofn_2_man(typed)
        lab_man = wiring_rs.ofn_2_man(labeled)

        print("======")
        print("ThickTriple: " + str(subject) + "," + str(predicate) + "," + str(object))
        print("Typed OFN: " + typed)
        print("Labelled OFN: " + labeled)
        print("Manchester: " + man)
        print("Lab Man: " + lab_man)
        print("======")


if __name__ == "__main__":

    # example call for OBI:
    # python ldtab_demo.py ldtab_obi.db obo:OBI_0002946

    database = sys.argv[1]
    subject = sys.argv[2]

    # run_demo(database, subject)
    # run_demo_object2omn(database, subject)
    run_demo_object2rdfa(database, subject)
    # run_demo_objects2omn(database, subject)
