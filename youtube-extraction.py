from __future__ import unicode_literals
import pandas as pd
import numpy as np
import youtube_dl
import os
import subprocess
from sklearn.utils import shuffle


# import time

def cut_sound(file:str, start=0, duration=10) -> None:
    subprocess.call(['ffmpeg', '-y','-ss', str(start),  '-i', str(file), '-t', str(duration), f'{file}_cut.wav'])
    os.remove(file)
    os.rename(f'{file}_cut.wav', file)
    
def extract_sound(file):
    np.random.seed(0)
    url = ''
    start = 0
    end = 0
    label1 = ''
    label2 = ''
    label3 = ''
    label4 = ''

    titlely = ''
    ident = 0

    df = pd.read_csv(file, index_col=False)
    df.drop(columns='Unnamed: 0', errors='ignore', inplace=True)
    df.fillna(' ', inplace=True)
    df.columns = ['url', 'start', 'end', 'label1', 'label2', 'label3', 'label4']
    df = shuffle(df)
    print(df.head())


    for row in df.index:
        url = 'https://youtu.be/' + df.url[row]
        print (url)

        # start = int(df.start[row]
        # end = df.end[row]



        start_time = df.start[row]
        end_time = df.end[row]
        label1 = df.label1[row]
        label2 = df.label2[row]
        label3 = df.label3[row]
        label4 = df.label4[row]

        titlely = label1

        if label2!= ' ':
            titlely = titlely + '-' + label2

        if label3!=' ':
            titlely = titlely + '-' + label3

        if label4!=' ':
            titlely = titlely + '-' + label4

        titlely = titlely + '-' + str(ident)
        ident += 1

        print (titlely)

        ydl_opts = {
            'format': 'bestaudio[asr=44100]',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'outtmpl': f'sounds/{titlely}.%(ext)s',
            # 'playliststart': int(start_time),
            # 'playlistend': int(end_time),
            # 'duration': 10
        }

        try:
            with youtube_dl.YoutubeDL (ydl_opts) as ydl:
                ydl.download([url])
            cut_sound(f'sounds/{titlely}.wav', start_time)

        except youtube_dl.utils.DownloadError:
            continue

    return


file = 'database1.csv'
extract_sound ( file )