from youtubesearchpython import *
import re
import pytube
import csv



def parse_title(title):
    #print(title)

    remove_list = [' in the Live Lounge', ' in the 1xtra Live Lounge', ' in the 1Xtra Live Lounge', ' (Live Lounge)', \
                   ' in the Radio 1 Live Lounge', ' (in the Live Lounge)', ' | Live Lounge Month 2020', ' – DJ Target 1Xtra Session', \
                    ' (Live)', ' on 1Xtra', ' - Radio 1\'s Piano Sessions', ' Radio 1\'s Piano Sessions', ' Live Lounge Special for BBC Radio 1'\
                        ' | BBC 1XTRA', ' – DJ Target Spotlight Session', ' (Live at Tuff Gong Studios)', ' Live Lounge 1Xtra', ' in the BBC 1Xtra Live Lounge'\
                            ' for 1Xtra', ' Radio 1 Live Lounge', ' for BBC 1Xtra\'s Hot for 2023', ' (1Xtra Live Lounge)', ' – DJ Target Spotlight', ' for BBC 1Xtra', ' BBC 1XTRA']
    for i in remove_list:
        if i in title:
            title = title.replace(i, '')
            break
    # XX cover(s) XX's/by XX
    r1 = re.compile(r".*covers?.*((\'s)|(s\')|(by)).*")
    # XX - XX (XX (cover))
    r2 = re.compile(r".*\s[\-\|]\s.*\s\(.*([Cc]over)?\)$")
    ## XX cover(s)/- XX
    r3 = re.compile(r".*\s((covers?)|(\-))\s.*")

    cover_singer = ''
    song = ''
    org_singer = ''

    try:
        if re.match(r1, title):
            partition = re.split(r'\scovers?\s', title)
            cover_singer = partition[0]
            partition = re.split(r'((\'s)|(s\')|(by))\s', partition[1])
            if ' by ' in title:
                org_singer = partition[-1]
                song = partition[0]
            else:
                org_singer = partition[0]
                song = partition[-1]
        elif re.match(r2, title):
            partition = re.split(r'\s[\-\|]\s', title)
            cover_singer = partition[0]
            partition = re.split(r'\s\(', partition[1])
            song = partition[0]
            org_singer = re.sub(r"(\s[Cc]over)?\)", "", partition[1])
        elif re.match(r3, title):
            #print(title)
            partition = re.split(r'\s((covers?)|(\-))\s', title)
            cover_singer = partition[0]
            song = partition[-1]
            org_singer = ''
        else:
            pass
            #print(title)
            #print()
    except:
        print('noooo')
        pass
        #print(title)
        #print()
    return cover_singer, org_singer, song


def get_likes(pytube_instance):
    like_template = r"like this video along with (.*?) other people"
    text = str(pytube_instance.initial_data)
    matches = re.findall(like_template, text, re.MULTILINE)
    if len(matches) >= 1:
        like_str = matches[0] 
        return int(like_str.replace(',', ''))
    return False


def print_video_info(video_dict, ai=False, viewcount_thre=0):
    title = video_dict['title']
    if ai and not 'ai' in title.lower():
        return None
    url = 'https://www.youtube.com/watch?v=' + video_dict['id']

    video_info = Video.getInfo(url, mode = ResultMode.json)
    viewcount = int(video_info['viewCount']['text'])
    if viewcount < viewcount_thre:
        return None
    
    pt = pytube.YouTube(url)
    likes = get_likes(pt)
    cover_singer, org_singer, song = parse_title(title)
    
    result_dic = dict()
    result_dic['cover_singer'] = cover_singer
    result_dic['original_singer'] = org_singer

    result_dic['url'] = url
    result_dic['title'] = title

    result_dic['views'] = viewcount
    result_dic['likes'] = likes
    result_dic['publish_date'] = video_info['publishDate']

    result_dic['keywords'] = video_info['keywords']
    result_dic['description'] = video_info['description']


    return result_dic



## playlist
# playlist = Playlist('https://www.youtube.com/playlist?list=PLEFin5ZtEWUpoUrRgsK5hbkLTjkvISOyP')
#
# print(f'Videos Retrieved: {len(playlist.videos)}')
#
# while playlist.hasMoreVideos:
#     print('Getting more videos...')
#     playlist.getNextVideos()
#     print(f'Videos Retrieved: {len(playlist.videos)}')
#
# print('Found all the videos.')
#
# result_rows = []
# count = 0
# for i in playlist.videos:
#     result_rows.append(print_video_info(i))
#     count += 1
#     if count %10 == 0:
#         print(count)


def main():
    fields = ['cover_singer', 'original_singer', 'url', 'title', 'views', 'likes', 'publish_date', 'keywords', 'description']
    artist = "Taylor Swift"

    result_rows = []
    count = 0
    index = 0
    videoSearch = VideosSearch(artist)
    if index == 0:
        videos = videoSearch.result()["result"]
        print(f'Videos Retrieved: {len(videos)}')
        for i in videos:
            result_rows.append(print_video_info(i))
            count += 1
            if count %10 == 0:
                print(count)
        index += 1

    while index > 0 and videoSearch.next():
        videoSearch.next()
        videos = videoSearch.result()["result"]
        print(f'Videos Retrieved: {len(videos)}')
        for i in videos:
            result_rows.append(print_video_info(i))
            count += 1
            if count %10 == 0:
                print(count)
        if len(videos) == 0:
            break



    # videoSearch.next()

    filename = f'{artist}.csv'
    with open(filename, 'w') as csvfile:
    # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=fields)
    # writing headers (field names)
        writer.writeheader()
    # writing data rows
        writer.writerows(result_rows)


if __name__ == '__main__':
    main()
