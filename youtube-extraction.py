from __future__ import unicode_literals
import pandas as pd
import numpy as np
import youtube_dl
import os

from sklearn.utils import shuffle



# import time

def cut_sound(file:str, start:int=0, duration:int=10) -> None:
    subprocess.call(['ffmpeg', '-y','-ss', str(start),  '-i', str(file), '-t', str(duration), f'{file}_cut.wav'])
    os.remove(file)
    os.rename(f'{file}_cut.wav', file)

def list_to_str_unique(labels:list)-> str:
    print(labels)
    cleaned_list = np.unique([x for x in labels if str(x) != 'nan']).tolist()
    for i, x in enumerate(cleaned_list):
      if x.lower() == 'stream':
        cleaned_list.insert(0, cleaned_list.pop(i))
  
    return '-'.join(cleaned_list)
    
def extract_sound(file):

    np.random.seed(0)

    url = ''
    start = 0
    end = 0
    ident = 0

    df = pd.read_csv(file, index_col=False)

    df.fillna(' ', inplace=True)
    df.columns = ['url', 'start', 'end', 'label1', 'label2', 'label3', 'label4']
    df = shuffle(df)
    print(df.head())



    for row in df.index:
        url = 'https://youtu.be/' + df.url[row]
        print (url)


        start_time = df.start[row]
        end_time = df.end[row]

        labels = [df.label1[row], df.label2[row], df.label3[row], df.label4[row]]

        titlely = list_to_str_unique(labels)
        
        titlely = titlely + '-' + str(ident)
        
        print (titlely)
        
        ident += 1


        ydl_opts = {
            'format': 'bestaudio[asr=44100]',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'outtmpl': f'sounds/{titlely}.%(ext)s',
        }
        if os.path.isfile(f'sounds/{titlely}.wav'):
            print('file already exists')
            continue

        try:
            with youtube_dl.YoutubeDL (ydl_opts) as ydl:
                ydl.download([url])
            cut_sound(f'sounds/{titlely}.wav', start_time)

        except youtube_dl.utils.DownloadError:
            continue

    return



file = 'URL/df_3540.csv'
extract_sound ( file )

