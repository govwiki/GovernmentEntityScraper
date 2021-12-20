import requests
import json

ploads = {}
ploads['cx'] = '1dd01de6db84fff81'
ploads['q'] = 'TX Anderson County'
ploads['key'] = 'AIzaSyD3NInkVqkEtSYIMxUoh3SozL1NOe6qQ10'

r = requests.get(
    'https://customsearch.googleapis.com/customsearch/v1?', params=ploads)

print(r.status_code)
print(r.text)

fname = 'search_response3.json'

f1 = open(fname, 'w', encoding="UTF-8")
f1.write(r.text)
f1.close()

f2 = open(fname, encoding="UTF-8")
print(f2)

map = json.load(f2)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
headers = {"user-agent": USER_AGENT}

for item in map['items']:
    link = item['link']
    if 'wikipedia' not in link:
        try:
            r = requests.get(link, headers=headers, timeout=5)
            print(link + " " + str(r.status_code))
        except Exception as e:
            print(link + " error ")
