from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import init_db
from routers import auth, messages, users, admin
from fastapi import WebSocket, WebSocketDisconnect
from websocket_manager import manager
import asyncio
from database.user_model import UserModel

async def check_inactive_users_periodically():
    """Периодическая проверка неактивных пользователей"""
    while True:
        try:
            inactive_users = UserModel.check_inactive_users(timeout_minutes=1)
            if inactive_users:
                print(f"📴 Marked users as offline due to inactivity: {inactive_users}")
        except Exception as e:
            print(f"Error checking inactive users: {e}")
        
        await asyncio.sleep(60)  # Проверка каждую минуту

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы данных при запуске
    init_db()
    
    # Запускаем фоновую задачу для проверки неактивных пользователей
    task = asyncio.create_task(check_inactive_users_periodically())
    
    yield
    
    # Останавливаем задачу при остановке приложения
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы данных при запуске
    init_db()
    yield
    # Опционально: код для закрытия соединений при остановке

app = FastAPI(
    title="Local Messenger API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    print(f"🔌 WebSocket connection attempt from user {user_id}")
    await manager.connect(websocket, user_id)
    print(f"✅ User {user_id} connected to WebSocket")
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                print(f"📨 WebSocket message from user {user_id}: {data}")
                
                if data == 'ping':
                    await websocket.send_text('pong')
                elif data.startswith('{'):
                    try:
                        message_data = json.loads(data)
                        await manager.send_personal_message(message_data, user_id)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from user {user_id}")
            except WebSocketDisconnect:
                print(f"❌ User {user_id} disconnected")
                break
            except Exception as e:
                print(f"⚠️ WebSocket error for user {user_id}: {e}")
                break
                
    except WebSocketDisconnect:
        print(f"❌ User {user_id} WebSocket disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, user_id)
        print(f"📴 User {user_id} removed from WebSocket manager")
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.0.51", port=8000)