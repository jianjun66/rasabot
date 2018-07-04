help:
	@echo "    run"
	@echo "        Runs the bot server on 8000"
	@echo "    init"
	@echo "        install required modules"

run:
	python3 manage.py runserver 0.0.0.0:8000

init: 
	pip3 install -r requirements.txt
