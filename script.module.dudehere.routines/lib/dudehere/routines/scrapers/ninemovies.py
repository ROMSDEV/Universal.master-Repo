#!/usr/bin/python
# -*- coding: utf-8 -*-
PYTHONIOENCODING="UTF-8"
import sys
import os
import re
import time
import urllib
from dudehere.routines import *
from dudehere.routines.vfs import VFSClass
from dudehere.routines.scrapers import CommonScraper, ScraperResult
QQ_MAP = {'720p': QUALITY.HD720, '1080p': QUALITY.HD1080}
AJAX_URL = '/ajax/film/episode?hash_id=%s&f=&p=%s'

class ninemoviesScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='ninemovies'
		self.name = '9movies.to'
		self.referrer = 'http://fmovies.to'
		self.base_url = 'http://fmovies.to'
		self.timeout = 3
	
	def search_tvshow(self, args):
		results = []
		url = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'],args['year'])
		if url:
			html = self.request(url, append_base=False, cache=86400)
			results = self.process_results(html, args['season'], args['episode'])
		return self.get_response(results)
	
	def search_movie(self, args):
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		if uri:
			html = self.request(uri)
			results = self.process_movie_results(html, args['year'])
		return self.get_response(results)
	
	def process_results(self, html, season, episode):
		episode = str(episode).zfill(2)
		results = []
		pattern = 'data-id="([^"]+)"\s+href="([^"]+)">%s<\/a>' % episode
		for match in re.finditer(pattern, html, re.DOTALL):
			id, url = match.groups()
			query = {'id': id, 'update': '0'}
			query.update(self.__get_token(query))
			ADDON.log(query)
			data = self.request('/ajax/episode/info', query, headers={'X-Requested-With': 'XMLHttpRequest', 'Referer': url}, return_json=True)
			ADDON.log(data)
			
		#pattern = 'href="([^"]+)" data-id="([^"]+)"\s*(data-subtitle="[^"]+")*\s*>\s*%s' % episode
		"""for match in re.finditer(pattern, html, re.DOTALL):
			uri, id, subs = match.groups()
			now = time.localtime()
			uri = AJAX_URL % (id, now.tm_hour + now.tm_min)
			data = self.request(uri, headers={'X-Requested-With': 'XMLHttpRequest'}, return_json=True)
			if 'videoUrlHash' in data and 'grabber' in data:
				query = {'flash': 1, 'json': 1, 's': now.tm_min, 'link': data['videoUrlHash'], '_': int(time.time())}
				query['link'] = query['link'].replace('\/', '/')
				grab_url = data['grabber'].replace('\/', '/')
				grab_url += '?' + urllib.urlencode(query)
				data = self.request(grab_url, headers={'X-Requested-With': 'XMLHttpRequest'}, append_base=False, return_json=True)
				for f in data:
					url = f['file']
					if 'label' in f:
						height = int(f['label'].replace('p', ''))
						quality = self.test_height_quality(height)
					else:
						quality = self.test_gv_quality(url, QUALITY.LOW)
					url = self.get_embeded_url(url)	
					result = ScraperResult(self.debrid_hosts, self.service, 'gvideo', url)
					result.quality = quality
					results += [result]"""
		return results
	
	def process_movie_results(self, html, year):
		results = []
		pattern = 'href="[^"]+" data-id="([^"]+)"\s*(data-subtitle="[^"]+")*'
		match = re.search(pattern, html)
		if match:
			id = match.group(1)
			now = time.localtime()
			uri = AJAX_URL % (id, now.tm_hour + now.tm_min)
			data = self.request(uri, headers={'X-Requested-With': 'XMLHttpRequest'}, return_json=True)
			if 'videoUrlHash' in data and 'grabber' in data:
					query = {'flash': 1, 'json': 1, 's': now.tm_min, 'link': data['videoUrlHash'], '_': int(time.time())}
					query['link'] = query['link'].replace('\/', '/')
					grab_url = data['grabber'].replace('\/', '/')
					grab_url += '?' + urllib.urlencode(query)
					data = self.request(grab_url, headers={'X-Requested-With': 'XMLHttpRequest'}, append_base=False, return_json=True)
					for f in data:
						url = f['file']
						if 'label' in f:
							height = int(f['label'].replace('p', ''))
							quality = self.test_height_quality(height)
						else:
							quality = self.test_gv_quality(url, QUALITY.LOW)
						url = self.get_embeded_url(url)	
						result = ScraperResult(self.debrid_hosts, self.service, 'gvideo', url)
						result.quality = quality
						results += [result]
		return results


	def get_resolved_url(self, url):
		return url

	def __get_token(self, data):
		n = 0
		for key in data:
			if not key.startswith('_'):
				for i, c in enumerate(data[key]):
					n += ord(c) * (i + 1990)
		return {'_token': hex(n)[2:]}
		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			soup = self.request('/search', query={"keyword": args[0], "type[]": "series"}, cache=86400, return_soup=True)
			div = soup.find('div', {"class": "row movie-list"})
			pattern = '<h1>([^<]+)<\/h1>\s+<span>(\d{4})'
			for f in div.findAll('div', {"class": "item"}):
				ajax_uri = f['data-tip']
				html = self.request(ajax_uri, cache=86400)
				match = re.search(pattern, html)
				if match:
					year = match.group(2)
					if year == str(args[3]):
						f = f.find('a', {"class": "poster"})
						return f['href']

		else:
			html = self.request('/search', query={"keyword": args[0], "type[]": "movie"}, cache=86400)
			pattern = '<a class="thumb" href="([^"]+)" title="([^"]+)">'
			for match in re.finditer(pattern, html, re.DOTALL):
				uri, title = match.groups()
				if title == args[0]:
					return uri
			return False

	
