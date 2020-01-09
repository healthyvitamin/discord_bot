import discord
from discord.ext import commands
from core.classes import Cog_Extension
import json
import time,random

with open("setting.json", 'r', encoding='utf-8') as jFile:
    jdata = json.load(jFile)

class Event(Cog_Extension):

    #儲存所有對話紀錄
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(int(jdata['成員動態']))
        await channel.send(F'歡迎{member}大駕光臨!')
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(int(jdata['成員動態']))
        await channel.send(F'{member}已被剔除(゜皿。)')
    @commands.Cog.listener()
    async def on_message(self, msg):
        random_tex = random.choice(jdata['打招呼'])
        keyword = (jdata['觸發訊息'])
        tex = random_tex
        if msg.content in keyword and msg.author != self.bot.user:
            await msg.channel.send(tex)


def setup(bot):
    bot.add_cog(Event(bot))