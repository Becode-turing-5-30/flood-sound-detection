import streamlit as st
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_io as tfio
import xgboost as xgb



st.title('Flooding sound detection')


def predict(filename):
    yamnet_model_handle = 'https://tfhub.dev/google/yamnet/1'
    yamnet_model = hub.load(yamnet_model_handle)
    wave = load_wav_16k_mono(filename)
    _, yamnet_feat, _ = yamnet_model(wave)
    model_xgb = xgb.XGBClassifier()
    model_xgb.load_model("xgboost_model.json")
    preds = model_xgb.predict(yamnet_feat.numpy())
    print(preds)
    if sum(preds)>len(preds)/2:
        return 1
    else:
        return 0





@tf.function
def load_wav_16k_mono(file):
    """ Load a WAV file, convert it to a float tensor, resample to 16 kHz single-channel audio. """
    #file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(
          file,
          desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

def load_wav_for_map(filename, label, fold):
  return load_wav_16k_mono(filename), label, fold



uploaded_file = st.file_uploader("Choose a wav file ")
left_column, right_column = st.beta_columns(2)
pressed = left_column.button('Warning:')
if pressed:
    if not uploaded_file:
        right_column.write('Please, upload a file')
    else:
        label = predict(uploaded_file.getvalue())
        label_category = "Flooding Warning" if label==0 else "No Warning"
        right_column.write(f'{label_category}')

