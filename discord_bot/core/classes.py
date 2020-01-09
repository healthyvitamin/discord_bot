import discord
import sqlite3, time
from discord.ext import commands
class Cog_Extension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_write(self, author, author_id, channel, channel_id, massage):
        try:  # 紀錄"帳號、時間、動作於log.db中"
            conn = sqlite3.connect('log.db')
            conn.execute("""create table if not exists member
                                        (
                                            author  char(25)  not null,
                                            author_id char(20) not null,
                                            channel char(20) not null,
                                            channel_id  char(20) not null,
                                            massage     char(50)  not null,
                                            datetime  char(10)   not null
                                        ); """)
            conn.execute("""insert into member(author, author_id,  channel, channel_id, massage, datetime)
                        values('{}', 'id:{}', '頻道:{}', 'id:{}', '訊息:{}', '時間:{}') """.format(author,
                        author_id, channel, channel_id, massage, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ))
            conn.commit()
            conn.close()
        except Exception as e:
            print("classes讀取失敗 原因: ", e)