import io

import librosa
import soundfile as sf
import speech_recognition as sr
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


def recognize_speech(file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio, language='uk-UA')
        except sr.UnknownValueError:
            return "Не вдалося розпізнати мову"
        except sr.RequestError as e:
            return f"Помилка сервера розпізнавання: {e}"


@router.message(Command("voice"))
async def recognize_voice_command(message: Message, bot: Bot):
    await message.answer("Команда не працює. Причина: тех. роботи")
    if message.reply_to_message and message.reply_to_message.voice:
        file_info = await bot.get_file(message.reply_to_message.voice.file_id)
        voice_file = io.BytesIO()
        await bot.download_file(file_info.file_path, destination=voice_file)
        voice_file.seek(0)

        y, sr = librosa.load(voice_file, sr=16000)
        voice_file = io.BytesIO()
        sf.write(voice_file, y, sr, format='WAV', subtype='PCM_16')
        voice_file.seek(0)

        recognized_text = recognize_speech(voice_file)
        await message.reply(f"Розпізнаний текст: {recognized_text}")
    else:
        await message.reply("Будь ласка, використовуйте команду /voice у відповідь на голосове повідомлення.")
