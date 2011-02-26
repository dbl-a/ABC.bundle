import re, string, datetime

##################################################################################################ABC
PLUGIN_PREFIX = "/video/abc"
NAME          = "ABC"

ABC_ROOT      = "http://abc.go.com/"
SHOW_LIST     = "http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/001/001/-1/-1/-1/-1/-1/-1"
EPISODE_LIST  = "http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/001/001/lf/-1/%s/-1/-1/-1"
FEED_URL      = "http://cdn.abc.go.com/vp2/ws/s/contents/2000/utils/mov/13/9024/%s/432"
ART_URL       = "http://cdn.media.abc.go.com/m/images/shows/%s/bg/bkgd.jpg"

ART           = "art-default.jpg"
ICON          = "icon-default.png"

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, NAME, ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "InfoList"

    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13"

####################################################################################################
def MainMenu():
    dir = MediaContainer()
    content = XML.ElementFromURL(SHOW_LIST)
    for item in content.xpath('//item'):
        title = item.xpath('./title')[0].text
        artId = title.replace(': ', '-').replace(' ', '-').replace("'", "")
        art = ART_URL % (artId)                           #MIGHT NOT WANT TO USE THIS ART & ALL SHOW DON'T HAVE ART
        titleUrl = item.xpath('./link')[0].text
        description = HTML.ElementFromString(item.xpath('./description')[0].text)
        thumb = description.xpath('.//img')[0].get('src')
        summary= description.xpath('.//p')[0].text
        showId = titleUrl.split('?')[0]
        showId = showId.rsplit('/', 1)[1]
        dir.Append(Function(DirectoryItem(VideoPage, title, thumb=Function(Graphic, url=thumb, type="thumb"), summary=summary, art=Function(Graphic, url=art, type="art")), showId=showId, art=art))
    return dir 

####################################################################################################
def VideoPage(sender, showId, art):
    dir = MediaContainer(title2=sender.itemTitle)
    episodeRss = EPISODE_LIST % (showId)
    content = XML.ElementFromURL(episodeRss)
    #Log(content.xpath("//text()"))
    for item in content.xpath('//item'):
        link = item.xpath('./link')[0].text
        title1 = item.xpath('./title')[0].text
        title = title1.split(' Full Episode')[0]
        season = re.findall('s([0-9]+)', title1.split(' Full Episode')[-1])[0]
        episode = re.findall('e([0-9]+)', title1.split(' Full Episode')[-1])[0]
        subtitle = 's' + season + '.' + 'e' + episode
        description = HTML.ElementFromString(item.xpath('./description')[0].text)
        thumb = description.xpath('.//img')[0].get('src')
        summary = description.xpath('.//p')[0].text

        #Log(subtitle)
        #duration = description.xpath("//text()")[3].split(': ')[1]   #SHOWS DURATION, NEEDS BETTER METHOD TO OBTAIN & CHANGE TO MILLISECONDS
        #Log(duration)
        id = link.rsplit('/', 2)[1]
        url = FEED_URL % (id)
        dir.Append(Function(VideoItem(VideoPlayer, title=title, subtitle=subtitle, summary=summary, thumb=Function(Graphic, url=thumb, type="thumb"), art=Function(Graphic, url=art, type="art")), url=url))  
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
        #player="http://ll.video.abc.com/" + clip.replace("mp4:/","")  #DIRECT FEED BROKE!!!
        player = "rtmp://cp88586.edgefcs.net/ondemand/"    #WE'RE STREAMING
    return Redirect(RTMPVideoItem(player, clip))

####################################################################################################
def Graphic(url, type):
    try:
        data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
        return DataObject(data, 'image/jpeg')
    except:
        if type == "art":
            return Redirect(R(ART))
        else:
            return Redirect(R(ICON))