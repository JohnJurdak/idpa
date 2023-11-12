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

    for hit in hits:
        print(f"Document ID: {hit['_id']}, Title: {hit['_source']['title']}")
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


def build_and_execute_query(input_str):
    # Step 1: Parse the Input String
    category_keyword_index = input_str.find("where the ") + len("where the ")
    is_keyword_index = input_str.find(" is ")

    category = '"' + input_str[category_keyword_index:is_keyword_index].strip() + '"'
    value = input_str[is_keyword_index + len(" is "):].strip()
    print("category", category)
    print("value", value)
    # Step 2: Build the XQuery (This is a placeholder as XQuery is not directly used with Elasticsearch)
    xquery = f"<query><category>{category}</category><value>{value}</value></query>"

    # Step 3: Convert XQuery to Elasticsearch DSL
    # Note: This is a simple match query; adjust according to your needs
    es_query = {
        "query": {
            "match": {
                category.strip('"'): value
            }
        }
    }

    print("query",es_query)
    print("------")
    print()

    # Step 4: Execute the Elasticsearch Query
    response = es.search(index="books", body=es_query)
    hits = response["hits"]["hits"]

    for hit in hits:
        print(f"Document ID: {hit['_id']}, Title: {hit['_source']['title']}")
    return hits

def search_as_you_type(query):
    response = es.search(index="books", body={
        "query": {
            "match": {
                "title": {
                    "query": query,
                    "fuzziness": "AUTO"
                }
            }
        }
    })
    return [hit["_source"] for hit in response['hits']['hits']]