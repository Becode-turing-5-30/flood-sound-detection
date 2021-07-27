import tweepy
import wget
import pandas as pd
import os
import moviepy.editor as mp
import subprocess

def video_scapper(search_words, item_limit=100000):
    video_list = pd.read_csv('videos.csv')

    consumerKey = "mHNhJxROGTTTVWsnWlAzcvAr6"
    consumerSecret = "fcGG7pll1dYPZEjqk64vTOL44AOPRcbqphWOoXEfvMXorq9RcU"
    accessToken = "1419583656549617665-wuXjKhmAelG2bcPhxoLx4sj0OQ8R7l"
    accessTokenSecret = "4NWxxQ7lgHKSOepK6UWJYFzHACzIXarLIt1uQ5iKBrvfR"

    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    date_since = "2021-07-01"
    date_until = "2021-07-26"

    tweets = tweepy.Cursor(api.search,
              q=search_words, since=date_since, until=date_until,
              include_entities=True, tweet_mode='extended').items()
    
    i = video_list.shape[0]
    for tweet in tweets:
        try:
            video_url = tweet._json['extended_entities']['media'][0]['video_info']['variants'][0]['url']
            print(video_url)
            if (video_list[['url']]==video_url).any().iloc[0]:
                continue
            video_list = video_list.append(pd.DataFrame({'url': [video_url], 'tweet':[tweet]}), ignore_index=True)
            filename = wget.download(video_url)
            extract_audio(filename, i)
            i+=1
            os.remove(filename)
        except:
            continue
    video_list.to_csv('videos.csv', index=False)

def extract_audio(filename, i):
    try:
        clip = mp.VideoFileClip(filename)
        clip.audio.write_audiofile(f'audio/flooding_audio{i}.wav')
    except:
        pass




if __name__=='__main__':
    video_scapper('#inondation')
    url_cmp = 'https://video.twimg.com/ext_tw_video/1418597331360903172/pu/pl/9KmQWdp8fFhgx0JG.m3u8?tag=12&container=fmp4'







