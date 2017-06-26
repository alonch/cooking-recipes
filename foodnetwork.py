import sys, re, requests, json

db = {}
url_matcher = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
script_matcher = re.compile('<script type="application/ld\+json">((?s)(.*?))</script>')
download = 0
def find_urls(root, predicate, persist):
	global download
	stack = [root]
	while(len(stack) > 0):
		url = stack.pop()
		r = requests.get(url)
		if r.status_code is not 200:
			print "invalid request: %s" % url
			continue
		
		page = r.text
		download += len(page)
		persist(url, page)

		for result in url_matcher.finditer(page):
			inner_url = result.group(0)
			if predicate(inner_url):
				persist(inner_url)
				stack.append(inner_url)

def find_json_ld(page):
	try:
		data = script_matcher.search(page).group(1)
		data = json.loads(data)
		data['status'] = 'VALID'
		return data
	except:
		return {'status':"INVALID"}

def save(url, page=None):
	db[url] = find_json_ld(page) if page else {}
	if len(db) % 100 is 0:
		print "%d - %d bytes" % (len(db), download)
	
def is_valid_url(url):
	return url.startswith("http://www.foodnetwork.com/recipes/") and url not in db.keys()

try:
	find_urls("http://www.foodnetwork.com/recipes/a-z", is_valid_url, save)
except:
	pass

with open("db.json", "w") as file:
	file.write(json.dumps(db))
