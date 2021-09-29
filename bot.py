# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 11:45:12 2021

@author: Elkap
"""

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord_buttons_plugin import *
from chineeseCog import ChineeseGOV
import asyncio
import nest_asyncio
import sqlite3
import schedule

import json

nest_asyncio.apply()

load_dotenv()
TOKEN = open("token.txt","r").readline()

#----Prefix stuff
def get_prefix(my_client: commands.Bot, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
        
    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix=get_prefix)
#-----------
client.remove_command('help')

@client.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    
    prefixes[str(guild.id)] = "?"
    
    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)
        
    with open("channel.json", "r") as f:
        channel = json.load(f)
    
    channel[str(guild.id)] = guild.text_channels[0].id
    
    with open("channel.json", "w") as f:
        json.dump(channel, f)
        
client.add_cog(ChineeseGOV(client))

print("Bot Running !")
client.run(TOKEN)