import os

import torchaudio

input_file_path = '../downloads/chadeeeeeeeeee5197139803.ogg'
output_folder = './wav_files_folder'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_file_path = os.path.join(output_folder, os.path.splitext(os.path.basename(input_file_path))[0] + '.wav')

waveform, sample_rate = torchaudio.load(input_file_path)

torchaudio.save(output_file_path, waveform, sample_rate)

print(f'Converted {input_file_path} to {output_file_path}')

import speech_recognition as sr


def recognize(audio_file):
    recognizer = sr.Recognizer()

    # Відкриваємо аудіофайл .wav
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:

            text_google = recognizer.recognize_google(audio_data, language="uk-UA")

            # Виводимо результат розпізнавання
            print("Розпізнаний текст (Google):", text_google)


        except sr.UnknownValueError:
            print("Не вдалося розпізнати мову.")
        except sr.RequestError as e:
            print(f"Помилка сервера розпізнавання: {e}")


for wav_file in os.listdir(output_folder):
    if wav_file.endswith('.wav'):
        recognize(os.path.join(output_folder, wav_file))
