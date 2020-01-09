import discord
from discord.ext import commands
from core.classes import Cog_Extension
import json, asyncio, datetime, sqlite3, shutil, os, time

class Task(Cog_Extension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_task_counters = 0
        self.bg_task = self.bot.loop.create_task(self.time_task())

    async def time_task(self):
            await self.bot.wait_until_ready()
            with open("setting.json", 'r', encoding='utf-8') as jFile:
                jdata = json.load(jFile)
            self.channel = self.bot.get_channel(jdata['test_channel'])
            while not self.bot.is_closed():
                now_time = datetime.datetime.now().strftime("%H%M")
                with open('setting.json', 'r', encoding='utf-8') as JJ:
                    Godjj = json.load(JJ)
                if now_time == Godjj['指定排程'] and self.time_task_counters == 0:
                    await self.channel.send('汪汪汪汪!! 瘋狗動出沒')
                    self.time_task_counters = 1
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(1) #間隔用
                    pass

    async def record_task(self, num):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(60)
            with open("setting.json", 'r', encoding='utf-8') as jFile:
                jdata = json.load(jFile)
            now_time = datetime.datetime.now().strftime('%H%M')  # X小時X分才進行備份
            if now_time == jdata['time']:
                #在刪除舊有檔案前 把檔案備份至log資料夾------------------------------------------------------------------
                if not os.path.exists(".\\log"):  # 檢查有沒有log資料夾
                    os.mkdir(".\\log")
                with open('setting.json', 'r', encoding='utf-8-sig') as jFile:
                    jdata = json.load(jFile)
                cur_path = ("{}.db".format(time.strftime("%Y%m%d%H%M%S\
                            ", time.localtime())))
                shutil.copy("log.db", cur_path)
                shutil.move(cur_path, jdata['log_path'])
                #------------------------------------------------------------------
                try:
                    conn = sqlite3.connect('log.db')
                    conn.execute("DROP TABLE member")
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print("讀取失敗 原因: ", e)
                self.channel = self.bot.get_channel(648202897259233355)
                await self.channel.send("清除資料庫完成")

    @commands.command()
    async def cancel_rd_task(self, ctx):
        self.rd_task.cancel()
        await ctx.send(f'關閉背景任務') 
        
    @commands.command()
    async def create_rd_task(self, ctx, num: int):
        self.rd_task = self.bot.loop.create_task(self.record_task(num))

        await ctx.send(f'開始每隔{num}秒自動清除資料庫') 

    @commands.command()
    async def set_channel(self, ctx, ch: int):
        self.channel = self.bot.get_channel(ch)
        await ctx.send(f'Set Channel: {self.channel.mention}') #mention 標記功能

    @commands.command() #使用者可以指定排程
    async def set_time(self, ctx, time):
        self.counters = 0
        with open('setting.json', 'r', encoding='utf-8') as JJ:
            Godjj = json.load(JJ)
        Godjj['指定排程'] = time #使用者的資料傳入json裡
        with open('setting.json', 'w', encoding='utf-8') as JJ:
            json.dump(Godjj, JJ, indent=4)
        await ctx.send('排程設定成功')
    

def setup(bot):
    bot.add_cog(Task(bot))