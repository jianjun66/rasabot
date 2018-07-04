from __future__ import unicode_literals
from chatterbot.logic.logic_adapter import LogicAdapter
import logging

logging.basicConfig(level=logging.ERROR)

class BestMatchWithTags(LogicAdapter):
    """
    A logic adapter that returns a response based on known responses to
    the closest matches to the input statement.
    """

    def get(self, input_statement):
        """
        Takes a statement string and a list of statement strings.
        Returns the closest matching statement from the list.
        """
        statement_list = self.chatbot.storage.get_response_statements()
        logging.info(
            'Selecting response from {} total responses.'.format(
                len(statement_list)
            )
        )

        if not statement_list:
            if self.chatbot.storage.count():
                # Use a randomly picked statement
                logging.info(
                    'No statements have known responses. ' +
                    'Choosing a random response to return.'
                )
                random_response = self.chatbot.storage.get_random()
                random_response.confidence = 0
                return random_response
            else:
                raise self.EmptyDatasetException()

        closest_match = input_statement
        closest_match.confidence = 0

        # Find the closest matching known statement
        for statement in statement_list:
            confidence = self.compare_statements(input_statement, statement)
            #logging.info("Going through the whole list with confidence{} : {}".format(confidence, statement))
            if confidence > closest_match.confidence:
                statement.confidence = confidence
                closest_match = statement

        return closest_match
    
    
    def can_process(self, statement):
        """
        Check that the chatbot's storage adapter is available to the logic
        adapter and there is at least one statement in the database.
        """
        return self.chatbot.storage.count()

    def process(self, input_statement):

        # Select the closest match to the input statement
        closest_match = self.get(input_statement)
        logging.info('Using "{}" as a close match to "{}"'.format(
            input_statement.text, closest_match.text
        ))

        # Get all statements that are in response to the closest match
        response_list = self.chatbot.storage.filter(
            in_response_to__contains=closest_match.text
        )

        if response_list:
            logging.info(
                'Selecting response from {} optimal responses.'.format(
                    len(response_list)
                )
            )
            response = self.select_response(input_statement, response_list)
            response.confidence = closest_match.confidence
        else:
            response = self.chatbot.storage.get_random()
            self.logger.info(
                'No response to "{}" found. Selecting a random response.'.format(
                    closest_match.text
                )
            )

            # Set confidence to zero because a random response is selected
            response.confidence = 0

        #for r in response.in_response_to:
        #    self.logger.info(' ---------- In response to: {}'.format(r.in_response_to) )
            
        return response