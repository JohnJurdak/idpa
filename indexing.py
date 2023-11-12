import json
import os

from elasticsearch import Elasticsearch, helpers
import time

ELASTIC_PASSWORD = "RRq_=87eqdMQlrbigSY-"

# Create the client instance
es = Elasticsearch(
    "https://localhost:9200",
    ca_certs="/Users/johnjurdak/Downloads/elasticsearch-8.10.4/config/certs/http_ca.crt",
    basic_auth=("elastic", ELASTIC_PASSWORD)
)



# Load JSON file
with open('Books.json', 'r') as f:
    data = json.load(f)

# Convert each item in data to the format expected by the bulk API
actions = [
    {
        "_index": "books", 
        "_id": i, 
        "_source": item
    } 
    for i, item in enumerate(data)
]

# Use the helpers module's bulk function to index the list of actions
helpers.bulk(es, actions)
print("indexing is done")
