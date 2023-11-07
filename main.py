from telegram import Bot
import asyncio
import logging.handlers
import os
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import datetime
import prettytable as pt

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

# Your bot's API token
try:
    TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
except KeyError:
    TELEGRAM_BOT_TOKEN = "Token not available!"
    logger.info("Token not available!")
    raise

# Your channel ID
channel_id = '5500999973'  # Replace with your channel name or ID


async def send_message_to_channel():
    # Initialize the Telegram bot
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    base_url = "https://www.thangamayil.com/"

    r = Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
    if True:
        webpage = urlopen(r, timeout=10).read()
        soup = BeautifulSoup(webpage, features="html.parser")
        data_ele = []
        for a in soup.findAll(attrs={'class': 'today_rate hover'}) or soup.findAll(attrs={'class': 'gold-rate down'}):
            for b in a.findAll("span"):
                data_ele.append(str(b).replace("<span>", "").replace("</span>", "").strip())

    # Send a message to the channel
    data = str(datetime.datetime.now()) + '🚨' + "---> \n" + data_ele[9] + " ==> " + data_ele[1] + " ==> " + str(int(str(data_ele[1]).replace(",", "").replace("₹", "")) * 8)

    message_text = f"📣 Gold Rate From {base_url} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

    table = pt.PrettyTable([ 'updt_ts', 'g(22k)₹','8g ₹','40k'])
    table.align['updt_ts'] = 'l'
    table.align['g(22k) ₹'] = 'l'
    table.align['8g ₹'] = 'l'
    table.align['40k'] = 'r'
    table.add_row([ data_ele[9] ,  data_ele[1] ,str(int(str(data_ele[1]).replace(",", "").replace("₹", "")) * 8),round(40000/int(data_ele[1].replace("₹", "")),3) ])
    combined_message = f"{message_text}\n\n<pre>{table}</pre>"
    await bot.send_message(chat_id=channel_id, text=combined_message,parse_mode='HTML')

# Run the asynchronous function
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message_to_channel())