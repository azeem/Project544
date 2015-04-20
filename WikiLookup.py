import requests

API_URL = "http://lookup.dbpedia.org/api/search/"

def _search(path, queryString, queryClass, maxHits):
    params = {
        "QueryString": queryString,
        "QueryClass": queryClass,
        "MaxHits": maxHits,
    }
    headers = {
        "Accept": "application/json"
    }
    request = requests.get(API_URL + path, params=params, headers=headers)
    return request.json()

def keywordSearch(queryString, queryClass = "", maxHits = 5):
    return _search("KeywordSearch", queryString, queryClass, maxHits)

def prefixSearch(queryString, queryClass = "", maxHits = 5):
    return _search("PrefixSearch", queryString, queryClass, maxHits)

def wikiMatches(word, maxDistance=5):
    import distance
    import re
    word = word.lower()
    response = keywordSearch(word, maxHits = 20)
    results = response["results"]
    for result in results:
        cleanLabel = re.sub(r'\(.*\)$', '', result["label"]).lower().strip()
        result["labelDistance"] = distance.levenshtein(word, cleanLabel)
    return [result for result in results if result["labelDistance"] <= maxDistance]
