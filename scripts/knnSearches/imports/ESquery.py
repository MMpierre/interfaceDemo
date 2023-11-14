def get_geo_matching_missions(es,index,geo,distance):
    
    # Construct the query
    query = {
        "query": {
            "bool": {
                "must": {
                    "geo_distance": {
                        "distance": distance,
                        "address__geolocation__0": {
                            "lon": geo[0],
                            "lat": geo[1]
                        }
                    }
                }
            }
        }
    }

    # Initialize scroll
    page = es.search(index=index, scroll='1m', size=1000, body=query)  # Adjust size as needed
    scroll_id = page['_scroll_id']
    hits = page['hits']['hits']
    
    # Collect all IDs
    ids = [hit['_id'] for hit in hits]

    # Start scrolling
    while len(hits):
        page = es.scroll(scroll_id=scroll_id, scroll='1m')
        scroll_id = page['_scroll_id']
        hits = page['hits']['hits']
        ids.extend(hit['_id'] for hit in hits)

    return ids

def get_geo_matching_users(es,index,geo):
    
    # Construct the query
    query = {
            "query": {
                "bool": {
                "must": {
                    "geo_shape": {
                    "employment_zone": {
                        "shape": {
                        "type": "point",
                        "coordinates": [float(geo[0]), float(geo[1])]
                        },
                        "relation": "contains"
                    }
                    }
                }
                }
            }
            }

    # Initialize scroll
    page = es.search(index=index, scroll='1m', size=1000, body=query)  # Adjust size as needed
    scroll_id = page['_scroll_id']
    hits = page['hits']['hits']
    
    # Collect all IDs
    ids = [hit['_id'] for hit in hits]

    # Start scrolling
    while len(hits):
        page = es.scroll(scroll_id=scroll_id, scroll='1m')
        scroll_id = page['_scroll_id']
        hits = page['hits']['hits']
        ids.extend(hit['_id'] for hit in hits)

    return ids

def construct_mission_search_request(vec, index, n):
    header = {"index": index}
    body = {
        "query": {"match_all": {}},
        "_source": ["id","address__city__0"],
        "size": n,
        "knn": {
            "field": "vector",
            "query_vector": vec,
            "k": n,
            "num_candidates": n
        }
    }
    return header, body

def construct_profile_search_request(vec,field, index, n):
    header = {"index": index}
    body = {
        "query": {"match_all": {}},
        "_source": ["id","location__city__0"],
        "size": n,
        "knn": {
            "field": field,
            "query_vector": vec,
            "k": n,
            "num_candidates": n
        }
    }
    return header, body
