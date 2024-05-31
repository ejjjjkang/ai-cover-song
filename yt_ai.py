from youtubesearchpython import *
import requests, re
from bs4 import BeautifulSoup
import pytube
import pafy
from itertools import filterfalse
import csv
import pandas as pd

df = pd.read_csv('wiki.csv',header=None)
unique_values = df.apply(set)
unique_singers = sorted(unique_values[0].union(unique_values[1]))

def get_likes(pytube_instance):
    like_template = r"like this video along with (.*?) other people"
    text = str(pytube_instance.initial_data)
    matches = re.findall(like_template, text, re.MULTILINE)
    if len(matches) >= 1:
        like_str = matches[0] 
        return int(like_str.replace(',', ''))
    return False

def check_singers(video_title, video_description, singer_name):
    string = video_title + video_description
    return 'ai' in string.lower() and 'cover' in string.lower() and singer_name.lower() in string.lower()
    '''

    if not ('ai' in string.lower() and 'cover' in string.lower()):
        return False #[]
    else:
        True
    found_singers = set()
    string = video_title + video_description
    for singer in unique_singers:
        if singer.lower() in string.lower():
            found_singers.add(singer)
            if len(found_singers) >= 1:
                return True #sorted(found_singers, key=lambda x: string.lower().index(x.lower()))
    return False #[]
    '''




def print_video_info(video_dict, singer_name, viewcount_thre=0):
    title = video_dict['title']
    if not 'ai' in title.lower():
        return None
    url = 'https://www.youtube.com/watch?v=' + video_dict['id']

    video_info = Video.getInfo(url, mode = ResultMode.json)
    viewcount = int(video_info['viewCount']['text'])
    if viewcount < viewcount_thre:
        return None
    
    description = video_info['description'][:200]
    found_singers = check_singers(title, description, singer_name)
    if not found_singers:
        return None
    
    result_dic = dict()
    result_dic['views'] = viewcount

    pt = pytube.YouTube(url)
    likes = get_likes(pt)
    # cover_singer, org_singer, song = parse_title(title)
    result_dic = dict()
    result_dic['cover_singer'] = singer_name
    result_dic['original_singer'] = ''

    result_dic['description'] = description
    result_dic['url'] = url
    result_dic['title'] = title

    result_dic['views'] = viewcount
    result_dic['likes'] = likes
    result_dic['publish_date'] = video_info['publishDate']

    result_dic['keywords'] = video_info['keywords']

    return result_dic

result_rows = []
stop_view = 10000

for singer in unique_singers[785:]:
    # Those don't work - will debug later.
    if singer in ['Alan Fletcher', 'Almir Guineto', 'Chester French', "Cookin' on 3 Burners", 
                  "DNCE", "Daniel Merriweather", "Donae'o", "Editors", "Jónsi", "Natalie La Rose",
                  "Sam and the Womp", "Scouting for Girls", 'The Amazons', 'The King Blues',
                  'The Magic Numbers', 'The Ordinary Boys', 'Tulisa', 'Twin Atlantic', 'Various Artists', 'WSTRN']:
        continue
    search_term = 'AI cover ' + singer
    customSearch = CustomSearch(search_term, VideoSortOrder.viewCount, limit = 19)

    print(singer)
    current_view = stop_view + 5
    while current_view >= stop_view:
        results = customSearch.result()['result']
        current_view = current_view - 1
        for result in results:
            row = print_video_info(result,singer,stop_view)
            if row != None:
                print(row['views'])
                current_view = row['views']
                print(row['title'])
                result_rows.append(row)
            else:
                try:
                    current_view = int(result['viewCount']['text'].split(' ')[0].replace(',', ''))
                except:
                    current_view = 0
                # print(current_view)
        print('--')
        customSearch.next()
    print()


fields = ['cover_singer', 'original_singer', 'url', 'title', 'views', 'likes', 'publish_date', 'keywords', 'description']
filename = 'yt_ai.csv'
with open(filename, 'w') as csvfile:
    # creating a csv dict writer object
    writer = csv.DictWriter(csvfile, fieldnames=fields)
 
    # writing headers (field names)
    writer.writeheader()
 
    # writing data rows
    writer.writerows(result_rows)

