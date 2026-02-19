import asyncio

from src.bot.openai_servise import openai_service

async def test_generate():
    message = [{"role": "user", "content": "Привет! Как дела?"}]
    resonse = await openai_service.generate_responce(message)
    
    print(f'Ответ: {resonse}')
    
if __name__ == "__main__":
    asyncio.run(test_generate())