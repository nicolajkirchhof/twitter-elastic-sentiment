#!/bin/bash
curl -XPUT localhost:9200/_template/tweet01 -d '{
    "template" : "tweets*",
    "settings" : {
        "number_of_shards" : 1
    },
    "mappings" : {
        "tweet_sentiment" : {
            "_all":       { "enabled": true },
            "_source":    { "enabled": true },
            "properties": {
                "date":         {
                    "type": "date",
A
A
A
A
A
A
A
A
A
B
B
B
B
B
B
B
B
B
B
B
B
B
B
B
B
B
B
B
B
B
                    "format": "yyy-MM-dd HH:mm:ss||epoch_millis",
                    "doc_values": true
                },
                "message":      {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type":  "string",
                            "index": "not_analyzed"
                        },
                        "german": {
                            "type":     "string",
                            "analyzer": "german"
                        }
                    }
                },
                "language":     { "type": "string", "index": "not_analyzed" },
                "hashtags":     { "type": "string", "index": "not_analyzed" },
                "location":     { "type": "geo_point", "ignore_malformed" : true },
                "sentiment":    { "type": "string", "index": "not_analyzed" },
                "polarity":     { "type": "float" },
                "subjectivity": { "type": "float" }
            }
        }
    }
}'
