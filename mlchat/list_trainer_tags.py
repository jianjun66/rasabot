import logging
import os
import sys
from chatterbot.trainers import Trainer
from chatterbot.conversation import Statement, Response
from chatterbot import utils
import logging
import json

logging.basicConfig(level=logging.ERROR)

class ListTrainerWithTags(Trainer):
    """
    Allows a chat bot to be trained using a list of strings
    where the list represents a conversation.
    """
    """
    conversation = [a,b,c, d] a questions, b answer, c tag label, d tag search term
    """
    def train(self, conversation):

        question = conversation[0]
        answer = conversation[1]
        tags_label = None
        tags_search_term = None
        try:
            tags_label = conversation[2]
            tags_search_term = conversation[3]
        except:
            logging.info("Training without tags - it's ok")
            
        
        statement = self.get_or_create(question)
        self.storage.update(statement)         

        statement2 = self.get_or_create(answer)
        logging.info(' ----------- {}'.format(statement2.text))
        ts=[]
        if tags_label and tags_search_term:
            try:
                ts= statement2.extra_data["tags"]
            except:
                logging.info('statement does not have tags, add one')
                
            t={}
            t['label'] = tags_label
            t['search_term'] = tags_search_term
            ts.append(t)
            statement2.add_extra_data('tags', ts)
        statement2.add_response(
            Response(question)
        )
        self.storage.update(statement2)
