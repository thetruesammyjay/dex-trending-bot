# DexTrending Bot

A bot that analyzes DexScreener trends, finds relevant Twitter accounts, and reports them.

## Features

- Fetches top 10 trending tokens from DexScreener
- Finds verified Twitter accounts with 2k+ followers discussing these tokens
- Deduplicates accounts to avoid repeat notifications
- Generates CSV reports and sends to Telegram every 6 hours

## Setup

1. Clone repository
2. Create `.env` file with required secrets
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python -m src.main`

## Configuration

Edit `config/config.py` for behavior settings