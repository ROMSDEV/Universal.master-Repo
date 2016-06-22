import re
import xbmcaddon
import xbmcgui
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult
from dudehere.routines.vfs import VFSClass
from dudehere.routines.premiumize import PremiumizeAPI

pm = PremiumizeAPI()
vfs = VFSClass()

def validate_premiumize():
	return xbmcaddon.Addon('script.module.urlresolver').getSetting('PremiumizeMeResolver_login') == 'true'

class ytsScraper(CommonScraper):
	def __init__(self):
		self.service='yts'
		self.name = 'yts.ag'
		self.referrer = 'https://yts.ag'
		self.base_url = 'https://yts.ag'
		self.is_cachable = True
		self.broken = validate_premiumize() == False

	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		query = {"query_term": args['imdb_id']}
		uri = '/api/v2/list_movies.json'
		data = self.request(uri, query=query, return_json=True)
		if 'status' in data and data['status'] == 'ok':
			for movie in data['data']['movies']:
				results += self.process_results(movie)
		return self.get_response(results)
	
	def process_results(self, movie):
		results = []
		hashes = [r['hash'] for r in movie['torrents']]
		hashes = PremiumizeAPI().check(hashes)
		for link in movie['torrents']:
			if link['hash'] in hashes['hashes']:
				url = "%s://%s" % (self.service, link['hash'])
				result = ScraperResult({}, self.service, self.name, url, self.name)
				result.size = link['size_bytes']
				result.quality = self.test_quality(str(link['quality']))
				results += [result]
		return results
	
	def get_resolved_url(self, raw_url):
		resolved_url = ''
		hash = raw_url
		raw_url = "https://yts.ag/torrent/download/%s.torrent" % hash
		response = pm.queue(raw_url)
		if 'status' in response:
			if response['status'] == 'success':
				hash = response['id']
				results = pm.browse(hash)
				resolved_url = pm.get_stream(results)
			elif response['message'] == 'This torrent is already in the download list.':
				from difflib import SequenceMatcher
				def similar(a, b):
					return SequenceMatcher(None, a, b).ratio()
				results = pm.file_list()
				for r in results['content']:
					test = r['name'].lower()
					test = re.sub('[^0-9a-zA-Z]+', '.', test)
					if similar(test, title) > .8:
						hash = r['hash']
						results = pm.browse(hash)
						resolved_url = pm.get_stream(results)
		if hash:
			self.set_property('Playback.Hash', hash)
		return resolved_url		
