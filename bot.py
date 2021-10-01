# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 11:45:12 2021

@author: Elkap
"""

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from chineeseCog import ChineeseGOV
import asyncio
import nest_asyncio
import sqlite3
import schedule

import json

nest_asyncio.apply()

load_dotenv()

#Really important
#Make sure you create the token.txt with your token
TOKEN = open("token.txt","r").readline()


#----Prefix stuff (borowed)
def get_prefix(my_client: commands.Bot, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
        
    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix=get_prefix)
#-----------

client.remove_command('help')

@client.event
async def on_guild_join(guild):
    """This function handles the prefixes on server join
    The bot needs to be online when joining a server for this code to work, 
    in the other case, the prefix will break and the bot will not work properly"""
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

#Start the Cog
client.add_cog(ChineeseGOV(client))

print("Bot Running !")
client.run(TOKEN)