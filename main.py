import discord 
import asyncio
import requests 
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)


