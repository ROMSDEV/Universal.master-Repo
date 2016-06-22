import re
import xbmcaddon
import xbmcgui
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult
from dudehere.routines.vfs import VFSClass
from dudehere.routines.premiumize import PremiumizeAPI
from dudehere.routines.kat import KatAPI
kat = KatAPI()
pm = PremiumizeAPI()
vfs = VFSClass()

def validate_premiumize():
	return xbmcaddon.Addon('script.module.urlresolver').getSetting('PremiumizeMeResolver_login') == 'true'

class katScraper(CommonScraper):
	def __init__(self):
		self.service='kat'
		self.name = 'kat.cr'
		self.referrer = 'http://kat.cr'
		self.base_url = 'http://kat.cr'
		self.is_cachable = True
		self.broken = validate_premiumize() == False
			
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		links = kat.search(args['showname'], season=args['season'], episode=args['episode'], return_results=True)
		results = self.process_results(links)
		
		return self.get_response(results)
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		links = kat.search(args['title'], year=args['year'], return_results=True)
		results = self.process_results(links)
		return self.get_response(results)
	
	def process_results(self, links):
		results = []
		for link in links:
			url = "%s://%s" % (self.service, link['torrentLink'])
			result = ScraperResult({}, self.service, self.name, url, link['title'])
			result.size = link['size']
			result. quality = self.test_quality(link['title'])
			results += [result]
		return results
	
	def get_resolved_url(self, raw_url):
		resolved_url = ''
		hash = ''
		title = raw_url.split("title=")[1]
		title = title.replace('[kat.cr]', '')
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
