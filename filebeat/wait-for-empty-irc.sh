#!/usr/bin/env bash
echo "Test if irclogs exists..."
while :
do
    IRCLOGS_INDEX_avail=$(curl -s -o /dev/null -w "%{http_code}" http://elasticsearch:9200/irclogs)
    echo "Elasticsearch irclog status-Code (200 exists, 404 not exists, 000 not reachable): $IRCLOGS_INDEX_avail"
    if [[ $IRCLOGS_INDEX_avail -eq 200 ]]; then
        echo "irclogs index exists"
        break
    fi
sleep 2
done

echo "Test if irclogs has 0 documents after waiting 10 seconds..."
sleep 10 # some time between reachable and importer has deleted mails
while :
do
    IRCLOGS_INDEX_result=$(curl -X GET http://elasticsearch:9200/irclogs/_count)
    echo "IRC res: $IRCLOGS_INDEX_result"
    IRCLOGS_INDEX_count=$(echo $IRCLOGS_INDEX_result | grep -Po '"count":.*?[^\\],')
    echo "IRC doc-count: $IRCLOGS_INDEX_count"
    if [ "$IRCLOGS_INDEX_count" == "\"count\":0," ]; then
        echo "irclogs index empty - start loading new logs..."
        break
    fi
sleep 2
done
if [ "$IRCLOGS_INDEX_count" == "\"count\":0," ]; then
    filebeat
else
    echo "Unexpected error, IRCLOGS_INDEX_count: $IRCLOGS_INDEX_count"
fi

