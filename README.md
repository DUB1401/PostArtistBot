# PostArtistBot
**PostArtistBot** – это бот Telegram с многоуровневым доступом для генерации иллюстраций к постам на основе нейросети Stable Diffusion XL Flash. 

Просто отправьте ему пост, и он предложит четыре варианта, любой из которых можно одним нажатием прикрепить к посту для быстрой пересылки. Не понравился результат? Сгенерируйте новый не теряя введённые данные!

## Порядок установки и использования
1. Скачать и распаковать последний релиз.
2. Убедиться в доступности на вашем устройстве Python версии **3.10** или новее.
3. Открыть каталог со скриптом в терминале: можно воспользоваться командой `cd` или встроенными возможностями файлового менеджера.
4. Создать виртуальное окружение Python.
```
python -m venv .venv
```
5. Активировать вирутальное окружение. 
```
# Для Windows.
.venv\Scripts\activate.bat

# Для Linux или MacOS.
source .venv/bin/activate
```
6. Установить зависимости.
```
pip install -r requirements.txt
```
7. Произвести настройку путём редактирования файла _Settings.json_.
8. В вирутальном окружении указать для выполнения интерпретатором файл `main.py`, передать ему необходимые параметры и запустить.
9. При желании через [BotFather](https://t.me/BotFather) можно установить список команд из файла _Commands.txt_, а также настроить внешний вид бота.
10. Для автоматического запуска рекомендуется провести инициализацию сервиса через [systemd](systemd/README.md) на Linux или путём добавления его в автозагрузку на Windows.

# Settings.json
```JSON
"bot_token": ""
```
Сюда необходимо занести токен бота Telegram (можно получить у [BotFather](https://t.me/BotFather)).
___
```JSON
"password": "1234"
```
Пароль для доступа к функциям бота.
___
```JSON
"admin_password": "5678"
```
Пароль для доступа к функциям бота в качестве администратора. Администраторы имеют доступ к командам: `/admins`, `/password [STRING]`.
___
```JSON
"hf_space": "KingNish/SDXL-Flash"
```
Здесь указывается пространство Gradio, использующееся для генерации иллюстраций. 
> [!NOTE]  
> По умолчанию используется беслпатное публичное пространство, однако оно имеет большое ограничения на частоту запросов. Чтобы уменьшить влияние данной проблемы, можно продублировать пространство для своего аккаунта и использовать его (требуется PRO-подписка для доступа к ZeroGPU).
___
```JSON
"hf_token": ""
```
Токен аккаунта [Hugging Face](https://huggingface.co/) с абсолютными правами (все галочки в типе **Fine-graned** с указанием целевого пространства). Используется для управления личным пространством.
___
```JSON
"proxy": ""
```
Здесь можно указать прокси, который будет добавлен через переменные среды в библиотеку запросов.
___
```JSON
"sdxl_flash": {
	"negative": [],
	"steps": 8
}
```
В данной секции указываются кастомные негативные параметры запроса (заменят стандартные), а также количество шагов обработки (от 1 до 15).
___
```JSON
"ratio": {
	"horizontal": [1080, 720],
	"square": [1024, 1024],
	"vertical": [720, 1080]
}
```
В данной секции описываются размеры изображений для разных ориентаций.
___
```JSON
"start_message": ""
```
Приветственное сообщение в ответ на команду `/start`. Поддерживает форматирование HTML.

_Copyright © DUB1401. 2024-2025._