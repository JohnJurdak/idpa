from elasticsearch import Elasticsearch, BadRequestError
import json

ELASTIC_PASSWORD = "Lx*=HqwOFH_Yi5sx3Q=V"

# Create the client instance
es = Elasticsearch(
    "https://localhost:9200",
    ca_certs="/Users/elie/Downloads/elasticsearch-8.10.4/config/certs/http_ca.crt",
    basic_auth=("elastic", ELASTIC_PASSWORD)
)


def create_index(es, index_name, settings):
    try:
        es.indices.create(index=index_name, body=settings)
        print(f"Index '{index_name}' created successfully.")
    except BadRequestError as e:
        if "resource_already_exists_exception" in str(e):
            print(f"Index '{index_name}' already exists.")
        else:
            raise e


def index_data(es, index_name, data):
    for i, item in enumerate(data):
        es.index(index=index_name, id=i, body=item)

def tf_search(index_name, word ):
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
            "my_field": {
                "type": "text",
                "similarity": "my_similarity"
            }
        }
    }
}
    

    query = {
        "query": {
            "match": {
                "title": word
            }
        }   
    }
    create_index(es, index_name=index_name, settings=settings)
    res = es.search(index=index_name, body=query)
    return res

def idf_search(index_name, word):
    settings_idf = {
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
                "my_field": {
                    "type": "text",
                    "similarity": "my_similarity"
                }
            }
        }
    }

    query = {
        "query": {
            "match": {
                "title": word
            }
        }   
    }
    create_index(es, index_name, settings_idf)
    res = es.search(index=index_name, body=query, profile=True)
    return res

def bm25_search(index_name, word):
    settings_bm25 = {
        "settings": {
            "index": {
                "similarity": {
                    "default": {
                        "type": "BM25"
                    }
                }
            }
        }
    }

    query = {
    "query": {
        "match": {
            "title": word
        }
    }
}
    create_index(es, index_name=index_name, settings=settings_bm25)
    res = es.search(index=index_name, body=query, profile=True)
    return res

# Load your JSON data
with open('Books.json', 'r') as f:
    books = json.load(f)


# Index the data
index_data(es, 'books', books)

# Define a query


# Perform searches
res_tf = tf_search('books_tf', 'fiction')
res_idf = idf_search('books_idf', 'fiction')
res_bm25 = bm25_search('books_bm25', 'fiction')

# # Get the runtime of each algorithm
runtime_tf = res_tf['took']
runtime_idf = res_idf['took']
runtime_bm25 = res_bm25['took']

# # Print the runtime of each algorithm
print(f"Runtime with TF settings: {runtime_tf} ms")
print(f"Runtime with IDF settings: {runtime_idf} ms")
print(f"Runtime with BM25 settings: {runtime_bm25} ms")

# Print the results
for hit in res_tf['hits']['hits']:
    print(f"Found book {hit['_source']['title']} with score {hit['_score']} (TF)")
for hit in res_idf['hits']['hits']:
    print(f"Found book {hit['_source']['title']} with score {hit['_score']} (IDF)")
for hit in res_bm25['hits']['hits']:
    print(f"Found book {hit['_source']['title']} with score {hit['_score']} (BM25)")