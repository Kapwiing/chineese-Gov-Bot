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

#This file is the COG of the bot, essentially all the functions

#------SQL Stuff
#The Name of the .db file
#Used by action_db and request_db
db_name="citizenDB.db"

#Quick note :
#The social credits are spread through servers because the database stores only user ids
#The reason bhind that is primarly because Im fucking lazy but I will probably change it in the future

def action_db(command):
    global db_name
    """Function to act on the database with a failsafe (prevent any DROP of any kind)
    Failsafe can be removed by deleting the command.startswith(DROP) line
    This function is only meant to act on database, to interrogate the database, please refer to request_db instead"""
    if type(command) != str:
        raise ValueError("Request must be a STR !")
    
    #FAILSAFE
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
    """Returns information based on a SQL request
    This function is only meant to interrogate the database, to act on the databe, refer to action_db"""
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
        """Print when bot ready do do his stuff"""
        
        print('Bot ready')
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over 1,398 Billion citizens"))
    
    @commands.Cog.listener("on_message")
    async def reprimand(self,msg):
        """Reprimand citizen if bad word is detected
        Can be adapted into a reward mechanism by giving points instead of taking them"""
        
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
        """To change the prefix of the bot in a server
        User must be server Admin"""
        
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = new_prefix.lower()
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f)
    
        await ctx.send(f"Good Work Citizen. My prefix is now `{new_prefix}`")
        
    @commands.command()
    async def feedback(self,ctx):
        """Submit feedback
        feedback is sent directly to the user id (mine) but can be replaced with anyone's id"""
        
        user = await self.bot.fetch_user(363396988672409602)
        modifMsg=ctx.message.content[9:]
        modifMsg=f"Received feedback from __{ctx.author}__ at **{time.ctime()}** :\n**{modifMsg}**"
        await user.send(modifMsg)
        await ctx.message.reply("Feedback has been subimitted to the head of the Glorious chinnese nation.Good work citizen and glory to the CCP.")
        
    @commands.command(aliases =["amount","credits"])
    async def credit(self,ctx):
        """Function that can be called by any user to check its own balance
        The aliases can be changed of course"""
        
        citizenId=ctx.message.author.id
        comm=f"SELECT socialCredit FROM \"citizens\" WHERE citizenID =\"{citizenId}\""
        amount=request_db(comm)[0][0]
        await ctx.send(f"Your Social Credit balance is {amount}\nGlory to the CCP !")

    @commands.command()
    async def check(self,ctx,citizen: discord.User):
        """Check the balance of another user byt pinging him
        TODO: If no user is specified, display ctx.author balance"""
        
        citizenId=citizen.id
        comm=f"SELECT socialCredit FROM \"citizens\" WHERE citizenID =\"{citizenId}\""
        amount=request_db(comm)[0][0]
        await ctx.send(f"The Social Credit balance of {citizen} is {amount}\nGlory to the CCP !")
            
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newcitizen(self,ctx,citizen: discord.User):
        """Force Enlist a user by pinging him
        User must be server admin"""

        citizenId=citizen.id
        command=f"INSERT INTO \"citizens\" VALUES(1000,{citizenId})"
        try:
            action_db(command)
            await ctx.send(f"Welcome to the Glorious CCP, {citizen} !\n Run the `credits` command to view your social credits !")
        except:
            await ctx.send("The Citizen is already registered in the glorious database of the CCP")
            
    @commands.command()
    async def enlist(self,ctx):
        """Enlist a citizen into the database"""
        
        citizenId=ctx.author.id
        command=f"INSERT INTO \"citizens\" VALUES(1000,{citizenId})"
        req=f"SELECT * FROM \"citizens\" WHERE citizenID={citizenId}"

        try:
            #Greet the user if his not already in the database
            action_db(command)
            await ctx.send(f"Welcome to the Glorious CCP, {ctx.author} !\n Run the `credits` command to view your social credits !")
        except:
            await ctx.send("The Citizen is already registered in the glorious database of the CCP")
        
    @commands.command()
    #This line will come back on day
    #@commands.has_permissions(administrator=True)
    async def socialcredit(self,ctx,user: discord.User,amount):
        
        #if user is admin
        #Temporary, will eventually be replaced by a proper, cleaner function
        if ctx.message.author.guild_permissions.administrator:
        
            citizenId=user.id
            amount=int(amount)
            
            #Refuses to give 0 credits
            if amount==0:
                ctx.send("Amount of social credits cannot be 0 !")
                return None
            
            #Act on the DB
            command=f"UPDATE \"citizens\" SET socialCredit=socialCredit+{amount} WHERE citizenID=\"{citizenId}\""
            action_db(command)
            
            #If credits are being added, the bot compliments the citizen
            #Else, it reprimands him
            #If social credits go below 0, The Citizen is reminded of his low social credit score by a motivating message to become a better citizen
            if amount>0:
                await ctx.send(f"+{amount} Social Credits, Good Work Citizen {user} ! And Glory to the CCP !")
            elif amount<0:
                await ctx.send(f"(我们的) {amount} Social Credits have been removed from your account! Bad work citizen {user}, you have not improved your behavior since a few hours ago, you must improve it NOW or you will suffer the consequences! Glory to the CCP.")
            
                req=f"SELECT socialCredit FROM \"citizens\" WHERE citizenID=\"{citizenId}\""
                resp=request_db(req)[0][0]
                if resp<=0:
                    #Portrait of XiJinPing
                    await ctx.send(f"⣿⣿⣿⣿⣿⠟⠋⠄⠄⠄⠄⠄⠄⠄⢁⠈⢻⢿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⠃⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠈⡀⠭⢿⣿⣿⣿⣿\n⣿⣿⣿⣿⡟⠄⢀⣾⣿⣿⣿⣷⣶⣿⣷⣶⣶⡆⠄⠄⠄⣿⣿⣿⣿\n⣿⣿⣿⣿⡇⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠄⠄⢸⣿⣿⣿⣿\n⣿⣿⣿⣿⣇⣼⣿⣿⠿⠶⠙⣿⡟⠡⣴⣿⣽⣿⣧⠄⢸⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣾⣿⣿⣟⣭⣾⣿⣷⣶⣶⣴⣶⣿⣿⢄⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡟⣩⣿⣿⣿⡏⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣹⡋⠘⠷⣦⣀⣠⡶⠁⠈⠁⠄⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣍⠃⣴⣶⡔⠒⠄⣠⢀⠄⠄⠄⡨⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣦⡘⠿⣷⣿⠿⠟⠃⠄⠄⣠⡇⠈⠻⣿⣿⣿⣿\n⣿⣿⣿⣿⡿⠟⠋⢁⣷⣠⠄⠄⠄⠄⣀⣠⣾⡟⠄⠄⠄⠄⠉⠙⠻\n⡿⠟⠋⠁⠄⠄⠄⢸⣿⣿⡯⢓⣴⣾⣿⣿⡟⠄⠄⠄⠄⠄⠄⠄⠄\n⠄⠄⠄⠄⠄⠄⠄⣿⡟⣷⠄⠹⣿⣿⣿⡿⠁⠄⠄⠄⠄⠄⠄⠄⠄\n ATTENTION CITIZEN \" {user} \" ! 市民请注意!\n\nThis is the Central Intelligentsia of the Chinese Communist Party.\n您的 Internet 浏览器历史记录和活动引起了我们的注意。\n因此，您的个人资料中的 15  ( {amount} Social Credits) 个社会积分将打折。\nDO NOT DO THIS AGAIN! 不要再这样做! \nIf you not hesitate, more Social Credits will be subtracted from your profile, resulting in the subtraction of ration supplies. (由人民供应部重新分配 CCP)\nYou'll also be sent into a re-education camp in the Xinjiang Uyghur Autonomous Zone.\n如果您毫不犹豫，更多的社会信用将从您的个人资料中打折，从而导致口粮供应减少。您还将被送到新疆维吾尔自治区的再教育营。\n")
                    #Motivational message to strongly encourage the citizen to up his social Credit score
                    await ctx.send("为党争光! Glory to the CCP!\n https://cdn.discordapp.com/attachments/802281935308849192/868053509545791498/CCP.mp4")
        
        #else it removes social credits
        else:
            citizenId=user.id
            auth=ctx.author.id
            if auth==337531510892789761:
                # for the retard (ben)
                await ctx.send("Dude calm down")
                return None
            else:
                #If citizen tries to activate a command that he is not allowed to
                
                #Social credits to be deducted
                creditsToDeduct=50 #Default = 50
                
                command=f"UPDATE \"citizens\" SET socialCredit=socialCredit-{creditsToDeduct} WHERE citizenID=\"{citizenId}\""
                action_db(command)
                await ctx.send(f"Error ! (没有权限) Citizens are not allowed to perform this command\nOnly CCP Official (为党争光) may attribute social credits\n个社会积分将打折。\n {creditsToDeduct} Credits ({creditsToDeduct} 学分) have been deducted for misconduct\nGlory to the CCP !")
                
                
            
    @commands.command()
    async def praise(self,ctx):
        """Why the fuck did I add that
        what even is this"""
        
        await ctx.reply("我爱中国和伟大的中共 ALL HAIL THE GREAT CCP 尝尝我们很棒的面条他们很好赞美真主 Taiwan is not a country 我非常讨厌女人，这是不真实的我的蛋蛋痒死了我他妈的讨厌维吾尔人把它们都烧了 Worship the great all mighty Xi Jing Ping在这里添加一些随机的东西以使中文文本变长 在你大吼大叫之前击中 quan 在你大吼大叫之前击中 QUAN Tiannamen square did not happen what are you talking about 用砂纸擦屁股，你什么也做不了，因为你被绑在绑在椅子上 John China  迪兹坚果 1 child only 我在我的裤子里拉屎，我是真的 I hate Hong Kong 我对这个狗屎的想法快用完了 The uyghurs do not exist Vine Boom汇编真实有趣的点击订阅 Mao's little red book 天上太阳红衫衫 天上太阳红呀红彤彤诶心中的太阳是毛泽东诶天上太阳红呀红彤彤诶心中的太阳是毛泽东诶他导我们奋勇向前进诶革命江山一耶一片红诶咿呀咿吱呦喂呀而呀吱呦啊革命江山一片红(诶)")
    