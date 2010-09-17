# PMS plugin framework
import re, string, datetime
from PMS import *

##################################################################################################ABC
PLUGIN_PREFIX     = "/video/ABCFamily"

ABC_URL                     = "http://abc.go.com/"
ABC_FULL_EPISODES_SHOW_LIST = "http://abc.go.com/watch"

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
    for item in content.xpath('//div[@id="show_list_data"]//ul[@class="show_listing_item"]'):
      title=item.xpath("li[@class='show_listing_title']")[0].text
      titleUrl = item.xpath("li[@class='show_listing_url']")[0].text
      thumb= item.xpath("li[@class='show_listing_thumb']")[0].text
      if titleUrl.count("afv---") !=1:
        Log(titleUrl)
        Log(thumb)
        dir.Append(Function(DirectoryItem(VideoPage, title,thumb=thumb), pageUrl = titleUrl))
    return dir 

####################################################################################################
def VideoPage(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    Log("Hello")
    Log(pageUrl)
    page = HTTP.Request(pageUrl)
    key1=re.compile('showLongCarouselTabbedViewPL5515994\.setValues\(1,\'PL5515994\',\'(.+?),').findall(page)[0]
    Log("key1: ")
    Log(key1)
    eplink1="http://abc.go.com/vp2/showlongformcarouselimagelist/feed/" + key1
    eplink1=eplink1 + "/start/0/limit/100/t/PL5515994/c/showFEPCarousel/pg/false?rand=05040004_3"


    dir=getnfo(dir,key1,eplink1)
      
    return dir
####################################################################################################
def getnfo(dir, key1, eplink1):
    
      content2=XML.ElementFromURL(eplink1, True)
      for item3 in content2.xpath('//div[@class="full"]'):
        Log(item3)
        vidUrl=item3.xpath('div/div/div[@class="thumb_img"]/a')[0].get('href')
        thumb=item3.xpath('div/div/div[@class="thumb_img"]/a/img')[0].get('src')
        title=item3.xpath('div/div[@class="ep_title"]/a')[0].text
        id=vidUrl.split('/')[-2]
        idUrl="http://cdn.abc.go.com/vp2/ws/s/contents/2000/utils/mov/13/9024/"+id+"/432?v=05040004_3"
        
        content3=XML.ElementFromURL(idUrl,False)
        for item4 in content3.xpath('//videos'):
          trueUrl=item4.xpath('video[@bitrate="1000"]')[0].get('src')
          clip=trueUrl.replace("mp4:/","")
          player="http://ll.media.abc.com/"
          Log(trueUrl)

          Log(thumb)
          Log(title)
        dir.Append(RTMPVideoItem(player, clip, title=title, thumb=thumb))
      return dir





