from elasticsearch import Elasticsearch, BadRequestError, helpers
import json
import os
prev_index = set()

ELASTIC_PASSWORD = "RRq_=87eqdMQlrbigSY-"

# Create the client instance
es = Elasticsearch(
    "https://localhost:9200",
    ca_certs="/Users/johnjurdak/Downloads/elasticsearch-8.10.4/config/certs/http_ca.crt",
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

def tf_search(index_name):
    print("we are in tf")
      # Define settings and mappings for the index
    prev_index.add(index_name)
    settings = {
        "settings": {
        "index": {
            "similarity": {
                "my_similarity": {
                    "type": "scripted",
                    "script": {
                        "source": "double tf = doc.freq; return tf;"
                    }
                }
            }
        }
    },
        "mappings": {
            "properties": {
                "title": {"type": "text", "similarity":"my_similarity"},
                # Add other fields as necessary
            }
        }
    }
    # Create the index
    es.indices.create(index=index_name, body=settings)
    es.indices.refresh(index=index_name)

    with open("Books.json", 'r') as open_file:
        json_data = json.load(open_file)
        for i, k in enumerate(json_data):
            data.append({
                "_index": index_name,
                "_id": i,
                "_source": k
            })
    helpers.bulk(es, data)  
    search_in_index("went", index_name)
    

def idf_search(index_name):
    print("we are in idf")
    prev_index.add(index_name)
    settings = {
        "settings": {
        "index": {
            "similarity": {
                "my_similarity": {
                    "type": "scripted",
                    "script": {
                            "source": "double idf = Math.log((field.docCount+0.5)/(term.docFreq+0.5)) + 0.5; return idf;"
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
    es.indices.create(index=index_name, body=settings, ignore=400)

    with open("Books.json", 'r') as open_file:
        json_data = json.load(open_file)
        for i, k in enumerate(json_data):
            data.append({
                "_index": index_name,
                "_id": i,
                "_source": k
            })
    helpers.bulk(es, data)  
    search_in_index("went", index_name)

def search_in_index(word, index_name):
    query = {
        "query": {
            "match": {
                "title": word
            }
        }
    }
    response = es.search(index=index_name, body=query)
    hits = response["hits"]["hits"]
    print(hits)
    for hit in hits:
        print(hit)
    return hits


def bm25_search(index_name):
    print("we are in bm25")
    prev_index.add(index_name)
    settings = {
        "settings": {
            "index": {
                "similarity": {
                    "default": {
                        "type": "BM25"
                    }
                }
            }
        },

    }
    es.indices.create(index=index_name, body=settings)
    es.indices.refresh(index=index_name)
    

    with open("Books.json", 'r') as open_file:
        json_data = json.load(open_file)
        for i, k in enumerate(json_data):
            data.append({
                "_index": index_name,
                "_id": i,
                "_source": k
            })
    helpers.bulk(es, data) 



# # Load your JSON data
# with open('Books.json', 'r') as f:
#     books = json.load(f)
#     print(books)
data = []
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# JSONFILE_DIR = os.path.join(BASE_DIR)
# for filename in os.listdir(JSONFILE_DIR):
#     if filename.endswith('Books.json'):
#         file_path = os.path.join(JSONFILE_DIR, filename)
#         with open(file_path, 'r') as open_file:
#             json_data = json.load(open_file)
#             for i, k in enumerate(json_data):
#                 print(k)
#                 data.append({
#                     "_index": "one_two_three",
#                     "_id": i,
#                     "_source": k
#                 })
# with open("Books.json", 'r') as open_file:
#     json_data = json.load(open_file)
#     for i, k in enumerate(json_data):
#         data.append({
#             "_index": "one_two_three",
#             "_id": i,
#             "_source": k
#         })
# helpers.bulk(es, data)

def get_prev():
    return(prev_index)


# tf_search("one_two_three")
# idf_search("odrob")

