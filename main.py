# -*- coding: UTF-8 -*-
import sys

import pandas as pd
import pandas
import pandas_gbq
from google.oauth2 import service_account
from telegram import Bot
import asyncio
import logging.handlers
import os
import logging
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import datetime
import configparser
import prettytable as pt


# Set up logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("\t\t\t\t ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
logger.info("\t\t\t Script Execution started for WebScrapping the Thangamayil Website to get current Gold Rates..\n\n")


def read_config():
    # Define the path to the config file
    config_file_path = os.path.join('config', 'config.ini')

    # Check if the config file exists
    if not os.path.exists(config_file_path):
        logger.error("\t\tConfig file NOT FOUND ,EXITING the code Execution ❌ ")
        sys.exit(98)

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    try:
        # Read the config file
        config.read(config_file_path)
        #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.get('bq','service_accnt_json_loc')
        os.environ["run_ts"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        logger.info("\t\tConfig file Exists and Read SUCCESSFULLY ✅ ")
        return config

    except configparser.Error as e:
        logger.error(f"Error reading config file: {e}")
        return None

def get_goldrates_scrapper(base_url):
    try:
        # Send an HTTP request with a User-Agent header
        logger.info(f"\t\tMake Request to the rate card webpage url : %s ", base_url)
        r = Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(r, timeout=10).read()

        # Parse the HTML content
        soup = BeautifulSoup(webpage, features="html.parser")

        # Extract gold rate elements
        rate_elements = []

        # Find all the necessary html attributes ot process the data
        for a in soup.findAll(attrs={'class': 'history-rate card'}):
            last_updated_ts = soup.find('h5').text.replace('Last updated on : ', '').strip()
            rate_elements.append(last_updated_ts)

            # Grab all he tags since the price resides on them
            logger.info("\t\tProcess <h2> HTML tags for gold and silver prices for the day..")
            price_elements = soup.findAll('h2')
            for item in price_elements[:-2]:
                rate_elements.append(str(item).replace("<h2>", "").replace("</h2>", "").replace('₹', ''))

            # Finally append the timestamp column as end of list element
            logger.info("\t\tCurrent day prices data : %s", rate_elements)
            rate_elements.append(os.environ.get("run_ts"))
            logger.info("\t\tWeb Scrapping completed SUCCESSFULLY ✅ \n\n")

        if not rate_elements:
            logger.error("\t\tNo Data is Extracted for Gold Rate from WebPage ❌ ")
            sys.exit(97)

        logger.info(f"STEP 2.1: DATA PREPARATION:")
        # Create a DataFrame
        df = pd.DataFrame([rate_elements],columns=['web_last_updated_ts','g_price_18k_gram','g_price_22k_gram','g_price_24k_gram','silver_price_gram','edw_publn_id'])

        # Convert data types
        logger.info("\t\tProcessing the prices for 18k,22k,24k gold anf silver prices.")
        df['web_last_updated_ts'] = pd.to_datetime(df['web_last_updated_ts'], format='%d/%m/%y %I:%M %p')
        df['g_price_18k_gram'] = pd.to_numeric(df['g_price_18k_gram'])
        df['g_price_22k_gram'] = pd.to_numeric(df['g_price_22k_gram'])
        df['g_price_24k_gram'] = pd.to_numeric(df['g_price_24k_gram'])
        df['silver_price_gram'] = pd.to_numeric(df['silver_price_gram'])
        df['edw_publn_id'] = pd.to_datetime(df['edw_publn_id'], format='%Y-%m-%d %H:%M')
        logger.info("\t\t" + df.to_string(index=False, col_space=4).replace('\n', '\n\t\t'))
        logger.info("\t\tData processing and Manupulation completed SUCCESSFULLY ✅ \n\n")
        return df

    except Exception as e:
        logger.error("\t\tERROR :%s in Webscraping and Data Preparation stage ❌ ",str(e))
        sys.exit(96)

def load_bq(src_df, project_id, dataset_id, table_id, write_mode):
    """
    Load a Pandas DataFrame to BigQuery.

    Parameters:
    - src_df: DataFrame, the source DataFrame to be loaded to BigQuery.
    - project_id: str, the BigQuery project ID.
    - dataset_id: str, the BigQuery dataset ID.
    - table_id: str, the BigQuery table ID.
    - if_exists: str, default 'append', whether to append, replace, or fail if the table exists.
    - SA_file : Service account Json file location
    Returns:
    - None
    """
    try:
        logger.info(f"\t\tLoading DataFrame to BigQuery: {project_id}.{dataset_id}{table_id}")
        # Ensure the 'src_df' parameter is a DataFrame
        if not isinstance(src_df, pd.DataFrame):
            raise ValueError("The 'src_df' parameter must be a Pandas DataFrame.")

        # Load the DataFrame to BigQuery
        pandas_gbq.to_gbq(src_df, f'{project_id}.{dataset_id}.{table_id}', project_id=project_id, if_exists=write_mode)
        logger.info("\t\tData load to EDW BQ completed SUCCESSFULLY ✅ \n\n")
    except Exception as e:
        logger.error("\t\tERROR :%s in EDW DATA LOAD ❌ ",str(e))
        sys.exit(96)


async def send_telegram_notifications(base_url,src_data):
    try:
        TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
        CHANNEL_ID = os.environ["CHANNEL_ID"]
    except KeyError:
        TELEGRAM_BOT_TOKEN = "Token not available!"
        CHANNEL_ID = "Channel ID not available!"
        logger.info("Token or CHANNEL ID not available!")
        raise

   # Initialize the Telegram bot
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Extract first two values
    updt_ts = src_data.at[0, 'web_last_updated_ts']
    g_22k_price = src_data.at[0, 'g_price_22k_gram']
    g_8g_price = int(g_22k_price) * 8
    g_40k_price = round(40000 / int(g_22k_price),3)

    message_text = f"📣 Gold Rate From {base_url} at {os.environ.get('run_ts')}"
    table = pt.PrettyTable([ 'updt_ts', 'g(22k)₹','8g ₹','40k'])
    table.align['updt_ts'] = 'l'
    table.align['g(22k) ₹'] = 'l'
    table.align['8g ₹'] = 'l'
    table.align['40k'] = 'r'
    table.add_row([ updt_ts ,  g_22k_price ,g_8g_price,g_40k_price ])

    combined_message = f"{message_text}\n\n<pre>{table}</pre>"
    await bot.send_message(chat_id=CHANNEL_ID, text=combined_message,parse_mode='HTML')


# Run the asynchronous function
if __name__ == '__main__':
    logger.info(f"STEP 1: CONFIG FILE EVALUATION:")
    config = read_config()
    if len(config.sections()) > 0:
        logger.info(f"\t\tCONFIG has sections: %s ",config.sections())
        logger.info("\t\tCONFIG File parsed SUCCESSFULLY ✅ \n\n")

        logger.info(f"STEP 2: WEB SCRAPING & DATA PREPARATION:")
        web_src_data = get_goldrates_scrapper(config.get('url','base_url'))

        logger.info(f"STEP 3: EDW DATA DUMP:")
        load_bq(web_src_data,config.get('bq','project_id'),config.get('bq','dataset_id'),config.get('bq','table_id'),'append')

        logger.info(f"STEP 4: SEND TELEGRAM NOTIFICATIONS:")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_telegram_notifications(config.get('url','base_url'),web_src_data))
        logger.info("\t\tTelegram Message sent SUCCESSFULLY ✅ \n\n")

    else:
        logger.error("\t\tConfig file is Empty ,EXITING the code Execution ❌ ")
        sys.exit(99)

