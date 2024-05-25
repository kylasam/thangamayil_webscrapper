# Gold Rate Telegram Bot

The Gold Rate Telegram Bot is a script that sends gold rate updates to a Telegram channel. It retrieves gold rate data from a specific website, formats it into a message, and sends it to a Telegram channel using the `python-telegram-bot` library. The entire process runs automatically via GitHub Actions on a cyclic schedule.

## Table of Contents
1. [Introduction](#introduction)
2. [Subscription](#subscription)
3. [GitHub Actions](#github-actions)
4. [Environment Variables](#environment-variables)
5. [Documentation](#documentation)

## Introduction <a name="introduction"></a>

The Gold Rate Telegram Bot is designed to provide regular updates on gold rates. It fetches data from a specific website and sends it to a dedicated Telegram channel.

## Subscription <a name="subscription"></a>

If you would like to receive regular updates on gold rates, please subscribe to our Telegram channel: [@ThangamayilGoldratesperHour](https://t.me/+dRZFgdLz3No0ZmY1).

## GitHub Actions <a name="github-actions"></a>

The entire process of fetching gold rate updates and sending them to the Telegram channel is automated using GitHub Actions. The script runs on a cyclic schedule, ensuring that you receive timely updates. It's a convenient way to stay informed about gold rate changes.

## Environment Variables <a name="environment-variables"></a>

Before you can run the Gold Rate Telegram Bot, you need to set up the following environment variables in your GitHub repository's secrets:

- **TELEGRAM_BOT_TOKEN**: Your Telegram bot's API token.
- **CHANNEL_ID**: The ID or username of the Telegram channel where you want to send updates.

Please set these environment variables as secrets in your GitHub repository's settings for the Gold Rate Telegram Bot to function correctly.


## Documentation <a name="documentation"></a>

For more detailed information about how the Gold Rate Telegram Bot works and the underlying code, you can refer to the [documentation](https://github.com/your-repo/documentation.md) on our GitHub repository.

NOTE:
KMS based encryption would be introduced sooner for this repo.

