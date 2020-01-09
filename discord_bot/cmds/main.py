import discord
from discord.ext import commands
from core.classes import Cog_Extension
import json, asyncio
import youtube_dl, os
import datetime, sqlite3, re
with open('setting.json', 'r', encoding='utf-8-sig') as jFile:
    jdata = json.load(jFile)
#Verbosity / Simulation Options:
songs = asyncio.Queue()  # 建立協程專用的queue (先進先出的儲存)
play_next_song = asyncio.Event()

#以下youtube下載的選項參數可以看https://github.com/ytdl-org/youtube-dl#options 的 EMBEDDING YOUTUBE-DL 部分
ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  #代表只下載音頻!
            'preferredcodec': 'mp3',
            'preferredquality': '300',
            }],
        }
ydl_opts_checklist = {
        'skip_download': True,  # 跳過下載
        'quiet': True,
        'no_warnings': True
        }
class Main(Cog_Extension):
#來自https://xbuba.com/questions/53605422--------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot.loop.create_task(self.audio_player_task())
        self.songs_Checklist = {}
        self.counter = 0  #紀錄目前音樂清單有多少歌 也用作songs_Checklist的鍵值
        self.bot.remove_command('help')  # 由於要重寫help資訊 原本的要remove掉

    def toggle_next(self, error):
        print("呼叫toggle_next")
        if os.path.isfile("./song.mp3"):  
            os.remove("./song.mp3")
        if os.path.isfile("./song.gz"):  
            os.remove("./song.gz")
        self.bot.loop.call_soon_threadsafe(play_next_song.set)

    async def audio_player_task(self):
        while True:
            play_next_song.clear()
            url = await songs.get()  # 等待queue是否有url可取得
            ##更新音樂清單---------------------------------------------------------------
            self.counter -= 1  #數量-1 (這樣下個用播放指令新增的音樂才會用正確的鍵值加入到音樂清單中)
            songs_Checklist_value = []  # 暫存清單用
            for key, value in self.songs_Checklist.items():  #將key2以後的取出 暫存起來
                if key == 1:
                    continue
                songs_Checklist_value.append(value)
            self.songs_Checklist.clear()  # 清空音樂清單
            for i, value in zip(list(range(1, self.counter+1)), songs_Checklist_value):  # 重新建立音樂清單
                self.songs_Checklist[i] = value
            #---------------------------------------------------------------
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:  #ydl_opts參數見上面
                if os.path.isfile("./song.mp3"):  # 我們會將要播放的音樂一直重複使用song.mp3 故要將前一個的刪除
                    os.remove("./song.mp3")
                song_info = ydl.extract_info(f"{url}", download=True)  # extract_info可取得影片的所有資訊 為一個字典 並且可選擇下載檔案
                self.file_name = song_info['title']
            for file in os.listdir("./"):  # 將音訊檔名改成song
                if file.endswith(".mp3"):
                    os.rename(file, 'song.mp3')
            # 將mp3檔轉換成PCM 需要安裝ffmpeg
            for i in self.bot.voice_clients:
                i.play(discord.FFmpegPCMAudio("song.mp3"), after=self.toggle_next)
                i.source = discord.PCMVolumeTransformer(i.source)
                i.source.volume = 0.7
            await play_next_song.wait()  #音樂播放完或中斷時after會呼叫toggle_next  將play_next_song的狀態改成set才會繼續執行
                                        #在官方文件中表示 after的函數一定要含有函數 error 才能執行
