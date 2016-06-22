#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.main import main

__settings__   = xbmcaddon.Addon()



BASE=[
('https://dl.dropbox.com/s/doa8gt9s0tdo2y7/Espana.xml', 'Respaldo TV España'),
#('http://playstationstorelibre.eshost.es/ps/Series.xml', 'Series España'),
]

#if (__settings__.getSetting("habilitarmodoadultos") == 'true') and (__settings__.getSetting("canalesrumanos") == 'true'): from resources.lib.main import main;main(BASE3)
if (__settings__.getSetting("habilitarmodoadultos") == 'true'): from resources.lib.main import main;main(BASE2)
#if (__settings__.getSetting("canalesrumanos") == 'true'): from resources.lib.main import main;main(BASE1)
else: from resources.lib.main import main;main(BASE)


