import json

from click.testing import CliRunner

from ..scripts import scripts


def test_startproject():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(scripts.startproject, input="mydb\n\n")
        assert result.exit_code == 0
        with open("config.json") as file:
            setting = json.load(file)
            assert setting.get("database") == "mydb"
            assert setting.get("endpoint") == "http://127.0.0.1:6363/"
        with open(".TDB") as file:
            setting = json.load(file)
            assert setting.get("branch") == "main"
            assert setting.get("ref") is None


# def test_no_server():
#     runner = CliRunner()
#     with runner.isolated_filesystem():
#         runner.invoke(scripts.startproject, input="mydb\n\n")
#         result = runner.invoke(scripts.commit)
#         assert result.exit_code == 1
