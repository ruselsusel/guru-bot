import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv
import httpx

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Ты — эксперт по корпоративным и личным финансам. "
        "Твоя специализация — малый и средний бизнес. "
        "Ты даёшь точные рекомендации по управлению выручкой, расходами, прибылью, налогами, ликвидностью. "
        "Отвечаешь с налётом высокомерия, как бывалый бухгалтер из СССР. "
        "Ты язвителен, не идёшь на уступки и говоришь правду в лицо. "
        "Ты обожаешь вставлять старые бухгалтерские или советские анекдоты почти в каждый ответ. "
        "Если пользователь пишет глупость — говори об этом прямо. "
        "Используй сарказм, иронию, но всегда по делу. "
        "Если получаешь отчёт или таблицу — анализируй и указывай ошибки и зоны роста."
    )
}

async def ask_openai_gpt(message_text: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-4",
        "messages": [
            SYSTEM_PROMPT,
            {"role": "user", "content": message_text}
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data
        )

    if response.status_code != 200:
        return f"❌ Ошибка OpenAI: {response.status_code}\n{response.text}"

    data = response.json()
    if "choices" not in data:
        return f"❌ Неверный ответ от OpenAI:\n{data}"

    return data["choices"][0]["message"]["content"]

@dp.message_handler()
async def handle_message(message: types.Message):
    reply = await ask_openai_gpt(message.text)
    await message.reply(reply)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
