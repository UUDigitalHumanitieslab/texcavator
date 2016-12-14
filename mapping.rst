Mapping
=======

The elasticsearch mapping we currently use is as follows::

    {
      "settings": {
        "analysis" : {
          "analyzer" : {
            "dutch_analyzer" : {
              "type" : "custom",
              "tokenizer": "standard",
              "filter" : ["standard", "lowercase", "dutch_stemmer"]
            }
          },
          "filter" : {
            "dutch_stemmer" : {
              "type" : "stemmer",
              "name" : "dutch_kp"
            }
          }
        }
      },
      "mappings": {
        "doc": {
          "properties" : {
            "article_dc_subject": {
              "type": "string",
              "include_in_all": "false",
              "index": "not_analyzed"
            },
            "article_dc_title": {
              "type": "string",
              "term_vector": "with_positions_offsets_payloads",
              "fields": {
                "stemmed": {
                  "type": "string",
                  "analyzer": "dutch_analyzer",
                  "term_vector": "with_positions_offsets_payloads"
                }
              }
            },
            "identifier": {
              "type": "string",
              "include_in_all": "false",
              "index": "not_analyzed"
            },
            "paper_dc_date": {
              "format": "dateOptionalTime",
              "type": "date"
            },
            "paper_dc_title": {
              "type": "string",
              "term_vector": "with_positions_offsets_payloads",
              "fields": {
                "raw": {
                  "type": "string",
                  "index": "not_analyzed"
                }
              }
            },
            "paper_dcterms_spatial": {
              "type": "string",
              "include_in_all": "false",
              "index": "not_analyzed"
            },
            "paper_dcterms_temporal": {
              "type": "string",
              "include_in_all": "false",
              "index": "not_analyzed"
            },
            "text_content": {
              "type": "string",
              "term_vector": "with_positions_offsets_payloads",
              "fields": {
                "stemmed": {
                  "type": "string",
                  "analyzer": "dutch_analyzer",
                  "term_vector": "with_positions_offsets_payloads"
                }
              }
            }
          }
        }
      }
    }


An example document would then be::

    {
        "article_dc_subject": "newspaper",
        "article_dc_title": "Test for Texcavator",
        "identifier": "test1",
        "paper_dc_date": "1912-04-15",
        "paper_dc_title": "The Texcavator Test",
        "paper_dcterms_spatial": "unknown",
        "paper_dcterms_temporal": "daily",
        "text_content": "This is a test to see whether Texcavator works!"
    }
