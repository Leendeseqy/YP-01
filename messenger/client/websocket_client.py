import websockets
import json
import asyncio
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal
from config import SERVER_HOST, SERVER_PORT

class MessengerWebSocket(QObject):
    message_received = pyqtSignal(dict)  # Сигнал для передачи сообщений в UI
    
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.ws = None
        self.reconnect_attempts = 0
        self.is_connected = False
        self.running = True
        self.server_host = SERVER_HOST  # Используем из конфига
        self.server_port = SERVER_PORT

    def connect(self):
        """Запускает WebSocket в отдельном потоке"""
        def websocket_thread():
            asyncio.run(self._websocket_listener())
        
        thread = Thread(target=websocket_thread, daemon=True)
        thread.start()

    async def _websocket_listener(self):
        """Основной цикл WebSocket"""
        while self.running and self.reconnect_attempts < 5:
            try:
                uri = f"ws://192.168.0.51:8000/ws/{self.user_id}"
                print(f"🔌 Connecting to WebSocket: {uri}")

                async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as websocket:
                    self.ws = websocket
                    self.is_connected = True
                    self.reconnect_attempts = 0
                    print("✅ WebSocket connected successfully")
                    
                    while self.running:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=30)
                            await self._handle_message(message)
                        except asyncio.TimeoutError:
                            # Отправляем ping для поддержания соединения
                            await websocket.send('ping')
                        except Exception as e:
                            print(f"⚠️ WebSocket receive error: {e}")
                            break
            except websockets.exceptions.InvalidURI:
                    print(f"❌ Invalid WebSocket URI: ws://{self.server_host}:{self.server_port}/ws/{self.user_id}")
                    break
            except ConnectionRefusedError:
                    print(f"❌ Connection refused to {self.server_host}:{self.server_port}")
                    self.is_connected = False
                    self.reconnect_attempts += 1
                    await asyncio.sleep(2)
            except Exception as e:
                    print(f"⚠️ WebSocket connection error: {e}")
                    self.is_connected = False
                    self.reconnect_attempts += 1
                    await asyncio.sleep(min(3000 * self.reconnect_attempts, 10000) / 1000)
                            
            except Exception as e:
                print(f"WebSocket connection error: {e}")
                self.is_connected = False
                self.reconnect_attempts += 1
                
                # Если разрыв соединения, отправляем статус оффлайн
                if self.reconnect_attempts >= 3:  # После 3 неудачных попыток
                    try:
                        # Попытка отправить статус оффлайн через HTTP
                        import requests
                        response = requests.post(
                            f"http://192.168.0.48:8000/auth/status",
                            json={"user_id": self.user_id, "is_online": False},
                            timeout=3
                        )
                    except:
                        pass
                
                await asyncio.sleep(min(3000 * self.reconnect_attempts, 10000) / 1000)

        # После завершения цикла устанавливаем статус оффлайн
        self._mark_user_offline()
        
    def _mark_user_offline(self):
        """Отметить пользователя как оффлайн"""
        try:
            import requests
            response = requests.post(
                f"http://192.168.0.51:8000/auth/status",
                json={"user_id": self.user_id, "is_online": False},
                timeout=3
            )
            print(f"📴 Marked user {self.user_id} as offline")
        except:
            print(f"⚠️ Failed to mark user {self.user_id} as offline")

    async def _handle_message(self, message):
        """Обработка входящих сообщений"""
        try:
            if message == 'pong':
                return
                
            data = json.loads(message)
            # Отправляем данные в UI через сигнал
            self.message_received.emit(data)
            
        except json.JSONDecodeError:
            print(f"Non-JSON message: {message}")
        except Exception as e:
            print(f"Error handling message: {e}")

    def send_message(self, data):
        """Отправка сообщения через WebSocket"""
        if self.is_connected and self.ws:
            asyncio.run(self._send_async(data))

    async def _send_async(self, data):
        """Асинхронная отправка сообщения"""
        try:
            await self.ws.send(json.dumps(data))
        except Exception as e:
            print(f"Error sending message: {e}")

    def disconnect(self):
        """Отключение WebSocket"""
        self.running = False
        if self.ws:
            asyncio.run(self.ws.close())