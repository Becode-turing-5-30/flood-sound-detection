from __future__ import unicode_literals
import pandas as pd
import numpy as np
import youtube_dl
# import time

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
            'start_time': int(df.start[row]),
            'end_time': int(df.end[row]),
        }

        try:
            with youtube_dl.YoutubeDL (ydl_opts) as ydl:
                ydl.download ([url])

        except youtube_dl.utils.DownloadError:
            continue

        # time.sleep(1)


    return


file = 'test4.csv'
extract_sound ( file )
