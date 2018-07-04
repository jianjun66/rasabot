from chatterbot.storage import StorageAdapter
from chatterbot.storage.mongodb import MongoDatabaseAdapter

class DomainMongoDatabaseAdapter(MongoDatabaseAdapter):
    """
    The MongoDatabaseAdapter is an interface that allows
    ChatterBot to store statements in a MongoDB database.

    :keyword database: The name of the database you wish to connect to.
    :type database: str

    .. code-block:: python

       database='chatterbot-database'

    :keyword database_uri: The URI of a remote instance of MongoDB.
    :type database_uri: str

    .. code-block:: python

       database_uri='mongodb://example.com:8100/'
    """

    def __init__(self, **kwargs):
        super(DomainMongoDatabaseAdapter, self).__init__(**kwargs)
 
        self.database_domain = self.kwargs.get("domain", "default")

        # The mongo collection of statement documents
        self.statements = self.database['statements_'+self.database_domain]

        # The mongo collection of conversation documents
        self.conversations = self.database['conversations_'+self.database_domain]

 

