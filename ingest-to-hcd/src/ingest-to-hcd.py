from pulsar import Function
import json
from astrapy import DataAPIClient
from astrapy.constants import Environment, VectorMetric
from openai import OpenAI
from astrapy.info import CollectionDefinition, CollectionVectorOptions
import datetime
from datetime import timezone

# The IngestToAstraFunction takes a JSON input and stores it into Astra DB using the Data API
#



def generate_embedding(client, content):
    response = client.embeddings.create(input=content, model="text-embedding-3-small")
    return response.data[0].embedding




class IngestToHcdFunction(Function):
    def __init__(self):
        pass

    def process(self, input, context):
        # Get the data from the input
        data = json.loads(input)
        namespace = "default_namespace"
        try:
            # Initialize the client and get a "Database" object
            openai_client = OpenAI(api_key=context.get_user_config_value("api_key"))
            client = DataAPIClient(environment=Environment.HCD)
            database = client.get_database(context.get_user_config_value('hcd_endpoint'), token=context.get_user_config_value('hcd_token'))
            database.use_keyspace(namespace)
        except Exception as e:
            context.get_logger().error(f"Error initializing HCD DB client or getting database: {e}")
            raise

        # Get the collection to store the payload in
        try:
            collections = database.list_collection_names()
            if context.get_user_config_value('collection') in collections:
                collection = database.get_collection(context.get_user_config_value('collection'))
            else:
                # If the collection does not exist, create it

                context.get_logger().info(f"Collection {context.get_user_config_value('collection')} does not exist. Creating new collection.")


                collection_definition = CollectionDefinition(
                vector=CollectionVectorOptions(
                    dimension=1536,
                    metric=VectorMetric.COSINE,
                ),
                )
                collection = database.create_collection(
                    context.get_user_config_value('collection'),
                    definition=collection_definition,)


                collection = database.create_collection(context.get_user_config_value('collection'),definition=collection_definition)

        except Exception as e:
            context.get_logger().error(f"Error getting collection from HCD DB: {e}")
            raise

        # Insert the data into the collection
        #Add embedding
        try:
            embedding = generate_embedding(openai_client, data["content"])
            data["$vector"] = embedding
            timestamp = f"{datetime.datetime.now(timezone.utc).isoformat()[:-3]}Z"
            data["metadata"] = {"source": "Pulsar", 
                                "title": data["title"], 
                                "date": timestamp.split('T')[0], 
                                "timestamp": timestamp}
        except:
            context.get_logger.error(f"Could not generate embedding")
        try:
            collection.insert_one(document=data)
            context.get_logger().info(f"Data with message id {context.get_message_id()} successfully inserted into HCD DB collection {collection.name}.")
        except Exception as e:
            context.get_logger().error(f"Error inserting data into HCD DB collection: {e}")
            raise
    
        return json.dumps(data)