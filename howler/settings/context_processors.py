from django.conf import settings


def global_settings(request):
    http_start = 'http://'
    es_host = ''.join((settings.ES_HOSTS[0], ':', str(settings.ES_DEFAULT_PORT)))
    kibana_host = ''.join((settings.ES_HOSTS[0], ':', '5601'))
    return {
        'http_es_settings': ''.join(
            (http_start, es_host, '/', settings.ES_INDEX_PREFIX.format('*'), '/_settings?pretty')),
        'http_es_indices': ''.join(
            (http_start, es_host, '/_cat/indices?v')),
        'http_kibana': ''.join(
            (http_start, kibana_host)),
        'http_kuromoji_analyze_test': ''.join(
            (http_start, es_host, '/', settings.ES_INDEX_PREFIX.format('ja'), '/_analyze?pretty=true&analyzer=kuromoji_custom')),
    }
