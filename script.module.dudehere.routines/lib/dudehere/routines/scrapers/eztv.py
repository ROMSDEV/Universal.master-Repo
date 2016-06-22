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

class eztvScraper(CommonScraper):
	def __init__(self):
		self.service='eztv'
		self.name = 'eztv.ag'
		self.referrer = 'https://eztv.ag'
		self.base_url = 'https://eztv.ag'
		self.is_cachable = True
		self.timeout = 5
		self.broken = validate_premiumize() == False
			
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'],args['year'])
		if uri:
			pattern = "S%sE%s" % (str(args['season']).zfill(2), str(args['episode']).zfill(2))
			results = self.process_results(uri, pattern)
		
		return self.get_response(results)

	
	def process_results(self, uri, pattern):
		results = []
		soup = self.request(uri, return_soup=True, cache=3600)
		links = soup.findAll('tr', {"class": "forum_header_border", "name": "hover"})
		for link in links:
			try:
				a = link.find('a', {"class": "download_1"})
				href = a['href']
				title = a['title']
				if re.search(pattern, href):
					url = "%s://%s" % (self.service, href)
					result = ScraperResult({}, self.service, self.name, url, title)
					result. quality = self.test_quality(title)
					match = re.search('>(\d+\.\d+)\s+(M|G)B<', str(link))
					if match:
						size, prefix = match.groups()
						if prefix == 'M':
							result.size = float(size) * 1024 * 1024
						else:
							result.size = float(size) * 1024 * 1024 * 1024

					results += [result]
					
			
			except:
				pass
		return results
	
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			title = args[0].replace(' ', '-').lower()
			title = re.sub("[^a-zA-Z0-9 -]", '', title)
			uri = '/showlist/'
			html = self.request(uri, cache=86640)
			pattern = '<a href="/shows/([0-9]+)/([^"]+)/" class="thread_link">'
			for match in re.finditer(pattern, html, re.DOTALL):
				code, test = match.groups()
				if title == test:
					uri = '/shows/%s/%s' % (code, test)
					return uri
		return False
	
	def get_resolved_url(self, raw_url):
		resolved_url = ''
		hash = ''
		#ADDON.log(raw_url)
		title = re.search('torrent\/(.+?)\.torrent$', raw_url).group(1)
		#title = title.replace('[kat.cr]', '')
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
