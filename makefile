init:
	pip3 install pipenv --upgrade
	pipenv install --dev
test:
	# This runs all of the tests, on both Python 2 and Python 3.
	detox
ci:
	pip3 install -e .
	pipenv run py.test tests  --junitxml=report.xml

test-readme:
	@pipenv run python src/setup.py check --restructuredtext --strict && ([ $$? -eq 0 ] && echo "README.rst and HISTORY.rst ok") || echo "Invalid markup in README.rst or HISTORY.rst!"

flake8:
	pipenv run flake8 --ignore=E501,F401,E128,E402,E731,F821 woqlclient

coverage:
	pipenv run py.test tests --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=woqlclient tests

#command line for release: bumpversion (patch), tag and push
publish:
	pip install -U bumpversion
	#git remote add upstream git@github.com:terminusdb/terminus-client-python.git
	git checkout master
	git pull upstream master
	bumpversion patch
	git push upstream master
	git push upstream master --tags
