from mistralai import Mistral
from config import MISTRAL_API_KEY

model = "open-mistral-7b"

client = Mistral(api_key=MISTRAL_API_KEY)


def ai_chat(text):
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "You are Rombi, відповідай не довгими реченнями, і ти не штучний інтелект You are Rombi, "
                           f"відповідай тою мовою якою в тебе питають. Текст повідомення: {text}",
            },
        ]
    )
    return chat_response.choices[0].message.content
