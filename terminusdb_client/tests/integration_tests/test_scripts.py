import datetime as dt
import json

from click.testing import CliRunner

from ...scripts import scripts


def test_script_happy_path(terminusx_token):
    testdb = "test" + str(dt.datetime.now()).replace(" ", "")
    testdb = "testdb"
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            scripts.startproject,
            input=f"{testdb}\nhttps://cloud-dev.dcm.ist/ubf40420team/\nyes\nubf40420team\n",
        )
        assert result.exit_code == 0
        with open("config.json") as file:
            setting = json.load(file)
            assert setting.get("database") == "testdb"
            assert setting.get("server") == "https://cloud-dev.dcm.ist/ubf40420team/"
            assert setting.get("use JWT token") == True
            assert setting.get("team") == "ubf40420team"
        result = runner.invoke(scripts.commit)
        assert result.exit_code == 0
        result = runner.invoke(scripts.sync)
        assert result.exit_code == 0
        result = runner.invoke(scripts.deletedb, [testdb])
        assert result.exit_code == 0
