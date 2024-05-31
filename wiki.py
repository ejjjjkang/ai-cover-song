import pandas as pd
import wikipedia as wp
import re
html = wp.page("List_of_Live_Lounge_cover_versions").html().encode("UTF-8")

result_df = pd.DataFrame(columns=['cover_singer', 'original_singer', 'title'])

count = 0
for i in range(1, 28):
    df = pd.read_html(html)[i]  # Try 2nd table first as most pages contain contents table first
    for index, row in df.iterrows():
        cover_singer = row['Artist/group']
        song_and_singer = row['Song(s)']
        matches = re.findall(r'"([^"]+)"(?: \(with ([^\)]+)\))? by ([^"]+)', song_and_singer)
        j = 0
        while j < len(matches):
            count = count + 1
            current = matches[j]
            j = j + 1
            song = current[0]
            original_singer = current[2]
            # if multiple songs are seperated by /
            if '/' in song and '/' in original_singer:
                song_list = song.split('/')
                original_singer_list = original_singer.split('/')
                for k in range(len(song_list)):
                    pair = (song_list[k], '', original_singer_list[k])
                    matches.append(pair)
                continue

            original_singer = re.sub(r'\[note (\d)+\]', '', original_singer)
            original_singer = re.sub(r'\(?feat\..*$', '', original_singer).strip()
            if " and " in original_singer:
                if original_singer not in ['Chase and Status', 'Florence and the Machine', 'Of Monsters and Men', \
                                           'Francis and the Lights', 'Peter Bjorn and John', 'Lilly Wood and the Prick', \
                                           'The Naked and Famous', 'Mumford and Sons', 'Marina and the Diamonds',
                                           'Bob Marley and the Wailers']:
                    original_singer_list = original_singer.split(" and ")
                    for k in range(len(original_singer_list)):
                        pair = (song, '', original_singer_list[k])
                        matches.append(pair)
                    continue
            
            to_append = pd.DataFrame([{'cover_singer': cover_singer, 'original_singer': original_singer, 'title': song}])
            result_df = pd.concat([result_df, to_append])

print(count)
result_df = result_df.map(lambda x: x.strip() if isinstance(x, str) else x)
print(result_df)
result_df.to_csv('wiki.csv', encoding='utf-8', index=False)
