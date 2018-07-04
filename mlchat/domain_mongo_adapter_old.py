from chatterbot.storage import StorageAdapter
#from chatterbot.adapters.exceptions import EmptyDatabaseException 
from chatterbot.conversation import Statement, Response
from pymongo import MongoClient
import logging

class DomainMongoDatabaseAdapter(StorageAdapter):
    """
    The MongoDatabaseAdapter is an interface that allows ChatterBot
    to store the conversation as a Mongo database.
    """

    def __init__(self, **kwargs):
        super(DomainMongoDatabaseAdapter, self).__init__(**kwargs)

        self.database_name = self.kwargs.get(
            "database", "chatterbot-database"
        )
        self.database_uri = self.kwargs.get(
            "database_uri", "mongodb://localhost:27017/"
        )
        self.database_domain = self.kwargs.get("domain", "default")
        
        self.read_only = {'True':True, 'False': False}.get(self.kwargs.get("read_only", False))
        # Use the default host and port
        self.client = MongoClient(self.database_uri)
        
        # Specify the name of the database
        self.database = self.client[self.database_name]

        # The mongo collection of statement documents
        self.statements = self.database['statements_'+self.database_domain]

    def count(self):
        return self.statements.count()

    def find(self, statement_text):
        values = self.statements.find_one({'text': statement_text})

        if not values:
            return None

        del(values['text'])

        # Build the objects for the response list
        response_list = self.deserialize_responses(
            values["in_response_to"]
        )
        values["in_response_to"] = response_list

        return Statement(statement_text, **values)

    def remove(self, statement_text):
        """
        Removes the statement that matches the input text.
        Removes any responses from statements if the response text matches the
        input text.
        """
        for statement in self.filter(in_response_to__contains=statement_text):
            statement.remove_response(statement_text)
            self.update(statement)

        self.statements.remove({'text': statement_text})

    def deserialize_responses(self, response_list):
        """
        Takes the list of response items and returns the
        list converted to object versions of the responses.
        """
        in_response_to = []

        for response in response_list:
            text = response["text"]
            del(response["text"])

            in_response_to.append(
                Response(text, **response)
            )

        return in_response_to

    def filter(self, **kwargs):
        """
        Returns a list of statements in the database
        that match the parameters specified.
        """
        filter_parameters = kwargs.copy()
        contains_parameters = {}

        # Convert Response objects to data
        if "in_response_to" in filter_parameters:
            response_objects = filter_parameters["in_response_to"]
            serialized_responses = []
            for response in response_objects:
                serialized_responses.append(response.serialize())

            filter_parameters["in_response_to"] = serialized_responses

        # Exclude special arguments from the kwargs
        for parameter in kwargs:

            if "__" in parameter:
                del(filter_parameters[parameter])

                kwarg_parts = parameter.split("__")

                if kwarg_parts[1] == "contains":
                    key = kwarg_parts[0]
                    value = kwargs[parameter]

                    contains_parameters[key] = {
                        '$elemMatch': {
                            'text': value
                        }
                    }

        filter_parameters.update(contains_parameters)

        matches = self.statements.find(filter_parameters)
        matches = list(matches)

        results = []

        for match in matches:
            statement_text = match['text']
            del(match['text'])
            try:
                response_list = self.deserialize_responses(match["in_response_to"])
                match["in_response_to"] = response_list

                results.append(Statement(statement_text, **match))
            except KeyError as e:
                pass
                #print (e)


        return results

    def update(self, statement, **kwargs):
        from pymongo import UpdateOne
        from pymongo.errors import BulkWriteError

        force = kwargs.get('force', False)
        # Do not alter the database unless writing is enabled
        logging.info('In update force:' + str(force))
        logging.info('In update self.read_only' + str(self.read_only))
        if force or not self.read_only :
            print('after checking condition')
            data = statement.serialize()

            operations = []

            update_operation = UpdateOne(
                {'text': statement.text},
                {'$set': data},
                upsert=True
            )
            operations.append(update_operation)

            # Make sure that an entry for each response is saved
            for response_dict in data.get('in_response_to', []):
                response_text = response_dict.get('text')

                # $setOnInsert does nothing if the document is not created
                update_operation = UpdateOne(
                    {'text': response_text},
                    {'$set': response_dict},
                    upsert=True
                )
                operations.append(update_operation)

            try:
                self.statements.bulk_write(operations, ordered=False)
            except BulkWriteError as bwe:
                # Log the details of a bulk write error
                self.logger.error(str(bwe.details))

        return statement

    def get_random(self):
        """
        Returns a random statement from the database
        """
        from random import randint

        count = self.count()

        random_integer = randint(0, count - 1)

        if self.count() < 1:
            raise EmptyDatabaseException()

        statement = self.statements.find().limit(1).skip(random_integer)

        values = list(statement)[0]
        statement_text = values['text']

        del(values['text'])
        return Statement(statement_text, **values)

    def drop(self):
        """
        Remove the database.
        """
        self.client.drop_database(self.database_name)
