# Command to initialize dev enviroment
init:
	python -m pip install --upgrade pip
	python -m pip install poetry --upgrade
	poetry lock
	poetry install
	# poetry run python -m pip install -U -e .

#test without integration test
unittest:
	poetry run pytest terminusdb_client/tests --ignore=terminusdb_client/tests/integration_tests

# Command to run test and generate a coverage report on terminal
coverage:
	poetry run pytest --cov=terminusdb_client terminusdb_client/tests/
	coverage report

# Command to generate a coverage report html
coverage_html:
	poetry run coverage html -d terminusdb_client_coverage

# Command to generate a documentation coverage report
interrogate:
	poetry run interrogate -c setup.cfg

# command line for release: bumpversion (patch), tag and push
# assuming patches are in master
# run in poetry shell
publish_patch:
	tox
	pip install -U bumpversion
	git checkout master
	git pull origin master
	bumpversion patch
	git push origin master
	git push origin master:dev
	git push origin --tags

publish_release:
	tox
	pip install -U bumpversion
	git checkout dev
	git pull origin dev
	git pull origin master
	bumpversion minor
	git push origin dev
	git push origin dev:master
	git push origin --tags

publish_release_major:
	tox
	pip install -U bumpversion
	git checkout dev
	git pull origin dev
	git pull origin master
	bumpversion major
	git push origin dev
	git push origin dev:master
	git push origin --tags
