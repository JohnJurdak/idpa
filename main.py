import json
import os

from elasticsearch import Elasticsearch, helpers
import time


ELASTIC_PASSWORD = "Lx*=HqwOFH_Yi5sx3Q=V"

def create_connection():
    es = Elasticsearch(
        "https://localhost:9200",
        ca_certs="/Users/elie/Downloads/elasticsearch-8.10.4/config/certs/http_ca.crt",
        basic_auth=("elastic", ELASTIC_PASSWORD)
    )

# es.indices.delete(index='my_index')
if not es.indices.exists(index='my_index'):
   # Create the index if it doesn't exist
   es.indices.create(index="my_index")




data = []
for filename in os.listdir("./"):
    if filename.endswith('output.json'):
        with open(filename, 'r') as open_file:
            json_data = json.load(open_file)
            for i, k in enumerate(json_data):
                data.append({
                    "_index": "my_index",
                    "_id": i,

                    "_source": k
                })

# Convert JSON data to Elasticsearch format
print(f"length of data: {len(data)}")
# Index data
helpers.bulk(es, data)

# Refresh the index to make sure all data is searchable
es.indices.refresh(index="my_index")
# Search for documents
query = {
    'query': {
        'match': {
            'title': 'lldlfaldfadthe big brown foxsflasdsss'
        }
    }
}

# query = {
#     'query': {
#         'match_all': {}
#     }
# }
result = es.search(index='my_index', body=query)

print("HERE")
# Print search results
# Print search results
if result['hits']['hits']:
    for hit in result['hits']['hits']:
        print(f'Document ID: {hit["_id"]}, score: {hit["_score"]}, source: {hit["_source"]}')
else:
    print("No results found.")

if es.indices.exists(index="my_index"):
    print("The index has been created.")
else:
    print("The index has not been created.")

# Delete the index
# es.indices.delete(index='my_index')
