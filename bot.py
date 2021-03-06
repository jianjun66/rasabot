from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import warnings

from intelleibot.policy import IntelleiPolicy
from rasa_core import utils
from rasa_core.actions import Action
from rasa_core.agent import Agent
from rasa_core.channels.console import ConsoleInputChannel
from rasa_core.events import SlotSet
from rasa_core.featurizers import (
    MaxHistoryTrackerFeaturizer,
    BinarySingleStateFeaturizer)
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.interpreter import RegexInterpreter
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.channels import HttpInputChannel
from rasa_core.channels.facebook import FacebookInput



logger = logging.getLogger(__name__)

domain_identifier = "default"
agents = {}
data_folder = "intelleibot/data"
model_folder = "intelleibot/models"

class ProgramAPI(object):
    def search(self, info):
        return "a list of programs (cats and dogs)"


class ActionSearchPrograms(Action):
    def name(self):
        return 'action_search_programs'

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("looking for programs.......")
        program_api = ProgramAPI()
        print("amount: {}".format(tracker.get_slot("amount")))
        print("interest: {}".format(tracker.get_slot("interest")))
        print("programs: {}".format(tracker.get_slot("program")))
        print("info: {}".format(tracker.get_slot("info")))
        programs = program_api.search(tracker.get_slot("program"))
        return [SlotSet("matches", programs)]


class ActionSuggest(Action):
    def name(self):
        return 'action_suggest'

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("here's what I found:")
        dispatcher.utter_message(tracker.get_slot("matches"))
        dispatcher.utter_message("is it ok for you? "
                                 "hint: I'm not going to "
                                 "find anything else :)")
        return []


def train_dialogue(domain_id = "default"):
    domain_file="{}/{}/domain.yml".format(data_folder, domain_id)
    model_path="{}/{}/dialogue".format(model_folder, domain_id)
    training_data_file="{}/{}/stories.md".format(data_folder, domain_id)
    agent = Agent(domain_file,
                  policies=[MemoizationPolicy(max_history=3),
                            IntelleiPolicy()])

    training_data = agent.load_data(training_data_file)
    agent.train(
            training_data,
            epochs=400,
            batch_size=100,
            validation_split=0.2
    )

    agent.persist(model_path)
    return agent


def train_nlu(domain_id = "default"):
    from rasa_nlu.training_data import load_data
    from rasa_nlu import config
    from rasa_nlu.model import Trainer

    training_data = load_data('{}/{}/intellei_rasa.json'.format(data_folder, domain_id))
    trainer = Trainer(config.load("intelleibot/nlu_model_config.yml"))
    trainer.train(training_data)
    model_directory = trainer.persist('{}/{}/nlu/'.format(model_folder, domain_id),
                                      fixed_model_name="current")

    return model_directory

def train():
    train_dialogue()
    train_nlu()
    
def answer( message, sender_id ,domain_id = 'default'):
    try:
        agent = agents[domain_id]
    except:
        interpreter = RasaNLUInterpreter("{}/{}/nlu/default/current".format(model_folder, domain_id))
        agent = Agent.load("{}/{}/dialogue".format(model_folder, domain_id), interpreter=interpreter)
        agents[domain_id] = agent
    return agent.handle_message(message, None, None, sender_id)
    
def run(domain_id = "default", serve_forever=True):
    interpreter = RasaNLUInterpreter("{}/{}/nlu/default/current".format(model_folder, domain_id))
    agent = Agent.load("{}/{}/dialogue".format(model_folder, domain_id), interpreter=interpreter)
     
    if serve_forever:
        agent.handle_channel(ConsoleInputChannel())
    return agent

# can't get this to work with FB  - FB requires https - the FB input channel runs on http
# use Django instead
def run_fb_webhook(a, b):
    print(a)
    print(b)
    domain_id = "default"
    try:
        agent = agents[domain_id]
    except:
        interpreter = RasaNLUInterpreter("{}/{}/nlu/default/current".format(model_folder, domain_id))
        agent = Agent.load("{}/{}/dialogue".format(model_folder, domain_id), interpreter=interpreter)
        agents[domain_id] = agent
    
    input_channel = FacebookInput(
        fb_verify="intelleibot",  # you need tell facebook this token, to confirm your URL
        fb_secret="f229180435b992cf99b715cc07af5760",  # your app secret
        fb_access_token="EAAFDolR6SBcBAOTdzAvEDP1VjDIRhaxCc7G6T1GTmIWRmr9vPSKERgiIxeGZBfqx7BRySQ9CVZCQ09BC8SdAXOEpGOnek5I1U2zCeJOUrj7AN2ZBjaxLutVVHJg9OWfVut4uZCL90etmWrAOscr0PjU71mJKImfpgw8wRrEw6wZDZD"   # token for the page you subscribed to
    )
    agent.handle_channel(HttpInputChannel(5004, "/intelleibot", input_channel))

def run_train_bot_online(input_channel, interpreter, domain_id = "default"):
    domain_file="{}/{}/domain.yml".format(data_folder, domain_id)
    training_data_file='{}/{}/stories.md'.format(data_folder, domain_id)
    agent = Agent(domain_file,
                  policies=[MemoizationPolicy(max_history=2), KerasPolicy()],
                  interpreter=interpreter)

    training_data = agent.load_data(training_data_file)
    agent.train_online(training_data,
                       input_channel=input_channel,
                       batch_size=50,
                       epochs=200,
                       max_training_samples=300)

    return agent

if __name__ == '__main__':
    utils.configure_colored_logging(loglevel="INFO")

    parser = argparse.ArgumentParser(
            description='starts the bot')

    parser.add_argument(
            'task',
            choices=["train-nlu", "train-dialogue", "run", "train-online", "runfbbot"],
            help="what the bot should do - e.g. run or train?")
    task = parser.parse_args().task

    # decide what to do based on first parameter of the script
    if task == "train-nlu":
        train_nlu()
    elif task == "train-dialogue":
        train_dialogue()
    elif task == "train-online":
        run_train_bot_online(ConsoleInputChannel(), RegexInterpreter())
    elif task == "run":
        run()
    elif task == "runfbbot":
        run_fb_webhook()
