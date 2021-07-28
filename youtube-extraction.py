from __future__ import unicode_literals
import pandas as pd
import numpy as np
import youtube_dl
import os
import subprocess


# import time

def cut_sound(file:str, start=0, duration=10) -> None:
    subprocess.call(['ffmpeg', '-y','-ss', str(start),  '-i', str(file), '-t', str(duration), f'{file}_cut.wav'])
    os.remove(file)
    os.rename(f'{file}_cut.wav', file)
    
def extract_sound(file):

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
    df.columns = ['url', 'start', 'end', 'label1', 'label2', 'label3', 'label4']
    print (df.head())


    for row in df.index:
        url = 'https://youtu.be/' + df.url[row]
        print (url)

        # start = int(df.start[row]
        # end = df.end[row]

        print(type(start))

        start_time = df.start[row]
        end_time = df.end[row]
        label1 = df.label1[row]
        label2 = df.label2[row]
        label3 = df.label3[row]
        label4 = df.label4[row]

        titlely = label1

        if not np.isnan(label2):
            titlely = titlely + '-' + label2

        if not np.isnan(label3):
            titlely = titlely + '-' + label3

        if not np.isnan(label4):
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


file = 'test1.csv'
extract_sound ( file )
