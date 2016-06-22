import json
import urllib
import urllib2
import cookielib
import math
from dudehere.routines import *
from dudehere.routines.vfs import VFSClass
from dudehere.routines.plugin import Plugin
vfs = VFSClass()
plugin = Plugin()
COOKIE_PATH = vfs.join(DATA_PATH,'cookies')
MAX_PAGES = 3

class KatAPI():
	def __init__(self):
		self.base_url = 'https://kat.cr/'
		self.search_uri = 'json.php'
		self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
			'Accept-Encoding': 'none',
			'Accept-Language': 'pl-PL,pl;q=0.8',
			'Connection': 'keep-alive'
		}
	
	def search(self, title, season='', episode='', year='', return_results=False, finished=True):
		if season and episode:
			query = "%s S%sE%s" % (title, str(season).zfill(2), str(episode).zfill(2))
			media = 'episode'
		elif year:
			query = "%s %s" % (title, year)
			media = 'movies'
		else:
			query = title
			media = ''
			
		results = self._call(query, media)
		results = results['list']
		pages = int(math.ceil(float(self.total_results) / 25))
		page = 2
		while page < MAX_PAGES:
			temp = self._call(query, media, page)
			results += temp['list']
			page += 1
		
		if return_results:
			return self.process_results(results, media)
		
		link = self.show_select(results, media, finished)
		return link
		
	def process_results(self, results, media):
		from dudehere.routines.premiumize import PremiumizeAPI
		media = 'tv' if media == 'episode' else media
		links = []
		hashes = [r['hash'] for r in results]
		hashes = PremiumizeAPI().check(hashes)
		for r in results:
			if r['category'].lower() == media:
				hash = r['hash']
				if hash in hashes['hashes']:
					if hashes['hashes'][hash]['status'] != 'finished': continue
					links += [r]
		return links
	
	def show_select(self, results, media, return_finished):
		media = 'tv' if media == 'episode' else media
		links = []
		options = []
		hashes = [r['hash'] for r in results]
		from dudehere.routines.premiumize import PremiumizeAPI
		hashes = PremiumizeAPI().check(hashes)
		for r in results:
			if r['category'].lower() == media or media == '':
				hash = r['hash']
				if hash in hashes['hashes']:
					finished = hashes['hashes'][hash]['status'] == 'finished'
				if finished and return_finished is False: continue	
				size = self.format_size(r['size'])
				title = "[COLOR yellow]%s[/COLOR]" % r['title'] if finished else r['title']
				display = "[COLOR blue](%s)[/COLOR] %s" % (size, title)
				options += [display]
				links += [r['torrentLink']]
		index = plugin.dialog_select("Select a torrent", options)
		if index is False: return False
		if index or index == 0:
			return links[index]
		else: return False
	
	def format_size(self, size):
		size = float(size) / (1024 * 1024)
		if size > 2000:
			size = size / 1024
			unit = 'GB'
			size = "%.2f %s" % (size, unit)
		else :
			unit = 'MB'
			size = "%s %s" % (int(size), unit)
		return size
		
	def _call(self, query, media, page=1):
		if media:
			params = {"q": query, "category": media, "order": "seeders", "sort": "desc", "page": page}
		else:
			params = {"q": query, "order": "seeders", "sort": "desc", "page": page}
		url = self.base_url + self.search_uri + '?' + urllib.urlencode(params)
		ADDON.log(url)
		try:
			request = urllib2.Request(url, headers = self.headers)
			f = urllib2.urlopen(request)
			results = f.read()
			results =  json.loads(results)
			self.total_results = results['total_results']
			return results
		except:
			self.total_results = 0
			return {"list": []}