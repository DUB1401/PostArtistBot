# PostArtistBot
**PostArtistBot** – это бот Telegram с многоуровневым доступом для генерации иллюстраций к постам на основе нейросетей GPT-4 и SDXL-Lightning. 

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
"bot-token": ""
```
Сюда необходимо занести токен бота Telegram (можно получить у [BotFather](https://t.me/BotFather)).
___
```JSON
"hf-space": "AP123/SDXL-Lightning"
```
Здесь указывается пространство Gradio, использующееся для генерации иллюстраций. 
> [!NOTE]  
> По умолчанию используется беслпатное публичное пространство, однако оно имеет большое ограничения на частоту запросов. Чтобы уменьшить влияние данной проблемы, можно продублировать пространство для своего аккаунта и использовать его (требуется PRO-подписка для доступа к ZeroGPU).
___
```JSON
"hf-token": null
```
Токен аккаунта [Hugging Face](https://huggingface.co/) с абсолютными правами (все галочки в типе **Fine-graned** с указанием целевого пространства). Используется для управления личным пространством.
___
```JSON
"password": "1234"
```
Пароль для доступа к функциям бота.
___
```JSON
"admin-password": "5678"
```
Пароль для доступа к функциям бота в качестве администратора. Администраторы имеют доступ к командам: `/about`, `/admins`, `/password [STRING*]`.
___
```JSON
"start-message": ""
```
Приветственное сообщение в ответ на команду `/start`.
___

```JSON
"steps": 8
```
Указывает количество шагов обработки изображения. Поддерживает следующие значения: _1_, _2_, _4_, _8_.
___

```JSON
"describe-by-gpt": false
```
Включает обработку запросов при помощи модели GPT-4, которая будет составлять описание иллюстрации для повышения качества выдачи.
___

```JSON
"reboot-for-all-requests": false
```
Указывает, что пространство [Hugging Face](https://huggingface.co/) должно перезапускаться после каждого выполненного запроса.
___

```JSON
"parameters": []
```
Здесь можно указать список ключевых фраз, которые будут добавляться к запросам для их конкретизации. Необходимо использовать английский язык.

_Copyright © DUB1401. 2024._