import pandas as pd
import dotenv
import os
import requests
from datetime import datetime

dotenv.load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")


def get_youtube_video_list(singer_name):
    video_list = []
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={singer_name}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    for item in data.get("items", []):
        if item["id"]["kind"] == "youtube#video":
            video_id = item["id"].get("videoId")
            if video_id:
                print(video_id)
                video_list.append(video_id)

    return video_list


def get_youtube_comments(video_id):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={API_KEY}"
    response = requests.get(url)

    data = response.json()
    return data


def main():
    ## load the csv file

    base_dir = os.path.dirname(os.path.abspath(__file__))

    df = pd.read_csv(os.path.join(base_dir, "data", "billboard_artist.csv"))
    artist_playlist_data = []

    for index, row in df.iterrows():
        singer_name = row["artist"]
        print(singer_name)
        data = get_youtube_video_list(singer_name)
        for video_id in data:
            comments = get_youtube_comments(video_id)
            for i in comments.get("items", []):
                text = (
                    i.get("snippet", {})
                    .get("topLevelComment", {})
                    .get("snippet", {})
                    .get("textDisplay")
                )
                artist_playlist_data.append(
                    {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "video_id": video_id,
                        "comment": text if text else None,
                        "singer_name": singer_name,
                    }
                )

    ## save the data to a csv file
    df_playlist = pd.DataFrame(artist_playlist_data)
    df_playlist.to_csv(
        os.path.join(base_dir, "data", "billboard_artist_playlist.csv"), index=False
    )
    print(df_playlist.head())


if __name__ == "__main__":
    main()
