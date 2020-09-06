import pytest


@pytest.fixture(scope="module")
def one_class_obj():
    return {
        "@type": "api:WoqlResponse",
        "api:status": "api:success",
        "api:variable_names": [
            "Parents",
            "Description",
            "Class Name",
            "Class ID",
            "Children",
            "Abstract",
        ],
        "bindings": [
            {
                "Abstract": {
                    "@type": "http://www.w3.org/2001/XMLSchema#string",
                    "@value": "No",
                },
                "Children": {
                    "@type": "http://www.w3.org/2001/XMLSchema#string",
                    "@value": "",
                },
                "Class ID": "terminusdb:///schema#Journey",
                "Class Name": {
                    "@type": "http://www.w3.org/2001/XMLSchema#string",
                    "@value": "Bike Journey",
                },
                "Description": {
                    "@type": "http://www.w3.org/2001/XMLSchema#string",
                    "@value": "Bike Journey object that capture each bike joourney.",
                },
                "Parents": [["http://terminusdb.com/schema/system#Document"]],
            }
        ],
        "deletes": 0,
        "inserts": 0,
        "transaction_retry_count": 0,
    }


@pytest.fixture(scope="module")
def one_class_prop():
    return {
        "@type": "api:WoqlResponse",
        "api:status": "api:success",
        "api:variable_names": [
            "Property Type",
            "Property Range",
            "Property Name",
            "Property ID",
            "Property Domain",
            "Property Description",
        ],
        "bindings": [
            {
                "Property Description": {
                    "@type": "http://www.w3.org/2001/XMLSchema#string",
                    "@value": "",
                },
                "Property Domain": "terminusdb:///schema#Journey",
                "Property ID": "terminusdb:///schema#Duration",
                "Property Name": {
                    "@type": "http://www.w3.org/2001/XMLSchema#string",
                    "@value": "",
                },
                "Property Range": "http://www.w3.org/2001/XMLSchema#integer",
                "Property Type": {
                    "@type": "http://www.w3.org/2001/XMLSchema#string",
                    "@value": "Data",
                },
            }
        ],
        "deletes": 0,
        "inserts": 0,
        "transaction_retry_count": 0,
    }


@pytest.fixture(scope="module")
def one_object():
    return {
        "@type": "api:WoqlResponse",
        "api:status": "api:success",
        "api:variable_names": ["Object ID", "Object Type"],
        "bindings": [
            {
                "Object ID": "terminusdb:///data/Journey_myobj",
                "Object Type": "terminusdb:///schema#Journey",
            }
        ],
        "deletes": 0,
        "inserts": 0,
        "transaction_retry_count": 0,
    }


@pytest.fixture(scope="module")
def one_prop_val():
    return {
        "@type": "api:WoqlResponse",
        "api:status": "api:success",
        "api:variable_names": [
            "Value ID",
            "Value Class",
            "Property Value",
            "Property ID",
            "Object ID",
        ],
        "bindings": [
            {
                "Object ID": "terminusdb:///data/Journey_myobj",
                "Property ID": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                "Property Value": "terminusdb:///schema#Journey",
                "Value Class": "system:unknown",
                "Value ID": "system:unknown",
            },
            {
                "Object ID": "terminusdb:///data/Journey_myobj",
                "Property ID": "terminusdb:///schema#Duration",
                "Property Value": {
                    "@type": "http://www.w3.org/2001/XMLSchema#integer",
                    "@value": 75,
                },
                "Value Class": "system:unknown",
                "Value ID": "system:unknown",
            },
        ],
        "deletes": 0,
        "inserts": 0,
        "transaction_retry_count": 0,
    }
