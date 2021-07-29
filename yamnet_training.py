import os

from IPython import display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.utils import shuffle

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_io as tfio

yamnet_model_handle = 'https://tfhub.dev/google/yamnet/1'
yamnet_model = hub.load(yamnet_model_handle)

class ReduceMeanLayer(tf.keras.layers.Layer):
  def __init__(self, axis=0, **kwargs):
    super(ReduceMeanLayer, self).__init__(**kwargs)
    self.axis = axis

  def call(self, input):
    return tf.math.reduce_mean(input, axis=self.axis)


@tf.function
def load_wav_16k_mono(filename):
    """ Load a WAV file, convert it to a float tensor, resample to 16 kHz single-channel audio. """
    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(
          file_contents,
          desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

def load_wav_for_map(filename, label, fold):
  return load_wav_16k_mono(filename), label, fold

def extract_embedding(wav_data, label, fold):
  ''' run YAMNet to extract embedding from the wav data '''
  scores, embeddings, spectrogram = yamnet_model(wav_data)
  num_embeddings = tf.shape(embeddings)[0]
  return (embeddings,
            tf.repeat(label, num_embeddings),
            tf.repeat(fold, num_embeddings))



def dataframe_creator(main_directory, categories=[]):
    df = pd.DataFrame({'filename':[], 'fold':[], 'target':[], 'category':[]})

    for i, cat in enumerate(categories):
        directory = f'{main_directory}/{cat}'
        for filename in os.listdir(directory):
            df = df.append({'filename':f'{directory}/{filename}', 'fold':0, 'target':i, 'category':cat}
                , ignore_index=True)

    df['target'] = df.target.astype('int')
    df['fold'] = df.fold.astype('int')
    df = shuffle(df)
    df.reset_index(drop=True, inplace=True)
    df['fold'] = df.apply(lambda x:0 if int(x.name)<=int(0.8*len(df)) else (1 if int(x.name)<int(0.9*0.8*len(df)) else 2), axis=1)

    return df

def dataset_builder(df):
    filenames = df['filename']
    targets = df['target']
    folds = df['fold']
    main_ds = tf.data.Dataset.from_tensor_slices((filenames, targets, folds))
    main_ds = main_ds.map(load_wav_for_map)
    main_ds = main_ds.map(extract_embedding).unbatch()
    cached_ds = main_ds.cache()
    train_ds = cached_ds.filter(lambda embedding, label, fold: fold ==0)
    val_ds = cached_ds.filter(lambda embedding, label, fold: fold == 1)
    test_ds = cached_ds.filter(lambda embedding, label, fold: fold == 2)

    # remove the folds column now that it's not needed anymore
    remove_fold_column = lambda embedding, label, fold: (embedding, label)

    train_ds = train_ds.map(remove_fold_column)
    val_ds = val_ds.map(remove_fold_column)
    test_ds = test_ds.map(remove_fold_column)

    train_ds = train_ds.cache().shuffle(1000).batch(32).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.cache().batch(32).prefetch(tf.data.AUTOTUNE)
    test_ds = test_ds.cache().batch(32).prefetch(tf.data.AUTOTUNE)
    return train_ds, val_ds, test_ds

def model_builder(train_ds, val_ds, classes):
    yamnet_model_handle = 'https://tfhub.dev/google/yamnet/1'
    model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(1024), dtype=tf.float32,
                          name='input_embedding'),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.25),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(len(classes))
    ], name='my_model')

    model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                 optimizer="adam",
                 metrics=['accuracy'])

    callback = tf.keras.callbacks.EarlyStopping(monitor='loss',
                                            patience=3,
                                            restore_best_weights=True)
    model.fit(train_ds, epochs=50, validation_data=val_ds, callbacks=callback)

    input_segment = tf.keras.layers.Input(shape=(), dtype=tf.float32, name='audio')
    embedding_extraction_layer = hub.KerasLayer(yamnet_model_handle,
                                            trainable=False, name='yamnet')
    _, embeddings_output, _ = embedding_extraction_layer(input_segment)
    serving_outputs = model(embeddings_output)
    serving_outputs = ReduceMeanLayer(axis=0, name='classifier')(serving_outputs)
    serving_model = tf.keras.Model(input_segment, serving_outputs)
    return serving_model

if __name__=='__main__':
    classes = ['stream', 'other']
    df = dataframe_creator('sounds',classes)
    train_ds, val_ds, test_ds = dataset_builder(df)
    model = model_builder(train_ds, val_ds, classes)
    saved_model_path = './stream_yamnet'
    model.save(saved_model_path, include_optimizer=False)
