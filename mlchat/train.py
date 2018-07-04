from django.http import HttpResponse
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
import xml

def remove_tags(text):
    #replace double quote with single quote
    text = text.replace('"', '')
    print(text)
    return ''.join(xml.etree.ElementTree.fromstring(text).itertext())

bot = ChatBot("test bot",
              storage_adapter="mlchat.DomainMongoDatabaseAdapter",
              database="simsChat")


#bot.set_trainer(ChatterBotCorpusTrainer)

# Train based on the english corpus
#bot.train("chatterbot.corpus.english")
bot.set_trainer(ListTrainer)
#bot.train(["FA", "You get free money from the government",])
#bot.train(["SA", "Do you have any money left?",])
#bot.train(["You are fired!", "Ok, Craig.",])
#bot.train(["fired!", "Ok, Craig.",])

with open("kb.csv", "r") as filestream:
    for line in filestream:
        currentline = line.split(",")
        print("training " + currentline[0])
        print("ANS:" + remove_tags(currentline[1]))
        bot.train([currentline[0], remove_tags(currentline[1])])

