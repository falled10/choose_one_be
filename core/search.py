from elasticsearch import Elasticsearch

from core.settings import ELASTICSEARCH_URL


es = Elasticsearch(hosts=[ELASTICSEARCH_URL])


def add_to_index(index, instance):
    payload = {}
    for field in instance.__searchable__:
        payload[field] = getattr(instance, field)
    es.index(index=index, id=instance.id, body=payload)


def remove_from_index(index, instance):
    es.delete(index=index, id=instance.id)


def remove_index(index):
    es.indices.delete(index=index, ignore=[400, 404])


def query_index(index, query, page, per_page):
    search = es.search(
        index=index,
        body={'query': query,
              'from': (page - 1) * per_page, 'size': per_page},
    )
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
