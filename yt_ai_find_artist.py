from youtubesearchpython import *
import requests, re
from bs4 import BeautifulSoup
import pytube
import pafy
from itertools import filterfalse
import csv
import pandas as pd

import os
import shutil

df = pd.read_csv('wiki.csv')
unique_values = df.apply(set)
unique_singers = unique_values[0].union(unique_values[1])
remove_list = ['Low', 'Eve']
# print(unique_singers)
for i in remove_list:
    unique_singers.discard(i)
unique_singers = sorted(unique_singers)
print(len(unique_singers))

nums = [20, 50, 100, 130, 180, 200, 250, 300, 350, 400, 450, 520, 600, 650, 700, 730, 770, 785, 820]

all_dfs = []

for n in nums:
    file_name = './result/yt_ai_' + str(n) + '.csv'
    df = pd.read_csv(file_name)
    all_dfs.append(df)
    for index, row in df.iterrows():
        string = str(row['title']) + str(row['description'])
        for singer in unique_singers:
            if singer.lower() in string.lower() and singer != row['cover_singer']:
                if singer in 'BTS Jungkook' and row['cover_singer'] in 'BTS Jungkook':
                    continue
                df.at[index, 'original_singer'] = singer
                break
    all_dfs.append(df)

    # df.to_csv('./result/yt_ai_' + str(n) + '_processed.csv')
    # print(file_name)

result_df = pd.concat(all_dfs).drop_duplicates(subset=['url'])
result_df = result_df.reset_index(drop=True)
result_df = result_df.rename({'cover_singer': 'Source', 'original_singer': 'Target'}, axis=1)
result_df.to_csv('yt_ai_all.csv')
print(result_df)


