import urllib, os, xbmc, xbmcgui
import base64
addon_id = 'plugin.video.BurnIptv'
data_folder = 'special://home/addons/plugin.video.BurnIptv/'
Url = base64.b64decode('aHR0cDovL3BsYXl3ZWIueDEwLm14L3BocGJiL2Rvd25sb2FkL2xpc3RhMS8=')
File = ['python.pydev']

def download(url, dest, dp = None):
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create("Key burn  Activador","Introduciendo Codigo",' ', ' ')
    dp.update(0)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
 
def _pbhook(numblocks, blocksize, filesize, url, dp):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        raise Exception("Cancelar")
        dp.close()

for file in File:
	url = Url + file
	fix = xbmc.translatePath(os.path.join( data_folder, file))
	download(url, fix)
	

		
	
#import xbmcaddon, util	
#addon = xbmcaddon.Addon('plugin.fusion  Activador')	
	
#util.playMedia(addon.getAddonInfo('name'), addon.getAddonInfo('icon'), 
               #'special://home/addons/plugin.fusion  Activador/intro.mp4')	
	
	
