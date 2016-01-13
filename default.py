# https://docs.python.org/2.7/
import os
import sys
import urllib
import urlparse
# http://mirrors.kodi.tv/docs/python-docs/
import xbmcaddon
import xbmcgui
import xbmcplugin
# http://docs.python-requests.org/en/latest/
import requests
# http://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)
    
def get_page(url):
    # download the source HTML for the page using requests
    # and parse the page using BeautifulSoup
    return BeautifulSoup(requests.get(url).text, 'html.parser')
    
def parse_page(page):
    songs = {}
    index = 1
    # the sample below is specific for the page we are scraping
    # you will need to view the source of the page(s) you are
    # planning to scrape to find the content you want to display
    # this will return all the <a> elements on the page:
    # <a href="some_url">some_text</a>
    for item in page.find_all('a'):
        # the item contains a link to an album cover
        if item['href'].find('.jpg') > 1:
            # format the url for the album cover to include the site url and url encode any spaces
            album_cover = '{0}{1}'.format(sample_page, item['href'].replace(' ', '%20'))
        # the item contains a link to a song containing '.mp3'
        if item['href'].find('.mp3') > 1:
            # update dictionary with the album cover url, song filename, and song url
            songs.update({index: {'album_cover': album_cover, 'title': item['href'], 'url': '{0}{1}'.format(sample_page, item['href'])}})
            index += 1
    return songs
    
def build_song_list(songs):
    song_list = []
    # iterate over the contents of the dictionary songs to build the list
    for song in songs:
        # create a list item using the song filename for the label
        li = xbmcgui.ListItem(label=songs[song]['title'], thumbnailImage=songs[song]['album_cover'])
        # set the fanart to the albumc cover
        li.setProperty('fanart_image', songs[song]['album_cover'])
        # set the list item to playable
        li.setProperty('IsPlayable', 'true')
        # build the plugin url for Kodi
        # Example: plugin://plugin.audio.example/?url=http%3A%2F%2Fwww.theaudiodb.com%2Ftestfiles%2F01-pablo_perez-your_ad_here.mp3&mode=stream&title=01-pablo_perez-your_ad_here.mp3
        url = build_url({'mode': 'stream', 'url': songs[song]['url'], 'title': songs[song]['title']})
        # add the current list item to a list
        song_list.append((url, li, False))
    # add list to Kodi per Martijn
    # http://forum.kodi.tv/showthread.php?tid=209948&pid=2094170#pid2094170
    xbmcplugin.addDirectoryItems(addon_handle, song_list, len(song_list))
    # set the content of the directory
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)
    
def play_song(url):
    # set the path of the song to a list item
    play_item = xbmcgui.ListItem(path=url)
    # the list item is ready to be played by Kodi
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    
def main():
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    
    # initial launch of add-on
    if mode is None:
        # get the HTML for http://www.theaudiodb.com/testfiles/
        page = get_page(sample_page)
        # get the content needed from the page
        content = parse_page(page)
        # display the list of songs in Kodi
        build_song_list(content)
    # a song from the list has been selected
    elif mode[0] == 'stream':
        # pass the url of the song to play_song
        play_song(args['url'][0])
    
if __name__ == '__main__':
    sample_page = 'http://www.theaudiodb.com/testfiles/'
    addon_handle = int(sys.argv[1])
    main()