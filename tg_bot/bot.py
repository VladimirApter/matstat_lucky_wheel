import telebot
import os


# для разработки @test_matstat_lucky_wheel_bot, в проде токен будет браться из переменной окружения и бот будет @matstat_lucky_wheel_bot
BOT_TOKEN = os.getenv('MATSTAT_LUCKY_WHEEL_BOT_TOKEN', '7775515350:AAGL_P3-NY2ZCUmrEVnv6Ix-LVZ7hVVo7uc')
bot = telebot.TeleBot(BOT_TOKEN)

VIDEO_PATH = 'wheel_video_render/ft-204-1_wheel.mp4'

@bot.message_handler(commands=['start'])
def send_video_note(message):
    with open(VIDEO_PATH, 'rb') as video:
        print("видево отправляю")
        bot.send_video_note(message.chat.id, video, length=360)

print("Бот запущен...")
bot.polling()
