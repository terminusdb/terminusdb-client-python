import csv
import datetime as dt
import json
import os
from random import random

import pytest
from click.testing import CliRunner

from terminusdb_client.woqlclient.woqlClient import WOQLClient

from ...errors import InterfaceError
from ...scripts import scripts


def _check_csv(csv_file, output):
    with open(csv_file) as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for item in header:
            assert item.lower().replace(" ", "_") in output
        for row in csvreader:
            for item in row:
                assert item in output


def test_local_happy_path(docker_url, test_csv):
    testdb = "test_" + str(dt.datetime.now()).replace(" ", "")
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            scripts.startproject,
            input=f"{testdb}\n{docker_url}\n\n",
        )
        assert result.exit_code == 0
        # test commit and sync
        result = runner.invoke(scripts.commit)
        assert result.exit_code == 0
        assert f"{testdb} created." in result.output
        assert f"{testdb} schema updated." in result.output
        result = runner.invoke(scripts.sync)
        assert result.exit_code == 0
        assert f"schema.py is updated with {testdb} schema." in result.output
        # test checkout, branch and rebase
        result = runner.invoke(scripts.checkout, ["-b", "new"])
        assert result.exit_code == 0
        with open(".TDB") as file:
            setting = json.load(file)
            assert setting.get("branch") == "new"
            assert setting.get("ref") is None
        assert "Branch 'new' created, checked out 'new' branch." in result.output
        result = runner.invoke(scripts.status)
        assert result.exit_code == 0
        assert (
            f"Connecting to '{testdb}' at '{docker_url}'\non branch 'new'\nwith team 'admin'"
            in result.output
        )
        result = runner.invoke(scripts.rebase, ["main"])
        assert result.exit_code == 0
        assert "Rebased main branch." in result.output
        result = runner.invoke(scripts.branch, ["-d", "not_exist"])
        assert result.exit_code == 1
        assert isinstance(result.exception, InterfaceError)
        assert "not_exist does not exist." in str(result.exception)
        result = runner.invoke(scripts.branch, ["-d", "new"])
        assert result.exit_code == 1
        assert isinstance(result.exception, InterfaceError)
        assert (
            "Cannot delete new which is current branch, please checkout to another branch first."
            in str(result.exception)
        )
        result = runner.invoke(scripts.checkout, ["main"])
        result = runner.invoke(scripts.branch, ["-d", "new"])
        assert result.exit_code == 0
        assert "Branch 'new' deleted. Remain on 'main' branch." in result.output
        # test log and time travel
        result = runner.invoke(scripts.log)
        assert result.exit_code == 0
        assert "Schema updated by Python client." in result.output
        first_commit = result.output.split("\n")[6].split(" ")[-1]
        # test import export csv
        with open("grades.csv", "w") as writer:
            writer.write(test_csv)
        result = runner.invoke(scripts.importcsv, ["grades.csv", "-m", "My message"])
        assert result.exit_code == 0
        result = runner.invoke(scripts.alldocs, ["--schema"])
        assert "Grades" in result.output
        result = runner.invoke(scripts.alldocs, ["--type", "Grades"])
        _check_csv("grades.csv", result.output)
        result = runner.invoke(
            scripts.exportcsv, ["Grades", "--filename", "new_grades.csv"]
        )
        assert result.exit_code == 0
        with open("new_grades.csv") as file:
            out_file = file.read()
            assert "Elephant" in out_file
            _check_csv("grades.csv", out_file)
        # test alldocs and export with alldocs
        result = runner.invoke(scripts.alldocs, ["--type", "Grades", "-q", "grade=B-"])
        assert result.exit_code == 0
        assert "B-" in result.output
        result = runner.invoke(
            scripts.alldocs,
            [
                "--type",
                "Grades",
                "-q",
                "grade=B-",
                "--export",
                "--filename",
                "query_result.csv",
            ],
        )
        assert result.exit_code == 0
        with open("query_result.csv") as file:
            out_file = file.read()
            assert "B-" in out_file
        # cont' test log and time travel
        result = runner.invoke(scripts.log)
        assert "My message" in result.output
        result = runner.invoke(scripts.reset, ["--soft", first_commit])
        assert result.exit_code == 0
        with open(".TDB") as file:
            setting = json.load(file)
            assert setting.get("branch") == "main"
            assert setting.get("ref") == first_commit
        result = runner.invoke(scripts.status)
        assert (
            f"Connecting to '{testdb}' at '{docker_url}'\non branch 'main'\nwith team 'admin'\nat commit '{first_commit}'"
            in result.output
        )
        result = runner.invoke(scripts.log)
        assert "My message" in result.output
        result = runner.invoke(scripts.reset)
        assert "Reset head to newest commit" in result.output
        with open(".TDB") as file:
            setting = json.load(file)
            assert setting.get("branch") == "main"
            assert setting.get("ref") is None
        result = runner.invoke(scripts.reset, [first_commit])
        assert result.exit_code == 0
        result = runner.invoke(scripts.log)
        assert "My message" not in result.output
        assert "Schema updated by Python client." in result.output
        # test inherits
        client = WOQLClient(docker_url)
        client.connect(db=testdb)
        schema_objects = [
            {
                "@type": "Class",
                "@id": "ThingWithId",
                "@abstract": [],
                "id": "xsd:string",
                "@key": {"@type": "Lexical", "@fields": ["id"]},
            },
            {
                "@type": "Class",
                "@id": "Study",
                "@inherits": "ThingWithId",
                "title": {"@type": "Optional", "@class": "xsd:string"},
                "@key": {"@type": "Lexical", "@fields": ["id"]},
            },
        ]
        client.insert_document(schema_objects, graph_type="schema")
        client.insert_document({"@type": "Study", "id": "foo", "title": "My Study"})
        result = runner.invoke(
            scripts.alldocs,
            [
                "--type",
                "Study",
                "-q",
                "id=foo",
            ],
        )
        assert result.exit_code == 0
        # deletedb
        result = runner.invoke(scripts.deletedb, input="y\n")
        assert result.exit_code == 0
        assert (
            f"Do you want to delete '{testdb}'? WARNING: This opertation is non-reversible."
            in result.output
        )
        assert f"{testdb} deleted." in result.output


