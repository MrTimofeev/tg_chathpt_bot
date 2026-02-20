import pytest
from unittest.mock import AsyncMock, patch
from src.bot.services.openai_service import OpenAIService

@pytest.fixture
def openai_service():
    return OpenAIService(
        api_key="test_key",
        base_url="https://test.url",
        model="gpt-3.5-turbo"
    )

@pytest.mark.asyncio
async def test_generate_response_success(openai_service):
    mock_choice = AsyncMock()
    mock_choice.message.content = "Это тестовый ответ от AI."
    
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    with patch.object(openai_service.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)):
        messages = [{"role": "user", "content": "Привет"}]
        response = await openai_service.generate_response(messages)
        
        assert response == "Это тестовый ответ от AI."

@pytest.mark.asyncio
async def test_generate_response_empty(openai_service):
    mock_choice = AsyncMock()
    mock_choice.message.content = None 
    
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    
    with patch.object(openai_service.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)):
        messages = [{"role": "user", "content": "Привет"}]
        response = await openai_service.generate_response(messages)
        
        assert "извините" in response.lower()
        assert "ответ" in response.lower()

@pytest.mark.asyncio
async def test_generate_response_rate_limit(openai_service):
    """Проверка обработки ошибки Rate Limit"""
    
    # Создаем обычное исключение с текстом, который содержит 'rate limit'
    # Это надежнее, чем конструировать сложный класс ошибки OpenAI
    class MockRateLimitError(Exception):
        def __str__(self):
            return "RateLimitError: Rate limit exceeded for requests"

    async def raise_error(*args, **kwargs):
        raise MockRateLimitError()

    with patch.object(openai_service.client.chat.completions, 'create', side_effect=raise_error):
        messages = [{"role": "user", "content": "Привет"}]
        response = await openai_service.generate_response(messages)
        
        assert "Слишком много запросов" in response