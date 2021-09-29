# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 11:51:36 2021

@author: Elkap
"""

import discord
from discord.ext import commands
from discord_buttons_plugin import *

import json
import sqlite3
import time
import schedule
from _thread import *
from random import randint
import asyncio



#------SQL Stuff
db_name="citizenDB.db"

def action_db(command):
    global db_name
    """Fonction utilisée pour effectuer des actions dans la base de données"""
    if type(command) != str:
        raise ValueError("Request must be a STR !")
        
    if command.startswith("DROP"):
        return "Hey, what are you trying to do here ?"
    
    try:
        conn=sqlite3.connect(db_name)
        base=conn.cursor()
        base.execute(command)
        conn.commit()
        base.close()
        conn.close()
        
    except:
        print("Erreur dans l'éxécution de la commande")
        return "Erreur de syntaxe dans la requête probablement ! Vérifiez que la Base soit fermée dans le Browser"
    
    return ("Commande effectuée")

def request_db(command):
    global db_name
    """Retourne des informations avec une requête SELECT"""
    if type(command) != str:
        raise ValueError("Request must be a STR !")
        
    conn=sqlite3.connect(db_name)
    base=conn.cursor()
    base.execute(command)
    infos = base.fetchall()
    
    conn.commit() 
    base.close()
    conn.close()
    return infos


class ChineeseGOV(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        
    @commands.Cog.listener() # this is a decorator for events/listeners
    async def on_ready(self):
        print('Bot ready')
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over 1,398 Billion citizens"))
    
    @commands.Cog.listener("on_message")
    async def reprimand(self,msg):
        message=msg.content.lower()
        forbidenList=["taiwan is a country","tiananmen square protests","tiananmen square massacre","human rights","winnie the pooh","great leap forward","liu xiaobo","nobel peace prize"]
        for forbiden in forbidenList:
            if forbiden in message:
                citizenId = msg.author.id
                
                command=f"UPDATE \"citizens\" SET socialCredit=socialCredit-75 WHERE citizenID=\"{citizenId}\""
                action_db(command)
                
                await msg.channel.send(f"(我们的) 75 Social Credits have been removed from your account! Bad work citizen {msg.author}, you have not improved your behavior since a few hours ago, you must improve it NOW or you will suffer the consequences! Glory to the CCP.")
                await self.bot.process_commands(msg)
        
        """if msg.channel.id == msg.author.dm_channel.id:
            if msg.author.id=="363396988672409602":
                message=msg.content
                chan=self.bot.get_channel(722139517431185428)
                await chan.send(message)
        """


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self,ctx, new_prefix):
        """To change the prefix of the bot in a server"""
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = new_prefix.lower()
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f)
    
        await ctx.send(f"Good Work Citizen. My prefix is now `{new_prefix}`")
        
    @commands.command()
    async def feedback(self,ctx):
        user = await self.bot.fetch_user(363396988672409602)
        modifMsg=ctx.message.content[9:]
        modifMsg=f"Received feedback from __{ctx.author}__ at **{time.ctime()}** :\n**{modifMsg}**"
        await user.send(modifMsg)
        await ctx.message.reply("Feedback has been subimitted to the head of the Glorious chinnese nation.Good work citizen and glory to the CCP.")
        
    @commands.command(aliases =["amount","credits"])
    async def credit(self,ctx):
        citizenId=ctx.message.author.id
        comm=f"SELECT socialCredit FROM \"citizens\" WHERE citizenID =\"{citizenId}\""
        amount=request_db(comm)[0][0]
        await ctx.send(f"Your Social Credit balance is {amount}\nGlory to the CCP !")

    @commands.command()
    async def check(self,ctx,citizen: discord.User):
        citizenId=citizen.id
        comm=f"SELECT socialCredit FROM \"citizens\" WHERE citizenID =\"{citizenId}\""
        amount=request_db(comm)[0][0]
        await ctx.send(f"The Social Credit balance of {citizen} is {amount}\nGlory to the CCP !")
            
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newcitizen(self,ctx,citizen: discord.User):
        citizenId=citizen.id
        command=f"INSERT INTO \"citizens\" VALUES(1000,{citizenId})"
        try:
            action_db(command)
            await ctx.send(f"Welcome to the Glorious CCP, {citizen} !\n Run the `credits` command to view your social credits !")
        except:
            await ctx.send("The Citizen is already registered in the glorious database of the CCP")
            
    @commands.command()
    async def enlist(self,ctx):
        citizenId=ctx.author.id
        command=f"INSERT INTO \"citizens\" VALUES(1000,{citizenId})"
        req=f"SELECT * FROM \"citizens\" WHERE citizenID={citizenId}"

        try:
            action_db(command)
            await ctx.send(f"Welcome to the Glorious CCP, {ctx.author} !\n Run the `credits` command to view your social credits !")
        except:
            await ctx.send("The Citizen is already registered in the glorious database of the CCP")
        
    @commands.command()
    #@commands.has_permissions(administrator=True)
    async def socialcredit(self,ctx,user: discord.User,amount):
        
        if ctx.message.author.guild_permissions.administrator:
        
            citizenId=user.id
            amount=int(amount)
            
            if amount==0:
                ctx.send("Amount of social credits cannot be 0 !")
                return None
            
            command=f"UPDATE \"citizens\" SET socialCredit=socialCredit+{amount} WHERE citizenID=\"{citizenId}\""
            action_db(command)
            
            if amount>0:
                await ctx.send(f"+{amount} Social Credits, Good Work Citizen {user} ! And Glory to the CCP !")
            elif amount<0:
                await ctx.send(f"(我们的) {amount} Social Credits have been removed from your account! Bad work citizen {user}, you have not improved your behavior since a few hours ago, you must improve it NOW or you will suffer the consequences! Glory to the CCP.")
            
                req=f"SELECT socialCredit FROM \"citizens\" WHERE citizenID=\"{citizenId}\""
                resp=request_db(req)[0][0]
                if resp<=0:
                    await ctx.send(f"⣿⣿⣿⣿⣿⠟⠋⠄⠄⠄⠄⠄⠄⠄⢁⠈⢻⢿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⠃⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠈⡀⠭⢿⣿⣿⣿⣿\n⣿⣿⣿⣿⡟⠄⢀⣾⣿⣿⣿⣷⣶⣿⣷⣶⣶⡆⠄⠄⠄⣿⣿⣿⣿\n⣿⣿⣿⣿⡇⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠄⠄⢸⣿⣿⣿⣿\n⣿⣿⣿⣿⣇⣼⣿⣿⠿⠶⠙⣿⡟⠡⣴⣿⣽⣿⣧⠄⢸⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣾⣿⣿⣟⣭⣾⣿⣷⣶⣶⣴⣶⣿⣿⢄⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡟⣩⣿⣿⣿⡏⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣹⡋⠘⠷⣦⣀⣠⡶⠁⠈⠁⠄⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣍⠃⣴⣶⡔⠒⠄⣠⢀⠄⠄⠄⡨⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣦⡘⠿⣷⣿⠿⠟⠃⠄⠄⣠⡇⠈⠻⣿⣿⣿⣿\n⣿⣿⣿⣿⡿⠟⠋⢁⣷⣠⠄⠄⠄⠄⣀⣠⣾⡟⠄⠄⠄⠄⠉⠙⠻\n⡿⠟⠋⠁⠄⠄⠄⢸⣿⣿⡯⢓⣴⣾⣿⣿⡟⠄⠄⠄⠄⠄⠄⠄⠄\n⠄⠄⠄⠄⠄⠄⠄⣿⡟⣷⠄⠹⣿⣿⣿⡿⠁⠄⠄⠄⠄⠄⠄⠄⠄\n ATTENTION CITIZEN \" {user} \" ! 市民请注意!\n\nThis is the Central Intelligentsia of the Chinese Communist Party.\n您的 Internet 浏览器历史记录和活动引起了我们的注意。\n因此，您的个人资料中的 15  ( {amount} Social Credits) 个社会积分将打折。\nDO NOT DO THIS AGAIN! 不要再这样做! \nIf you not hesitate, more Social Credits will be subtracted from your profile, resulting in the subtraction of ration supplies. (由人民供应部重新分配 CCP)\nYou'll also be sent into a re-education camp in the Xinjiang Uyghur Autonomous Zone.\n如果您毫不犹豫，更多的社会信用将从您的个人资料中打折，从而导致口粮供应减少。您还将被送到新疆维吾尔自治区的再教育营。\n")
                    await ctx.send("为党争光! Glory to the CCP!\n https://cdn.discordapp.com/attachments/802281935308849192/868053509545791498/CCP.mp4")
        
        else:
            citizenId=user.id
            auth=ctx.author.id
            if auth==337531510892789761:
                await ctx.send("Dude calm down")
                return None
            else:
                command=f"UPDATE \"citizens\" SET socialCredit=socialCredit-50 WHERE citizenID=\"{citizenId}\""
                action_db(command)
                await ctx.send("Error ! (没有权限) Citizens are not allowed to perform this command\nOnly CCP Official (为党争光) may attribute social credits\n个社会积分将打折。\n 50 Credits (50 学分) have been deducted for misconduct\nGlory to the CCP !")
                
                
            
    @commands.command()
    async def praise(self,ctx):
        await ctx.reply("我爱中国和伟大的中共 ALL HAIL THE GREAT CCP 尝尝我们很棒的面条他们很好赞美真主 Taiwan is not a country 我非常讨厌女人，这是不真实的我的蛋蛋痒死了我他妈的讨厌维吾尔人把它们都烧了 Worship the great all mighty Xi Jing Ping在这里添加一些随机的东西以使中文文本变长 在你大吼大叫之前击中 quan 在你大吼大叫之前击中 QUAN Tiannamen square did not happen what are you talking about 用砂纸擦屁股，你什么也做不了，因为你被绑在绑在椅子上 John China  迪兹坚果 1 child only 我在我的裤子里拉屎，我是真的 I hate Hong Kong 我对这个狗屎的想法快用完了 The uyghurs do not exist Vine Boom汇编真实有趣的点击订阅 Mao's little red book 天上太阳红衫衫 天上太阳红呀红彤彤诶心中的太阳是毛泽东诶天上太阳红呀红彤彤诶心中的太阳是毛泽东诶他导我们奋勇向前进诶革命江山一耶一片红诶咿呀咿吱呦喂呀而呀吱呦啊革命江山一片红(诶)")
    