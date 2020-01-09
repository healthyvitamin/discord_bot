# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 00:14:38 2019

@author: amd
"""
import discord
from discord.ext import commands
import json
import random
import os

with open("setting.json", 'r', encoding='utf-8') as jPile:
    jdata = json.load(jPile)#-['']

bot = commands.Bot(command_prefix='-')

@bot.event
async def on_ready():
    print(">>本柴已上線(･ω´･ )<<")

@bot.command()
async def load(ctx, extension):
    bot.load_extension(F'cmds.{extension}')
    await ctx.send(F'Loaded {extension} done.')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(F'cmds.{extension}')
    await ctx.send(F'Un - Loaded {extension} done.')

@bot.command()
async def reload(ctx, extension):
    if os.path.isfile("./song.mp3"):  # reload main時要刪除音樂檔案 否則會無法繼續播放(因已存在)
        os.remove("./song.mp3")
    bot.reload_extension(F'cmds.{extension}')
    await ctx.send(F'Re - Loaded {extension} done.')

for Filename in os.listdir('./cmds'): #列出資料夾下的所有文件
    if Filename.endswith('.py'):                    #結尾是.py才導入
        print(Filename)
        bot.load_extension(F'cmds.{Filename[:-3]}') #-3代表不拿".py"

if __name__ == '__main__':
    bot.run(jdata['TOKEN'])