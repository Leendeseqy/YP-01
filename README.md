### ТЕСТОВАЯ ВЕТКА
# 📚 Учебная практика 2026
## Документация проекта "Локальный мессенджер для образовательных учреждений"

---

### 📋 Общая информация
- **Студент:** Малиневский Егор Сергеевич
- **Группа:** 21ИС-24
- **Учебный план:** [План учебной практики (УП.01)](./План%20УП.01.md) 
- **Дисциплина:** Моделирование программных продуктов
- **Преподаватель:** Бобошко Михаил Николаевич
- **Дата выполнения:** 19 января 2026

---

## 👥 Группа 21ИС-24

| Номер | ФИО студента | Ник-ссылка на репозиторий |
|-------|--------------|---------------------------|
| 1 | **Курносенко Александр Сергеевич** | [Alixandros](https://github.com/Alixandros/PKOvchinnikova_21IS_4semestr_Kyrnosenko.A.C) |
| 2 | **Ларетина Дарья Алексеевна** | [Al-Daria](https://github.com/Al-Daria/PKOvchinnikova_21IS_4semestr_Laretina) |
| 3 | **Малиневский Егор Сергеевич** | [Leendeseqy](https://github.com/Leendeseqy/PKOvchinnikova_21IS_4semestr_Malinevskiy) |
| 4 | **Микштас Артурас Мариусо** | [Mrkirk1](https://github.com/Mrkirk1/PKOvchinnikova_21IS_4semestr_Mikshtas) |
| 5 | **Мирошкин Егор Денисович** | [SWaT-137](https://github.com/SWaT-137/PKOvchinnikova_21IS_4semestr_Miroshkin) |
| 6 | **Поздняков Владимир Романович** | [Voviy-ux](https://github.com/Voviy-ux/PKOvchinnikova_21IS_PozdnyakovVR-main) |
| 7 | **Поздняков Дмитрий Романович** | [Mitya1606](https://github.com/Mitya1606/PKOvchinnikova_21IS_4semestr_PozdnyakovD) |
| 8 | **Полсачев Матвей Анатольевич** | [⏳В Процессе...⏳]() |
| 9 | **Рукас Вероника Олеговна** | [⏳В Процессе...⏳]() |
| 10 | **Силаков Максим Андреевич** | [Grozard](https://github.com/Grozard/PKOvchinnikova_21IS_4semestr_Silakov) |
| 11 | **Тараканова Андрей Андреевич** | [andreitar3](https://github.com/andreitar3/PKOvchinnikova_21IS_4semestr_Tarakanov) |
| 12 | **Удин Дмитрий Максимович** | [prostoflytre](https://github.com/prostoflytre/modelup) |
| 13 | **Фисенко Анна Андреевна** | [Fisai](https://github.com/Fisai/PKOvchinikova_21IS_4semestr_FisenkoAA) |
| 14 | **Шабанов Даниил Алексеевич** | [fertak08](https://github.com/fertak08/PKOvchinnikova_21IS_4semestr_Shabanov) |
| 15 | **Юхин Лавр Юрьевич** | [PananiXX](https://github.com/PananiXX/PKOvchinnikova_21IS_4semestr_Yukhin) |

---

```
📦 messenger/
├── 📄 requirements.txt                    # Зависимости проекта
│
├── 📁 client/                            # Клиентская часть
│   ├── 📄 main.py                        # Точка входа клиента
│   ├── 📄 config.py                      # Конфигурация клиента
│   ├── 📄 server_discovery.py            # Поиск серверов
│   ├── 📄 server_manager.py              # Управление серверами
│   ├── 📄 auth_manager.py                # Управление аутентификацией
│   │
│   ├── 📁 ui/                           # Пользовательский интерфейс
│   │   ├── 📄 server_browser_dialog.py   # Выбор сервера
│   │   ├── 📄 server_create_dialog.py    # Создание сервера
│   │   ├── 📄 login_dialog.py           # Авторизация
│   │   ├── 📄 main_window.py            # Главное окно
│   │   ├── 📄 chat_widget.py            # Виджет чата
│   │   └── 📄 settings_dialog.py        # Настройки (НОВЫЙ)
│   │
│   ├── 📁 models/                       # Модели данных
│   │   ├── 📄 message.py                # Модель сообщения
│   │   ├── 📄 user.py                   # Модель пользователя
│   │   └── 📄 server_info.py            # Модель сервера
│   │
│   ├── 📁 network/                      # Сетевой слой
│   │   ├── 📄 websocket_client.py       # WebSocket клиент
│   │   ├── 📄 broadcast_client.py       # Broadcast клиент
│   │   └── 📄 broadcast_server.py       # Broadcast сервер
│   │
│   ├── 📁 utils/                        # Утилиты (НОВАЯ ПАПКА)
│   │   ├── 📄 notifications.py          # Система уведомлений (НОВЫЙ)
│   │   └── 📄 theme_manager.py          # Менеджер тем (НОВЫЙ)
│   │
│   ├── 📁 icons/                        # Иконки приложения
│   └── 📁 sounds/                       # Звуковые файлы
│
└── 📁 server/                           # Серверная часть
    ├── 📄 main.py                       # Точка входа сервера
    ├── 📄 server_config.py              # Конфигурация сервера
    ├── 📄 server_auth.py                # Аутентификация сервера
    ├── 📄 websocket_manager.py          # Менеджер WebSocket
    ├── 📄 dependencies.py               # Зависимости
    ├── 📄 broadcast_server.py           # Broadcast сервер
    │
    ├── 📁 database/                     # Работа с БД
    │   ├── 📄 db.py                     # Инициализация БД
    │   ├── 📄 user_model.py             # Модель пользователя
    │   ├── 📄 message_model.py          # Модель сообщения
    │   └── 📄 models.py                 # Основные модели
    │
    ├── 📁 routers/                      # Маршруты API
    │   ├── 📄 auth.py                   # Аутентификация
    │   ├── 📄 messages.py               # Работа с сообщениями
    │   ├── 📄 users.py                  # Управление пользователями
    │   └── 📄 admin.py                  # Административные функции
    │
    └── 📁 schemas/                      # Pydantic схемы
        ├── 📄 user.py                   # Схемы пользователей
        └── 📄 message.py                # Схемы сообщений
```

*Исходный код мессенджера доступен по ссылке: https://github.com/Leendeseqy/PKOvchinnikova_21IS_4semestr_Malinevskiy*
