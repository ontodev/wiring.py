import wiring_rs
import sqlite3
import sys


def get_types(connection, subject):
    cur = connection.cursor()
    query = (
        f"SELECT * FROM statement WHERE "
        f"subject='{subject}' AND "
        f"predicate='rdf:type'"
    )
    types = set()
    for row in cur.execute(query):
        types.add(row[5])

    return types


def get_labels(connection, subject):
    cur = connection.cursor()
    query = (
        f"SELECT * FROM statement WHERE "
        f"subject='{subject}' AND "
        f"predicate='rdfs:label'"
    )
    label = set()
    for row in cur.execute(query):
        label.add(row[5])

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


def get_statements(connection, subject):
    cur = connection.cursor()
    query = f"SELECT * FROM statement WHERE subject='{subject}'"
    return cur.execute(query)


def run_demo(database, subject):

    # connection to database
    con = sqlite3.connect(database, check_same_thread=False)

    # query for ThickTriples of the subject
    for row in get_statements(con, subject):

        # fetch data of a ThickTriple
        subject = row[3]
        predicate = row[4]
        object = row[5]

        # convert ThickTriple to an OFN S-expression
        ofn = wiring_rs.ldtab_2_ofn(subject, predicate, object)

        # fetch typing information relevant for the OFN S-exression
        types = get_types_of_signature(con, ofn)

        # fetch labelling information relevant for the OFN S-exression
        labels = get_labels_of_signature(con, ofn)

        # perform typing
        typed = wiring_rs.ofn_typing(ofn, types)

        # perform labelling (this requires a correctly typed OFN S-expression)
        labeled = wiring_rs.ofn_labeling(typed, labels)

        # convert to manchester syntax
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

    run_demo(database, subject)
