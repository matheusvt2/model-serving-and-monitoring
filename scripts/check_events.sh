#!/bin/bash

printf "Checking for events in Elasticsearch...\n"
count=$(curl -s -X GET "localhost:9200/predictions/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_all": {}
  }
}' | jq '.count')

if [ "$count" -gt 0 ]; then
    printf "Found %s events in Elasticsearch\n" "$count"
else
    printf "No events found in Elasticsearch\n"
fi

# most recents
# curl -s -X GET "localhost:9200/predictions/_search" -H 'Content-Type: application/json' -d'
# {
#   "size": 5,
#   "sort": [
#     { "@timestamp": { "order": "desc" } }
#   ],
#   "query": {
#     "match_all": {}
#   }
# }'