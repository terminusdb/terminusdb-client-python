init:
	pip3 install pipenv --upgrade
	pipenv install --dev
	pip install -e .
test:
	#pytest terminusdb_client/tests/
	tox
ci:
	tox
	#python -m pytest tests  --junitxml=report.xml

test-readme:
	@pipenv run python src/setup.py check --restructuredtext --strict && ([ $$? -eq 0 ] && echo "README.rst and HISTORY.rst ok") || echo "Invalid markup in README.rst or HISTORY.rst!"

flake8:
	pipenv run flake8 --ignore=E501,F401,E128,E402,E731,F821 woqlclient

coverage:
	pipenv run py.test terminusdb_client/tests --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=terminusdb_client terminusdb_client/tests

interrogate:
	interrogate -v -I -i -p -s terminusdb_client/woqlclient/woqlClient.py terminusdb_client/woqldataframe/woqlDataframe.py terminusdb_client/woqlquery/woql_query.py terminusdb_client/woqlquery/woql_library.py

#command line for release: bumpversion (patch), tag and push
publish_patch:
	pip install -U bumpversion
	#git remote add upstream git@github.com:terminusdb/terminus-client-python.git
	git pull upstream master
	bumpversion patch
	git push upstream master
	git push upstream master:dev
	git push upstream --tags

publish_release:
	pip install -U bumpversion
	#git remote add upstream git@github.com:terminusdb/terminus-client-python.git
	git checkout dev
	git pull upstream dev
	git pull upstream master
	bumpversion minor
	git push upstream dev
	git push upstream dev:master
	git push upstream --tags
