from elasticsearch import Elasticsearch, helpers
import json



ELASTIC_PASSWORD = "RRq_=87eqdMQlrbigSY-"
INDEX_NAME = "books_idf_trial_index_part30"

# Initialize Elasticsearch Client
es = Elasticsearch(
    "https://localhost:9200",
    ca_certs="/Users/johnjurdak/Downloads/elasticsearch-8.10.4/config/certs/http_ca.crt",
    basic_auth=("elastic", ELASTIC_PASSWORD)
)

def create_tf_index(es_client, index_name):
    # Define settings and mappings for the index
    settings = {
        "settings": {
        "index": {
            "similarity": {
                "my_similarity": {
                    "type": "scripted",
                    "script": {
                        "source": "double tf = Math.sqrt(doc.freq); return query.boost * tf;"
                    }
                }
            }
        }
    },
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                # Add other fields as necessary
            }
        }
    }
    # Create the index
    es_client.indices.create(index=index_name, body=settings, ignore=400)

def create_idf_index(es_client, index_name):
    # Define settings and mappings for the index
    settings = {
        "settings": {
        "index": {
            "similarity": {
                "my_similarity": {
                    "type": "scripted",
                    "script": {
                            "source": "double idf = Math.log((docCount - doc.freq + 0.5) / (doc.freq + 0.5)); return query.boost * idf;"
                    }
                }
            }
        }
    },
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                # Add other fields as necessary
            }
        }
    }
    # Create the index
    es_client.indices.create(index=index_name, body=settings, ignore=400)


def index_documents(es_client, index_name, file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    actions = [
        {"_index": index_name, "_id": i, "_source": item}
        for i, item in enumerate(data)
    ]
    # Use the bulk API to index documents
    helpers.bulk(es_client, actions)
    print("Indexing complete")

def tf_search(es_client, index_name, query_term):
    query = {
        "query": {
            "match": {
                "title": query_term
            }
        }
    }
    response = es_client.search(index=index_name, body=query)
    return response['hits']['hits']

def main():
    # create_tf_index(es, INDEX_NAME)
    create_idf_index(es, index_name=INDEX_NAME)
    print(INDEX_NAME)
    index_documents(es, INDEX_NAME, 'Books.json')
    word = "went"  # Replace with your search term
    hits = tf_search(es, INDEX_NAME, word)
    for hit in hits:
        print(f"Document ID: {hit['_id']}, Title: {hit['_source']['title']}")

if __name__ == "__main__":
    main()
