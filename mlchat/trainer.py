from chatterbot.trainers import Trainer

from chatterbot.conversation import Statement, Response
import json
class PairTrainer(Trainer):
    """
    Allows a chat bot to be trained using a key value
    pair and extra data info
    """

    def train(self, key, value, extra_data_key, extra_data_value):
        """
        Train the chat bot based on key and value and extra data info
        """
        keyStatement = self.get_or_create(key)
        if extra_data_value:
            keyStatement.add_extra_data(extra_data_key, json.loads(extra_data_value))
        self.storage.update(keyStatement, force=True)

        valueStatement = self.get_or_create(value)
        valueStatement.add_response(
            Response(key)
        )
        self.storage.update(valueStatement, force=True)