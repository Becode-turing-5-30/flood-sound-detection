from __future__ import unicode_literals
import pandas as pd
import youtube_dl


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

    df = pd.read_csv(file, header=None)
    df.columns = ['url', 'start', 'end', 'label1', 'label2', 'label3', 'label4']

    for row in df.index:
        url = 'https://' + df.url[row]
        print (url)

        start_time = df.start[row]
        end_time = df.end[row]
        label1 = df.label1[row]
        label2 = df.label2[row]
        label3 = df.label3[row]
        label4 = df.label4[row]

        titlely = label1

        if label2 != ' ':
            titlely = titlely + '-' + label2

        if label3 != ' ':
            titlely = titlely + '-' + label3

        if label4 != ' ':
            titlely = titlely + '-' + label4

        titlely = titlely + '-' + str(ident)
        ident += 1

        print (titlely)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'outtmpl': f'sounds/{titlely}.%(ext)s',
            'start_time': start_time,
            'end_time': end_time,
        }

        with youtube_dl.YoutubeDL (ydl_opts) as ydl:
            ydl.download ([url])


    return


file = 'test2.csv'
extract_sound ( file )
