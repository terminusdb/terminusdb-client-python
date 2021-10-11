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
        # test config
        result = runner.invoke(scripts.config)
        assert result.exit_code == 0
        assert (
            result.output
            == "Current config:\ndatabase=mydb\nendpoint=http://127.0.0.1:6363/\nteam=admin\n"
        )
        result = runner.invoke(
            scripts.config,
            [
                "test_key=test_value",
                "test_list=[value1, value2, 789]",
                "database=newdb",
                "test_num=1234",
            ],
        )
        assert result.exit_code == 0
        assert result.output == "config.json updated\n"
        with open("config.json") as file:
            setting = json.load(file)
            assert setting.get("database") == "newdb"
            assert setting.get("endpoint") == "http://127.0.0.1:6363/"
            assert setting.get("test_key") == "test_value"
            assert setting.get("test_list") == ["value1", "value2", 789]
            assert setting.get("test_num") == 1234
        result = runner.invoke(scripts.config)
        assert (
            result.output
            == "Current config:\ndatabase=newdb\nendpoint=http://127.0.0.1:6363/\nteam=admin\ntest_key=test_value\ntest_list=['value1', 'value2', 789]\ntest_num=1234\n"
        )
        result = runner.invoke(
            scripts.config, ["-d", "test_key", "-d", "test_list", "-d", "test_num"]
        )
        assert result.exit_code == 0
        assert result.output == "config.json updated\n"
        with open("config.json") as file:
            setting = json.load(file)
            assert setting.get("database") == "newdb"
            assert setting.get("endpoint") == "http://127.0.0.1:6363/"
        result = runner.invoke(scripts.config)
        assert (
            result.output
            == "Current config:\ndatabase=newdb\nendpoint=http://127.0.0.1:6363/\nteam=admin\n"
        )


# def test_no_server():
#     runner = CliRunner()
#     with runner.isolated_filesystem():
#         runner.invoke(scripts.startproject, input="mydb\n\n")
#         result = runner.invoke(scripts.commit)
#         assert result.exit_code == 1
