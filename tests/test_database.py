import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.bot.database.models import Base
from src.bot.database.crud import get_history, save_message, clear_history
from src.bot.services.dialog_service import DialogService

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = session_maker()
    
    yield session
    
    await session.close()
    await engine.dispose()

@pytest.mark.asyncio
async def test_save_and_get_history(db_session):
    user_id = 12345
    await save_message(db_session, user_id, "user", "Как дела?")
    
    history = await get_history(db_session, user_id)
    
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Как дела?"

@pytest.mark.asyncio
async def test_clear_history(db_session):
    user_id = 12345
    await save_message(db_session, user_id, "user", "Сообщение 1")
    await save_message(db_session, user_id, "assistant", "Ответ 1")
    
    history = await get_history(db_session, user_id)
    assert len(history) == 2
    
    await clear_history(db_session, user_id)
    
    history = await get_history(db_session, user_id)
    assert len(history) == 0

@pytest.mark.asyncio
async def test_dialog_service_flow(db_session):
    user_id = 99999
    from unittest.mock import AsyncMock, patch
    from src.bot.services import openai_service
    
    fake_ai_response = "Я бот, у меня всё отлично!"
    user_message = "Привет, бот!"
    
    with patch.object(openai_service, 'generate_response', new=AsyncMock(return_value=fake_ai_response)):
        service = DialogService(db_session)
        response = await service.process_user_message(user_id, user_message)
        
        assert response == fake_ai_response
        
        history = await get_history(db_session, user_id)
        
        # Проверяем длину
        assert len(history) == 2
        
        # Проверяем наличие сообщений с правильными ролями и контентом
        # Не зависим от индекса, что надежнее
        user_msgs = [m for m in history if m['role'] == 'user']
        assistant_msgs = [m for m in history if m['role'] == 'assistant']
        
        assert len(user_msgs) == 1
        assert len(assistant_msgs) == 1
        
        assert user_msgs[0]['content'] == user_message
        assert assistant_msgs[0]['content'] == fake_ai_response
        
        # Дополнительно проверим порядок (пользователь должен быть первым)
        assert history[0]['role'] == 'user'
        assert history[1]['role'] == 'assistant'