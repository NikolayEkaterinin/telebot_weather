import telegram
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters
import pyowm
from geopy.geocoders import Nominatim

# здесь нужно указать свой API-ключ от Telegram
bot = telegram.Bot(token='YOUR_TELEGRAM_API_KEY')

# здесь нужно указать свой API-ключ от OpenWeatherMap
owm = pyowm.OWM('YOUR_OPENWEATHERMAP_API_KEY')

# создаем геокодер для определения геопозиции по названию города
geolocator = Nominatim(user_agent="my-application")

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот погоды. Напиши мне название города или пришли свою геопозицию, чтобы узнать погоду.")

def weather(update, context):
    location = update.message.location
    if location:
        # если пользователь отправил геопозицию, используем ее для получения погоды
        weather_at_location(update, context, location.latitude, location.longitude)
    else:
        # иначе, пытаемся получить геопозицию по названию города
        city = update.message.text
        try:
            loc = geolocator.geocode(city)
            weather_at_location(update, context, loc.latitude, loc.longitude)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Я не смог найти город {city}. Попробуйте еще раз.")

def weather_at_location(update, context, latitude, longitude):
    observation = owm.weather_at_coords(latitude, longitude)
    w = observation.get_weather()
    temperature = w.get_temperature('celsius')['temp']
    status = w.get_detailed_status()
    location = geolocator.reverse(f"{latitude}, {longitude}").address
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Погода в {location}:\nТемпература: {temperature}°C\n{status}")

updater = Updater(token='YOUR_TELEGRAM_API_KEY', use_context=True)

start_handler = CommandHandler('start', start)
weather_handler = MessageHandler(Filters.location | (~Filters.command), weather)

updater.dispatcher.add_handler(start_handler)
updater.dispatcher.add_handler(weather_handler)

updater.start_polling()