#--------------------------------------------------------------------------
    @commands.command()
    async def music_file(self, ctx):  # 將檔案上傳至discord聊天室 然而沒付費，只能上傳最大8MB的檔案 假如如果創頻的人有去升級就可以用了。
        try:
            await ctx.send(file=discord.File(fp="./song.mp3", filename=self.file_name))
        except:
            await ctx.send("音樂檔案過大，無法上傳")
            if os.path.isfile("./song.mp3"): 
                os.remove("./song.mp3")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(F'本柴的反應速度有({round(self.bot.latency*1000)})ms這麼快哦! d(`･∀･)b')


    @commands.command()
    async def connect(self, ctx):
        channel = self.bot.get_channel(int(jdata['music_channel']))
        #await ctx.send(channel.id)
        try:
            self.voice_client = await channel.connect()
        # Code below this e.g.
            if not self.voice_client.is_connected():
                print(f"Not connected to {channel.name}")
        except asyncio.TimeoutError:
            print(f'Connecting to channel: <{channel}> timed out.')
        except discord.ClientException:
            print("You are already connected to a voice channel.")
        except discord.opus.OpusNotLoaded:
            print("The opus library has not been loaded.")
        except discord.DiscordException as ex:
            print(ex)
    @commands.command()
    async def disconnect(self, ctx):
        for i in self.bot.voice_clients:
            await i.disconnect()
    @commands.command()
    async def play(self, ctx, url):
        if not self.bot.voice_clients:                  # 檢查語音頻道內是否有機器人
            await ctx.send("機器人還沒連上語音頻道")
            raise Exception("機器人還沒連上語音頻道")
        # 如果播放位於清單中的音樂會導致整個程式中斷 原因未知 所以將清單前的網址拿出來再放入queue中
        match = re.search(r'(.+)&list', url)
        if match:
            url = match.groups()[0]
        with youtube_dl.YoutubeDL(ydl_opts_checklist) as ydl:  # 將新來的音樂加入到音樂清單中 並且檢查時間是否大於10分鐘 避免大檔案下載過久
            song_info = ydl.extract_info(f"{url}")
            if song_info["duration"] > 601:
                await ctx.send("音樂:{}的時間大於十分鐘，無法播放".format(song_info["title"]))
                raise Exception("音樂:{}的時間大於十分鐘，無法播放".format(song_info["title"]))  # 中斷程式
            self.counter += 1
            self.songs_Checklist[self.counter] = song_info["title"]
        await songs.put(url)

    @commands.command()
    async def stop(self, ctx):
        for i in self.bot.voice_clients:
            i.stop()
    @commands.command()
    async def pause(self, ctx):
        for i in self.bot.voice_clients:
            i.pause()
    @commands.command()
    async def resume(self, ctx):
        for i in self.bot.voice_clients:
            i.resume()
    @commands.command()
    async def volume(self, ctx, num: float):
        for i in self.bot.voice_clients:
            i.source = discord.PCMVolumeTransformer(i.source)
            i.source.volume = 0.1  # num如果給0 之後就無法再設回有聲音(BUG?) 故這邊先給0.1再改
            i.source.volume = num
    @commands.command()
    async def jump(self, ctx, num: int):
        #處理queue 刪除要jump前的音樂----------------------------------------------
        songs_Temporary = []
        for i in range(songs.qsize()):  # 將queue全部拿出來成一個list
            songs_Temporary.append(await songs.get())
        
        if num > len(songs_Temporary) or num < 1:
            for k in songs_Temporary:  # 記的放回queue 否則queue就會直接清空了
                await songs.put(k)
            await ctx.send("不能jump超出索引範圍")
            raise Exception("不能jump超出索引範圍")

        songs_Temporary = songs_Temporary[num - 1:]
        for j in songs_Temporary:  #放回queue
            await songs.put(j)
        #處理音樂清單 刪除jump前的音樂---------------------------------------------
        self.counter -= num-1  # 刪除音樂數量  
        songs_Checklist_value = []  # 暫存清單用
        for key, value in self.songs_Checklist.items():  #將除了要刪除的value值全部取出 暫存起來
            if key < num:
                continue
            songs_Checklist_value.append(value)
        self.songs_Checklist.clear()  # 清空音樂清單
        for i, value in zip(list(range(1, self.counter+1)), songs_Checklist_value):  # 重新建立音樂清單
            self.songs_Checklist[i] = value
        #最後將音樂停下-------------------------------------------------
        for client in self.bot.voice_clients:
            client.stop()

    @commands.command()
    async def delete(self, ctx, num: str):  # 從音樂清單中刪除指定num音樂
    #判斷是否要範圍刪除----------------------------------------------------------
        match = re.search(r"([0-9]+)\~([0-9]+)", num)  # 匹配A~B
        final = []
        if match:
            match2 = []
            for i in match.groups():  # 將A、B放入list 這麼做是為了跟"刪除一個"做統一
                match2.append(int(i))
            if match2[0] >= match2[1]:  # 檢查大小
                await ctx.send("delete A~B，A必須大於B")
                raise Exception("delete A~B，A必須大於B")
            final = list(range(match2[0], match2[1] + 1))  # 注意 final是A~B的數量 如果queue中只有1 2 3 4 卻刪除3~6 
            #則self.counter會-4 導致最後音樂清單被刪掉 所以下面queue同時查看是否超出索引
        else:
            final.append(int(num))  # 與範圍刪除做統一 故雖然只要刪除一個也要放入list中
    #處理queue-----------------------------------------------------------------
        songs_Temporary = []
        for i in range(songs.qsize()):                 # 將queue全部拿出來成一個list
            songs_Temporary.append(await songs.get())
        # print(len(songs_Temporary),"final", final)
        for i in final:
            if i > len(songs_Temporary) or i < 1:
                for k in songs_Temporary:  # 記的放回queue 否則queue就會直接清空了
                    await songs.put(k)
                await ctx.send("不能delete超出索引範圍")
                raise Exception("不能delete超出索引範圍")

        if len(final) >= 2:
            del songs_Temporary[final[0] - 1:final[-1]]  # 根據索引刪除指定的音樂 要一次刪除 不能分次刪除(否則會刪到錯誤的索引)
        else:
            del songs_Temporary[final[0]]
        for k in songs_Temporary:  # 放回queue
            await songs.put(k)
    #更新音樂清單---------------------------------------------------------------
        self.counter -= len(final)  #音樂數量-要刪掉的數量
        songs_Checklist_value = []  # 暫存清單用
        for key, value in self.songs_Checklist.items():  #將除了要刪除的value值全部取出 暫存起來
            if key in final:
                continue
            songs_Checklist_value.append(value)
        self.songs_Checklist.clear()  # 清空音樂清單
        for i, value in zip(list(range(1, self.counter+1)), songs_Checklist_value):  # 重新建立音樂清單
            self.songs_Checklist[i] = value
    #---------------------------------------------------------------
    @commands.command()  #對調音樂
    async def swap(self, ctx, num1: str, num2: str):
    #判斷是否要範圍對調----------------------------------------------------------
        match_num1 = re.search(r"([0-9]+)\~([0-9]+)+", num1)  # 匹配A~B
        match_num2 = re.search(r"([0-9]+)\~([0-9]+)+", num2)
        final1 = []
        final2 = []
        if match_num1 or match_num2:
            if match_num1:
                match2_num1 = list(match_num1.groups())
            else:
                match2_num1 = [num1]
            if match_num2:
                match2_num2 = list(match_num2.groups())
            else:
                match2_num2 = [num2]
            match3_num1 = []
            match3_num2 = []
            for i in match2_num1:
                match3_num1.append(int(i))
            for i in match2_num2:
                match3_num2.append(int(i))
            if len(match3_num1) >= 2:  # 檢查數字是否有2個 有才需要檢查 否則 A~B 跟 C  C只有一個數字 沒有match3_num2[1]故會報錯
                if match3_num1[0] >= match3_num1[1]:  # 檢查大小
                    await ctx.send("swap A~B C~D，A必須大於B")
                    raise Exception("swap A~B C~D，A必須大於B")
                #final1 = list(range(match3_num1[0], match3_num1[1] + 1))
                final1 = match3_num1
            else:
                final1.append(int(num1))
            if len(match3_num2) >= 2:
                if match3_num2[0] >= match3_num2[1]:  # 檢查大小
                    await ctx.send("swap A~B C~D，C必須大於D")
                    raise Exception("swap A~B C~D，C必須大於D")
                final2 = match3_num2
            else:  # 數字只有一個 那就改放原本數字即可
                final2.append(int(num2))
        else:
            final1.append(int(num1)) 
            final2.append(int(num2))
        # print(final1, final2)
        for i in final1:  # 判斷範圍是否互衝到
            if i in final2:
                await ctx.send("A~D C~E C在A~D中 無法對調")
                raise Exception("A~D C~E C在A~D中 無法對調")
        if final1[0] > final2[0]:  #  [swap 3~4 1~2 前面大於後面時 會導致切成五等分不對 所以我乾脆在這邊將3~4與1~2對調
            final_swap = final1
            final1 = final2
            final2 = final_swap


    #處理queue-----------------------------------------------------------------
        songs_Temporary = []
        for i in range(songs.qsize()):  # 將queue全部拿出來成一個list
            songs_Temporary.append(await songs.get())
        
        for i in final1:
            if i < 1 or i > len(songs_Temporary):
                for k in songs_Temporary:  # 記的放回queue 否則queue就會直接清空了
                    await songs.put(k)
                await ctx.send("不能swap超出索引範圍")
                raise Exception("不能swap超出索引範圍")
        for j in final2:
            if j < 1 or j > len(songs_Temporary):
                for k in songs_Temporary:  # 記的放回queue 否則queue就會直接清空了
                    await songs.put(k)
                await ctx.send("不能swap超出索引範圍")
                raise Exception("不能swap超出索引範圍")

        if len(final1) >= 2:  # 將例如2,4 變成 2,3,4 而單一個的就維持不動
            final1_num = list(range(final1[0], final1[1] + 1))
        else:
            final1_num = final1
        if len(final2) >= 2:
            final2_num = list(range(final2[0], final2[1] + 1))
        else:
            final2_num = final2
        
        songs_Temporary_j1 = []  # 對調的方式 我選擇將整個list切成5等分 2 4是我們要對調的 1 3 5則是其他的 這樣就只需要最後重新堆疊起來即可
                                #原本用索引的方式過於麻煩
        songs_Temporary_j2 = []
        songs_Temporary_j3 = []
        songs_Temporary_j4 = []
        songs_Temporary_j5 = []

        for i in range(len(songs_Temporary)): 
            bang = i+1  # i是索引 所以要看真正的值要+1
            if bang < final1_num[0]:
                songs_Temporary_j1.append(songs_Temporary[i])
            elif bang in final1_num:
                songs_Temporary_j2.append(songs_Temporary[i])
            elif bang > final1_num[-1] and bang < final2_num[0]:
                songs_Temporary_j3.append(songs_Temporary[i])
            elif bang in final2_num:
                songs_Temporary_j4.append(songs_Temporary[i])
            elif bang > final2_num[-1]:
                songs_Temporary_j5.append(songs_Temporary[i])
        
        # print("j1取出:{} j2取出:{} j3取出:{} j4取出:{} j5取出:{}".format(songs_Temporary_j1, songs_Temporary_j2,
        # songs_Temporary_j3, songs_Temporary_j4, songs_Temporary_j5))

        # print("對調前", songs_Temporary)
        
        for i in songs_Temporary_j4:  # 2跟4要對調 因為要對調音樂順序
            songs_Temporary_j1.append(i)
        for i in songs_Temporary_j3:
            songs_Temporary_j1.append(i)
        for i in songs_Temporary_j2:
            songs_Temporary_j1.append(i)
        for i in songs_Temporary_j5:
            songs_Temporary_j1.append(i)

        songs_Temporary = songs_Temporary_j1
        # print("對調後",songs_Temporary)
        for k in songs_Temporary:  # 完成對調 放回queue
            await songs.put(k)
    #更新音樂清單---------------------------------------------------------------

        songs_Temporary_j1 = []
        songs_Temporary_j2 = []
        songs_Temporary_j3 = []
        songs_Temporary_j4 = []
        songs_Temporary_j5 = []
        for key, value in self.songs_Checklist.items():
            if (key in final1_num):
                songs_Temporary_j2.append(value)  # 同queue將要對調的值儲存起來
            elif (key in final2_num):
                songs_Temporary_j4.append(value)
            elif key < final1_num[0]:
                songs_Temporary_j1.append(value)
            elif key > final1_num[-1] and key < final2_num[0]:
                songs_Temporary_j3.append(value)
            elif key > final1_num[-1]:
                songs_Temporary_j5.append(value)
        #對調音樂
        for i in songs_Temporary_j4: 
            songs_Temporary_j1.append(i)
        for i in songs_Temporary_j3:
            songs_Temporary_j1.append(i)
        for i in songs_Temporary_j2:
            songs_Temporary_j1.append(i)
        for i in songs_Temporary_j5:
            songs_Temporary_j1.append(i)

        self.songs_Checklist.clear()
        for i, value in zip(list(range(1, self.counter+1)), songs_Temporary_j1):
            self.songs_Checklist[i] = value

    #---------------------------------------------------------------

    @commands.command()
    async def delete_all(self, ctx):
        for i in self.bot.voice_clients:
            for j in range(songs.qsize()):  # 先將queue排空
                await songs.get()
            i.stop()  # 再停止目前音樂
        self.songs_Checklist = {}
        self.counter = 0
    @commands.command()
    async def music_list(self, ctx):
        #queue要用list才能操作 http://hk.uwenku.com/question/p-fumrmlpx-ec.html
        songs_Checklist_str = ""
        for key, value in self.songs_Checklist.items():  # 再把字典拿出來用成字串 用於顯示
            songs_Checklist_str += ("{}. {}\n".format(key, value))
        if songs_Checklist_str == "":
            await ctx.send("目前沒有音樂在等候")
        else:
            await ctx.send(songs_Checklist_str)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="指令資訊", description="使用: 在指令前加入-", color=0xff0000)
        embed.add_field(name="play (url)", value="播放音樂，不可超過10分鐘", inline=False)
        embed.add_field(name='stop', value="停止播放當前音樂", inline=False)
        embed.add_field(name="pause", value="暫停播放當前音樂", inline=False)
        embed.add_field(name="resume", value="恢復播放當前音樂", inline=False)
        embed.add_field(name="volume (0.0~1.0)", value="設置目前音樂的音量大小", inline=False)
        embed.add_field(name="jump (A)", value="停止當前音樂並且跳到A音樂", inline=False)
        embed.add_field(name="swap (A/A~B) (C/C~D)", value="A跟C音樂對調，可範圍對調", inline=False)
        embed.add_field(name="delete (A/A~B)", value="刪除A音樂,可範圍刪除", inline=False)
        embed.add_field(name="delete_all", value="刪除音樂清單並停止播放當前音樂", inline=False)
        embed.add_field(name="music_list", value="取得音樂清單", inline=False)
        embed.add_field(name="connect", value="將機器人連線至音樂頻道", inline=False)
        embed.add_field(name="disconnect", value="將機器人中斷連結", inline=False)
        embed.add_field(name="clear (A)", value="刪除數量A行訊息", inline=False)
        embed.add_field(name="music_file", value="將目前音樂檔案上傳", inline=False)
        #---------------------------------------------------------
        embed.set_thumbnail(url="https://i.imgur.com/fIxDB9k.gif")
        embed.add_field(name="ping", value="查看柴柴的延遲(發呆)", inline=True)
        embed.add_field(name="安安", value="可以跟柴柴打招呼", inline=True)
        embed.add_field(name="開車", value="當有老司機發車可以使用", inline=True)
        embed.add_field(name="clean", value="可以刪除聊天內容,\n加上數字可以\n刪除指定行數\n(空格後再加)", inline=True)
        embed.add_field(name="saying", value="後面加入自己想說的話,\n可以讓柴柴幫你發話\n(空格後再加)", inline=True)
        embed.add_field(name="set_time", value="格式[1510]代表\n下午3點10分，\n指定時間發送訊息\n(空格後再加)", inline=True)
        embed.set_footer(text="現在時間" + datetime.datetime.now().strftime("%Y/%m/%d %H:%M"))
        #---------------------------------------------------------
        # embed.add_field(name="picture", value="機器人給你看一張優美的圖", inline=False)
        # embed.add_field(name="web", value="同上", inline=False)
        # embed.add_field(name="record", value="查看資料庫", inline=False)
        # embed.add_field(name="delete_record", value="刪除資料庫", inline=False)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def record(self, ctx, num: int):  #有時只能10筆 這是因為await ctx.send一次最多只能發送2000字
        bang = ""
        try:  # 依照時間讀取最後20筆log資料
            conn = sqlite3.connect('log.db')
            cursor = conn.execute("""select * from member order by \
                datetime desc limit {}""".format(num))
            rows = cursor.fetchall()
            for i in rows:
                bang += "{}\n".format(i)
            conn.close()
        except Exception as e:
            print("main讀取失敗 原因: ", e)
        if bang == "":
            await ctx.send("錯誤或資料庫中沒有資料")
        else:
            await ctx.send(bang)
    
    @commands.command()
    async def delete_record(self, ctx):
        try:
            conn = sqlite3.connect('log.db')
            conn.execute("DROP TABLE member")
            conn.commit()
            conn.close()
        except Exception as e:
            print("讀取失敗 原因: ", e)
    
def setup(bot):
    bot.add_cog(Main(bot))
