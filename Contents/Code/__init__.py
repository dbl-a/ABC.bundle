# PMS plugin framework
import re, string, datetime
from PMS import *

##################################################################################################ABC
PLUGIN_PREFIX     = "/video/ABC"

ABC_URL                     = "http://abc.go.com/"
ABC_FULL_EPISODES_SHOW_LIST = "http://abc.go.com/watch/shows"

ABC_FEED                    = "http://www.abc.com/fod/"
DEBUG                       = False
abcart                      ="art-default.png"
abcthumb                    ="icon-default.png"

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "ABC (US)","icon-default.jpg", "art-default.jpg")
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  
  MediaContainer.art        =R(abcart)
  DirectoryItem.thumb       =R(abcthumb)

####################################################################################################
#def MainMenu():
#    dir = MediaContainer(mediaType='video') 
#    dir.Append(Function(DirectoryItem(all_shows, "All Shows"), pageUrl = ABC_FULL_EPISODES_SHOW_LIST))
#    return dir
    
####################################################################################################
def MainMenu():
    pageUrl=ABC_FULL_EPISODES_SHOW_LIST
    dir = MediaContainer(mediaType='video')
    content = XML.ElementFromURL(pageUrl, True)
    Log(content.xpath('//div[@id="abcShows"]/div/a'))
    for item in content.xpath('//div[@id="abcShows"]/div/a'):
      Log(item)
      title=item.get('title')
      titleUrl = item.get('page')
      thumb=item.xpath("img")[0].get('src')
      summary=item.get('desc')
      Log(titleUrl)
      Log(thumb)
      Log(title)
      Log(summary)
      if titleUrl.count("afv---") !=1:
        dir.Append(Function(DirectoryItem(VideoPage, title,thumb=thumb, summary=summary), pageUrl = titleUrl))
    return dir 

####################################################################################################
def VideoPage(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    Log("Hello")
    Log(pageUrl)
    page = HTTP.Request(pageUrl)
    showID=re.compile('"showid": "(.+?)"}').findall(page)[0]
    Log("showID: ")
    Log(showID)
    bust=re.compile('bust=(.+?)"').findall(page)[0]
    Log("bust:")
    Log(bust)    
    seasonIDUrl="http://abc.go.com/vp2/s/carousel?svc=season&showid=" + showID + "&bust=" + bust
    Log(seasonIDUrl)
    page=HTTP.Request(seasonIDUrl)
    seasonID=re.compile('seasonid="(.+?)"').findall(page)[0]
    Log("seasonID: ")
    Log(seasonID)
    
    eplink1="http://abc.go.com/vp2/s/carousel?svc=showplaylist&showid=" + showID + "&playlistid=PL5515994&seasonid=" + seasonID + "&start=0&size=4&bust=" + bust

    dir=getnfo(dir,bust,eplink1)
      
    return dir
####################################################################################################
def getnfo(dir, bust, eplink1):
    
      content2=XML.ElementFromURL(eplink1, True)
      for item3 in content2.xpath('//div[@class="tile"]'):
        Log(item3)
        vidUrl=item3.xpath('div[@class="thumb"]/a')[0].get('href')
        thumb=item3.xpath('div[@class="thumb"]/a/img')[0].get('src')
        title=item3.xpath('div[@class="tile_title"]/a')[0].text
        summary=item3.xpath('div[@class="tile_desc"]')[0].text
        id=vidUrl.split('/')[-2]
        idUrl="http://cdn.abc.go.com/vp2/ws/s/contents/2000/utils/mov/13/9024/"+id+"/432?v="+ bust
        
        content3=XML.ElementFromURL(idUrl,False)
        for item4 in content3.xpath('//videos'):
          trueUrl=item4.xpath('video[@bitrate="1000"]')[0].get('src')
          clip=trueUrl.replace("mp4:/","")
          player="http://ll.media.abc.com/"
          Log(trueUrl)

          Log(thumb)
          Log(title)
          dir.Append(RTMPVideoItem(player, clip, title=title, thumb=thumb,summary=summary))
      return dir





