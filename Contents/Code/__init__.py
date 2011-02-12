# PMS plugin framework
import string, datetime

##################################################################################################ABC
PLUGIN_PREFIX = "/video/ABC"

ABC_ROOT      = "http://abc.go.com/"
SHOW_LIST     = "http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/001/001/-1/-1/-1/-1/-1/-1"
EPISODE_LIST  = "http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/001/001/lf/-1/%s/-1/-1/-1"
FEED_URL      = "http://cdn.abc.go.com/vp2/ws/s/contents/2000/utils/mov/13/9024/%s/432"
ART_URL       = "http://cdn.media.abc.go.com/m/images/shows/%s/bg/bkgd.jpg"

ART           = "art-default.jpg"
THUMB         = "icon-default.jpg"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, 'ABC', THUMB, ART)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  
  MediaContainer.art = R(ART)
  DirectoryItem.thumb = R(THUMB)

####################################################################################################
def MainMenu():
    dir = MediaContainer(mediaType='video')
    content = XML.ElementFromURL(SHOW_LIST)
    for item in content.xpath('//item'):
      title = item.xpath('./title')[0].text
      artID = title.replace(': ', '-').replace(' ', '-').replace("'", "")
      art = ART_URL % (artID)                           #MIGHT NOT WANT TO USE THIS ART & ALL SHOW DON'T HAVE ART
      titleUrl = item.xpath('./link')[0].text
      description = HTML.ElementFromString(item.xpath('./description')[0].text)
      thumb = description.xpath('.//img')[0].get('src')
      summary= description.xpath('.//p')[0].text
      showID = titleUrl.split('?')[0]
      showID = showID.rsplit('/', 1)[1]
      dir.Append(Function(DirectoryItem(VideoPage, title,thumb=thumb, summary=summary, art=art), showID = showID, art=art))
    return dir 

####################################################################################################
def VideoPage(sender, showID, art):
    dir = MediaContainer(title2=sender.itemTitle)
    episodeRSS = EPISODE_LIST % (showID)
    content = XML.ElementFromURL(episodeRSS)
    #Log(content.xpath("//text()"))
    for item in content.xpath('//item'):
        link = item.xpath('./link')[0].text
        title1 = item.xpath('./title')[0].text
        title = title1.split(' Full Episode')[0]
        season=re.findall('s([0-9]+)',title1.split(' Full Episode')[-1])[0]
        episode=re.findall('e([0-9]+)',title1.split(' Full Episode')[-1])[0]
        subtitle='s'+season+'.'+'e'+episode
        description = HTML.ElementFromString(item.xpath('./description')[0].text)
        thumb = description.xpath('.//img')[0].get('src')
        summary = description.xpath('.//p')[0].text
        
        #Log(subtitle)
        #duration = description.xpath("//text()")[3].split(': ')[1]   #SHOWS DURATION, NEEDS BETTER METHOD TO OBTAIN & CHANGE TO MILLISECONDS
        #Log(duration)
        id=link.rsplit('/', 2)[1]
        url = FEED_URL % (id)
        dir.Append(Function(VideoItem(VideoPlayer, title=title, subtitle=subtitle,summary=summary, thumb=thumb, art=art), url=url))  
    return dir
    
####################################################################################################
def VideoPlayer(sender, url):
    dir = MediaContainer(title2=sender.itemTitle)
    Log(url)
    content=XML.ElementFromURL(url)
    for item in content.xpath('//videos'):
        clip=item.xpath('video[@bitrate="1000"]')[0].get('src')
        #clip=item.get('src')             #MIGHT WANT TO SETUP PREFS FOR QUALITY???
        #Log(clip)
        player="http://ll.media.abc.com/" + clip.replace("mp4:/","")
    return Redirect(VideoItem(player))
