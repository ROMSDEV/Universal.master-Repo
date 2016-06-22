# coding: utf-8
__author__ = 'mancuniancol'


import xbmc,xbmcaddon,xbmcgui,json,re,urllib

class FollwitXBMCInterface():

    def __init__(self, debug=False):
        if debug:
            self.debug = True
        else:
            self.debug = False

    # Method to return imdb_id
    # @param xbmc_id    id of movie
    def getMovieIMDB(xbmc_id):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetMovieDetails', 'params': {"movieid": int(xbmc_id), 'properties': ['imdbnumber']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)

        try:
            temp = result['result']['moviedetails']['imdbnumber']
            return True
        except:
            return False

    # Method to return dictionary of tvbd series id, season #, and episode #
    # @param xbmc_id    id of episode
    def getEpisodeTVDB(xbmc_id):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodeDetails', 'params': {"episodeid": int(xbmc_id), 'properties': ['season', 'episode', 'tvshowid', 'showtitle']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)

        try:
            item = {}
            item['season'] = result['result']['episodedetails']['season']
            item['tvshowid'] = result['result']['episodedetails']['tvshowid']
            item['episode'] = result['result']['episodedetails']['episode']
            item['showtitle'] = result['result']['episodedetails']['showtitle']

            #still need to get tvshowid from thetvdb. this is in TVShowDetails not Episode Details
            rpccmd = args= {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShowDetails', 'params': {"tvshowid": int(item['tvshowid']), 'properties': ['imdbnumber']}, 'id': 1}
            rpccmd = json.dumps(rpccmd)
            result = xbmc.executeJSONRPC(rpccmd)
            result = json.loads(result)
            item['tvshowid'] = result['result']['tvshowdetails']['imdbnumber']

            return item
        except:
            #failed to find episode matching xbmc movie id
            if self.debug:
                print '[Follwit Addon] Failed to find episode with an id matching the xbmc episodeid. ID given: '+str(xbmc_id)
            return False

    # Method to return all movies in xbmc library
    def getAllMovies(self):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetMovies', 'params': {'properties': ['imdbnumber', 'playcount']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)
        return result

    # Method to return all episodes in xbmc library
    def getAllEpisodes(self):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodes', 'params': {'properties': ['season', 'episode', 'tvshowid', 'showtitle', 'playcount']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)
        return result

    # Method to return all tv shows in xbmc library
    def getAllTVShows(self):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShows', 'params': {'properties': ['imdbnumber']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)
        return result

    # Method to return if an episode is watched
    def isWatchedEpisode(self, xbmc_id):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodeDetails', 'params': {"episodeid": int(xbmc_id), 'properties': ['playcount']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)

        try:
            if result['result']['episodedetails']['playcount'] > 0:
                return True
            else:
                return False
        except:
            #failed to find movie with an imdbid matching the xbmc movie id
            if self.debug:
                print '[Follwit Addon] Failed to find episode matching the xbmc movieid. ID given: '+str(xbmc_id)
            return False

    def isWatchedMovie(self, xbmc_id):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetMovieDetails', 'params': {"movieid": int(xbmc_id), 'properties': ['playcount']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)

        try:
            if result['result']['moviedetails']['playcount'] > 0:
                return True
            else:
                return False
        except:
            #failed to find movie with an imdbid matching the xbmc movie id
            if self.debug:
                print '[Follwit Addon] Failed to find movie matching the xbmc movieid. ID given: '+str(xbmc_id)
            return False

    def setWatchedEpisode(self, xbmc_id):
        if self.debug:
            print '[Follwit Addon] Setting episode watched for id '+str(xbmc_id)
        match = self.xbmcHttpapiQuery(
        "SELECT episode.idFile FROM episode"+
        " WHERE episode.idEpisode='%(xbmc_id)s'" % {'xbmc_id':self.xcp(xbmc_id)})

        result = self.xbmcHttpapiExec(
        "UPDATE files"+
        " SET playcount=%(playcount)d" % {'playcount':int(1)}+
        " WHERE idFile=%(idFile)s" % {'idFile':self.xcp(match[0])})

        if self.debug:
            print "xml answer: " + str(result)

    def setWatchedMovie(self, xbmc_id):
        if self.debug:
            print '[Follwit Addon] Setting movie watched for id '+str(xbmc_id)
        match = self.xbmcHttpapiQuery(
        "SELECT movie.idFile FROM movie"+
        " WHERE movie.idMovie='%(xbmc_id)s'" % {'xbmc_id':self.xcp(xbmc_id)})

        result = self.xbmcHttpapiExec(
        "UPDATE files"+
        " SET playcount=%(playcount)d" % {'playcount':int(1)}+
        " WHERE idFile=%(idFile)s" % {'idFile':self.xcp(match[0])})

        if self.debug:
            print "xml answer: " + str(result)


    # SQL string quote escaper
    def xcp(self, s):
        return re.sub('''(['])''', r"''", str(s))

    # make a httpapi based XBMC db query (get data)
    def xbmcHttpapiQuery(self, query):
        if self.debug:
            print "[httpapi-sql] query: "+query

        xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urllib.quote_plus(query), )
        match = re.findall( "<field>((?:[^<]|<(?!/))*)</field>", xml_data,)

        if self.debug:
            print "[httpapi-sql] responce: "+xml_data
            print "[httpapi-sql] matches: "+str(match)

        return match

    # execute a httpapi based XBMC db query (set data)
    def xbmcHttpapiExec(self, query):
        xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus(query), )
        return xml_data