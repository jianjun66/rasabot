help:
	@echo "    run"
	@echo "        Runs the bot server on 8000"
	@echo "    init"
	@echo "        install required modules"
	@echo "    run"
	@echo "        Runs the bot on the command line."
	@echo "    train-nlu"
	@echo "        Train the natural language understanding using Rasa NLU."
	@echo "    train-core"
	@echo "        Train a dialogue model using Rasa core."
	@echo "    train"
	@echo "        Train a both dialogue and nlu model using Rasa core."
	@echo "    train-online"
	@echo "        Train stories."
	@echo "    runbot"
	@echo "        Runs the bot on the command line."

run:
	python3 manage.py runserver 0.0.0.0:8000

init: 
	pip3 install -r requirements.txt
	
train-nlu:
	python3 bot.py train-nlu

train-dialogue:
	python3 bot.py train-dialogue

train-online:
	python3 bot.py train-online

train:
	npx chatito intelleibot/data/default/intellei.chatito --format=rasa 
	python3 bot.py train-nlu
	python3 bot.py train-dialogue
	
runbot:
	python3 bot.py run
