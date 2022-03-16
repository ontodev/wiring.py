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
    query = (
        f"SELECT * FROM statement WHERE "
        f"subject='{subject}' AND "
        f"predicate='rdf:type'"
    )
    types = set()
    for row in cur.execute(query):
        types.add(row["object"])

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
    query = f"SELECT * FROM {table} WHERE subject='{subject}'"
    return cur.execute(query)


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
    # 6. manchester string (wiring.rs)
    man = wiring_rs.ofn_2_man(labeled)
    return man


def run_demo_2(database, subject):
    con = sqlite3.connect(database, check_same_thread=False)
    for row in get_statements(con, "statement", subject):
        # check for _JSON
        if row["datatype"] == "_JSON":
            print(object2omn(con, "statement", row["object"]))


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

    # run_demo(database, subject)
    run_demo_2(database, subject)
