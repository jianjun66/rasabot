help:
	@echo "    train-nlu"
	@echo "        Train the natural language understanding using Rasa NLU."
	@echo "    train-core"
	@echo "        Train a dialogue model using Rasa core."
	@echo "    train"
	@echo "        Train a both dialogue and nlu model using Rasa core."
	@echo "    train-online"
	@echo "        Train stories."
	@echo "    run"
	@echo "        Runs the bot on the command line."

run:
	python3 bot.py run

train-nlu:
	python3 bot.py train-nlu

train-core:
	python3 bot.py train-dialogue

train-online:
	python3 bot.py train-online

train:
	npx chatito data/default/intellei.chatito --format=rasa 
	python3 bot.py train-nlu
	python3 bot.py train-dialogue
