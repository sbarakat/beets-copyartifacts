init:
	virtualenv env
	./env/bin/pip install -r requirements.txt
	./env/bin/pip install -e .
	cp -b config.yaml ~/.config/beets/

test:
	nosetests tests
