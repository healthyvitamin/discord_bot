import discord
from discord.ext import commands
from core.classes import Cog_Extension
import random
import json

with open('setting.json', 'r', encoding='utf-8-sig') as jFile:
    jdata = json.load(jFile)

class React(Cog_Extension):

    @commands.command()
    async def picture(self, ctx):
        random_pic = random.choice(jdata['pic'])
        pic = discord.File(random_pic)
        await ctx.send(file = pic)

    @commands.command()
    async def web(self, ctx):
        random_pic = random.choice(jdata['url_pic'])
        await ctx.send(random_pic)

    
    @commands.command()
    async def saying(self, ctx, *, msg): #前面的*能把後面的引數表示當使用者space時能夠繼續接收引數
        await ctx.message.delete()
        await ctx.send(msg)
    
    @commands.command()
    async def 開車(self, ctx):
        random_pic = random.choice(jdata['開車'])
        car = discord.File(random_pic)
        await ctx.send('也給本柴來一點ლ(́◕◞౪◟◕‵ლ)',file = car)
    @commands.command()
    async def 安安(self, ctx):
        random_tex = random.choice(jdata['打招呼'])
        tex = random_tex
        await ctx.send(tex)
    @commands.command()
    async def clean(self, ctx, num:int):
        await ctx.channel.purge(limit=num+1)

def setup(bot):
    bot.add_cog(React(bot))