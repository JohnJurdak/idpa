import json
import os

ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')



from elasticsearch import Elasticsearch, helpers

ELASTIC_PASSWORD = "RRq_=87eqdMQlrbigSY-"

# Create the client instance
es = Elasticsearch(
    "https://localhost:9200",
    ca_certs="/Users/johnjurdak/Downloads/elasticsearch-8.10.4/config/certs/http_ca.crt",
    basic_auth=("elastic", ELASTIC_PASSWORD)
)


def search(word):
    query = {
        "query": {
            "match": {
                "title": word
            }
        }
    }
    response = es.search(index="books", body=query)
    hits = response["hits"]["hits"]

    # for hit in hits:
    #     print(f"Document ID: {hit['_id']}, Title: {hit['_source']['title']}")
    return hits

def knn_search(vector):
    query = {
        "knn": {
            "my_vector_field": {
                "vector": vector,
                "k": 10
            }
        }
    }
    response = es.search(index="my_index", body=query)
    hits = response["hits"]["hits"]
    # for hit in hits:
    #     print(f"Document ID: {hit['_id']}, Vector: {hit['_source']['my_vector_field']}")
    return hits


def upload_and_compare(file_path):
    # Read the document
    with open(file_path, 'r', encoding='ISO-8859-1') as f:
        document = f.read()

    # Index the document
    es.index(index="my_index", body={"title": document})

    # Construct a more_like_this query to find similar documents
    query = {
        "query": {
            "more_like_this": {
                "fields": ["title"],
                "like": document,
                "min_term_freq": 1,
                "max_query_terms": 20
            }
        }
    }

    # Perform the search in the books index
    response = es.search(index="books", body=query)

    # Extract the hits and their IDs
    hits = [(hit["_id"], hit["_source"]) for hit in response["hits"]["hits"]]

    return hits