@pytest.mark.skipif(
    os.environ.get("TERMINUSX_TOKEN") is None, reason="TerminusX token does not exist"
)
def test_script_happy_path(terminusx_token):
    testdb = "test_" + str(dt.datetime.now()).replace(" ", "") + "_" + str(random())
    endpoint = "https://cloud-dev.terminusdb.com/TerminusDBTest/"
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            scripts.startproject,
            input=f"{testdb}\n{endpoint}\nTerminusDBTest\nyes\ny\n{terminusx_token}\n",
        )
        assert result.exit_code == 0
        with open("config.json") as file:
            setting = json.load(file)
            assert setting.get("database") == testdb
            assert (
                setting.get("endpoint")
                == "https://cloud-dev.terminusdb.com/TerminusDBTest/"
            )
            assert setting.get("use JWT token")
            assert setting.get("team") == "TerminusDBTest"
        result = runner.invoke(scripts.commit)
        assert result.exit_code == 0
        assert f"{testdb} created." in result.output
        assert f"{testdb} schema updated." in result.output
        result = runner.invoke(scripts.sync)
        assert result.exit_code == 0
        assert f"schema.py is updated with {testdb} schema." in result.output
        result = runner.invoke(scripts.checkout, ["-b", "new"])
        assert result.exit_code == 0
        assert "Branch 'new' created, checked out 'new' branch." in result.output
        result = runner.invoke(scripts.status)
        assert result.exit_code == 0
        assert (
            f"Connecting to '{testdb}' at '{endpoint}'\non branch 'new'\nwith team 'TerminusDBTest'"
            in result.output
        )
        result = runner.invoke(scripts.rebase, ["main"])
        assert result.exit_code == 0
        assert "Rebased main branch." in result.output
        result = runner.invoke(scripts.deletedb, input="y\n")
        assert result.exit_code == 0
        assert (
            f"Do you want to delete '{testdb}'? WARNING: This opertation is non-reversible."
            in result.output
        )
        assert f"{testdb} deleted." in result.output
