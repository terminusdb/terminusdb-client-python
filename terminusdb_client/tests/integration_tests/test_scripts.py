import datetime as dt
import json

from click.testing import CliRunner

from ...scripts import scripts


def test_script_happy_path(terminusx_token):
    testdb = "test" + str(dt.datetime.now()).replace(" ", "")
    endpoint = "https://cloud-dev.dcm.ist/ubf40420team/"
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            scripts.startproject,
            input=f"{testdb}\n{endpoint}\nyes\nubf40420team\n",
        )
        assert result.exit_code == 0
        with open("config.json") as file:
            setting = json.load(file)
            assert setting.get("database") == testdb
            assert setting.get("server") == "https://cloud-dev.dcm.ist/ubf40420team/"
            assert setting.get("use JWT token")
            assert setting.get("team") == "ubf40420team"
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
            f"Connecting to '{testdb}' at '{endpoint}'\non branch 'new'\nwith team 'ubf40420team'"
            in result.output
        )
        result = runner.invoke(scripts.rebase, ["main"])
        assert result.exit_code == 0
        assert f"Rebased main branch." in result.output
        result = runner.invoke(scripts.deletedb, [testdb])
        assert result.exit_code == 0
