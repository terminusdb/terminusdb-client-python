# Command to initialize dev enviroment
init:
	python -m pip install pipenv --upgrade
	pipenv install --dev
	python -m pip install -e .

#test without integration test
unittest:
	pytest terminusdb_client/tests --ignore=terminusdb_client/tests/integration_tests

# Command to run test and generate a coverage report on terminal
coverage:
	pytest --cov=terminusdb_client terminusdb_client/tests/
	coverage report

# Command to generate a coverage report html
coverage_html:
	coverage html -d terminusdb_client_coverage

# Command to generate a documentation coverage report
interrogate:
	interrogate -c setup.cfg

# command line for release: bumpversion (patch), tag and push
# assuming patches are in master
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
