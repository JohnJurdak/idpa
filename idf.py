from elasticsearch import Elasticsearch, BadRequestError
import json

ELASTIC_PASSWORD = "Lx*=HqwOFH_Yi5sx3Q=V"

def create_connection():
    es = Elasticsearch(
        "https://localhost:9200",
        ca_certs="/Users/elie/Downloads/elasticsearch-8.10.4/config/certs/http_ca.crt",
        basic_auth=("elastic", ELASTIC_PASSWORD)
    )

    if not es.ping():
        raise ValueError("Elasticsearch is not running")

    return es

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

def tf_search(es, index_name, query):
    res = es.search(index=index_name, body=query)
    return res

def idf_search(es, index_name, query):
    res = es.search(index=index_name, body=query, profile=True)
    return res

def bm25_search(es, index_name, query):
    res = es.search(index=index_name, body=query, profile=True)
    return res

# Load your JSON data
with open('Books.json', 'r') as f:
    books = json.load(f)

# Create Elasticsearch connection
es = create_connection()

# Define the settings for the index, specifying the use of the BM25 algorithm
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

# Create indices
create_index(es, 'books', settings)
create_index(es, 'books_idf', settings)
create_index(es, 'books_bm25', settings)

# Index the data
index_data(es, 'books', books)

# Define a query
query = {
    "query": {
        "match": {
            "title": "fiction"
        }
    }
}

# Perform searches
res_tf = tf_search(es, 'books', query)
res_idf = idf_search(es, 'books_idf', query)
res_bm25 = bm25_search(es, 'books_bm25', query)

# Get the runtime of each algorithm
runtime_tf = res_tf['took']
runtime_idf = res_idf['took']
runtime_bm25 = res_bm25['took']

# Print the runtime of each algorithm
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