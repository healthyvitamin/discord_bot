# discord_bot

此為一個簡單的discord機器人，可以做到一般聊天室機器人的功能(只要偵測用戶特定詞語做出回應即可達成)
，但主要的功能是播放音樂，與市面上一個免費的音樂機器人Groovy相比，只缺少了倒退歌曲、列印歌詞、隨機播放功能，詳見簡報與報告。

參考文獻&學習來源

Code a discord bot 架構主要來自於這裡
https://www.youtube.com/playlist?list=PLSCgthA1Anif1w6mKM3O6xlBGGypXtrtN

官方API文件，音樂的暫停、停止、恢復播放、音量是使用官方內建的函式
https://discordpy.readthedocs.io/en/latest/migrating.html?highlight=volume#voice-changes

Queue說明(asyncio的queue一樣)
https://docs.python.org/zh-cn/3.7/library/asyncio-queue.html

播放音樂的架構主要是參考這個
https://xbuba.com/questions/53605422

然而上面的程式過舊已不可使用，所以我發現以下網址的播放方法
https://stackoverflow.com/questions/56031159/discord-py-rewrite-what-is-the-source-for-youtubedl-to-play-music

以下網址用ctrl-F搜尋 EMBEDDING YOUTUBE-DL 可以發現youtube_dl的下載參數
https://github.com/ytdl-org/youtube-dl#options

 youtube_dl支援的網站
https://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md

ffmpeg可以放入自建的虛擬環境，將ffmpeg/bin下的三個檔案放入Scripts中即可
https://stackoom.com/question/256ip/%E6%89%BE%E4%B8%8D%E5%88%B0ffprobe%E6%88%96avprobe-%E8%AF%B7%E5%AE%89%E8%A3%85%E4%B8%80%E4%B8%AA

ffmpeg下載
https://www.ffmpeg.org/

PCM介紹
https://read01.com/zh-tw/3Q7Nd3.html#.Xgd_DkczaUk
