# Command to initialize dev enviroment
init:
	pip3 install pipenv --upgrade
	pipenv install --dev
	pip install -e .

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
	pip install -U bumpversion
	git checkout master
	git pull origin master
	bumpversion patch
	git push origin master
	git push origin master:dev
	git push origin --tags

publish_release:
	pip install -U bumpversion
	git checkout dev
	git pull origin dev
	git pull origin master
	bumpversion minor
	git push origin dev
	git push origin dev:master
	git push origin --tags
