import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
import json
import hashlib
import base64
from cryptography.fernet import Fernet
import qrcode
import io
import os
from datetime import datetime, timedelta
import sqlite3
import random
import string

# Configuration sécurisée
TOKEN = "VOTRE_TOKEN_DISCORD_ICI"
SERVER_ID = 123456789012345678  # ID de votre serveur
ADMIN_ROLES = ["Owner", "Admin"]
CRYPTO_WALLETS = {
    "BTC": "bc1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "XMR": "48jxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

# Base de données
DB_FILE = "task_bot.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# Initialisation DB
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    discord_id TEXT PRIMARY KEY,
    wallet_address TEXT,
    total_spent REAL DEFAULT 0,
    verified INTEGER DEFAULT 0,
    join_date TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    price_btc REAL,
    price_xmr REAL,
    download_url TEXT,
    password TEXT,
    stock INTEGER DEFAULT -1
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    tx_id TEXT PRIMARY KEY,
    user_id TEXT,
    product_id TEXT,
    amount REAL,
    currency TEXT,
    status TEXT,
    timestamp TEXT,
    delivery_code TEXT
)
''')

conn.commit()

# Chiffrement
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# Produits disponibles
PRODUCTS = {
    "RAT-001": {
        "name": "Remote Access Toolkit Pro",
        "price_btc": 0.005,
        "price_xmr": 8.5,
        "description": "RAT complet avec builder + crypteur FUD"
    },
    "EXPLOIT-002": {
        "name": "Windows 10/11 LPE Exploit",
        "price_btc": 0.015,
        "price_xmr": 25.0,
        "description": "Privilege Escalation 0-day"
    },
    "STEALER-003": {
        "name": "Stealer Multi-Platform",
        "price_btc": 0.003,
        "price_xmr": 5.0,
        "description": "Cookie/Password/Crypto Wallet stealer"
    }
}
