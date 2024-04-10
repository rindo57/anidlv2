
import asyncio
import time
import aiohttp
import requests
import aiofiles
import sys

from main.modules.compressor import compress_video

from main.modules.utils import episode_linker, get_duration, get_epnum, status_text, get_filesize, b64_to_str, str_to_b64, send_media_and_reply, get_durationx

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from main.modules.uploader import upload_video
from main.modules.thumbnail import generate_thumbnail

import os

from main.modules.db import del_anime, save_uploads, is_fid_in_db, is_tit_in_db

from main.modules.downloader import downloader

from main.modules.anilist import get_anilist_data, get_anime_img, get_anime_name

from config import INDEX_USERNAME, UPLOADS_USERNAME, UPLOADS_ID, INDEX_ID, PROGRESS_ID, LINK_ID

from main import app, queue, status

from pyrogram.errors import FloodWait

from pyrogram import filters

from main.inline import button1

status: Message

async def tg_handler():

    while True:

        try:
            if len(queue) != 0:

                i = queue[0]  

                i = queue.pop(0)
                
                id, name, video = await start_uploading(i)
                print("Title: ", i["title"])
                await del_anime(i["title"])
                await save_uploads(i["title"])
                await asyncio.sleep(30)


            else:                

                if "Idle..." in status.text:

                    try:

                        await status.edit(await status_text("Idle..."))

                    except:

                        pass

                await asyncio.sleep(30)

                

        except FloodWait as e:

            flood_time = int(e.x) + 5

            try:

                await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

            except:

                pass

            await asyncio.sleep(flood_time)

        except:

            pass

            

async def start_uploading(data):

    try:

        title = data["title"]
        dbtit = data["title"]
        title = title.replace("Dr. Stone - New World", "Dr Stone New World")
        title = title.replace("Opus.COLORs", "Opus COLORs")
        title = title.replace(" Isekai wa Smartphone to Tomo ni. 2", " Isekai wa Smartphone to Tomo ni 2")
        title = title.replace("Stand My Heroes - Warmth of Memories - OVA", "Stand My Heroes Warmth of Memories - OVA")
        link = data["link"]
        size = data["size"]
        nyaasize = data["size"]
        subtitle = data["subtitle"]
        name, ext = title.split(".")

        name += f" [AniDL]." + ext

        KAYO_ID =  -1001373634390
        uj_id = 1159872623
        DATABASE_ID = -1001373634390
        bin_id = -1002062055380
        name = name.replace(f" [AniDL].","").replace(ext,"").strip()
        id, img, tit = await get_anime_img(get_anime_name(title))
        msg = await app.send_photo(bin_id,photo=img,caption=title)

        print("Downloading --> ",name)
        img, caption = await get_anilist_data(title)
        await asyncio.sleep(5)
        await status.edit(await status_text(f"Downloading {name}"),reply_markup=button1)
        file = await downloader(msg,link,size,title)

        await msg.edit(f"Download Complete : {name}")
        print("Encoding --> ",name)

        duration = get_duration(file)
        durationx = get_durationx(file)
        filed = os.path.basename(file)
        filed = filed.replace(filed[-14:], ".mkv")
        filed = filed.replace("[Erai-raws]", "[AniDL]")
        filed = filed.replace("[1080p][Multiple Subtitle]", "[1080p Web-DL]")
        filed = filed.replace("[1080p]", "[1080p Web-DL]")
        filed = filed.replace("2nd Season", "S2")
        filed = filed.replace("3rd Season", "S3")
        razo = filed.replace("[1080p Web-DL]", "[720p x265] @animxt")
        fpath = "downloads/" + filed
        ghostname = name
        ghostname = ghostname.replace("[1080p][Multiple Subtitle]", "")
        ghostname = ghostname.replace("[1080p]", "")
        ghostname = ghostname.replace("2nd Season", "S2")
        ghostname = ghostname.replace("3rd Season", "S3")
        subtitle = subtitle.replace("][", ", ")
        subtitle = subtitle.replace("[", "")
        subtitle = subtitle.replace("]", "")     
        subtitle = subtitle.replace("ENG", "English")
        subtitle = subtitle.replace("POR-BR", "Portuguese (Brazil)")
        subtitle = subtitle.replace("SPA-LA", "Spanish (Latin America)")
        subtitle = subtitle.replace("SPA", "Spanish")
        subtitle = subtitle.replace("ARA", "Arabic")
        subtitle = subtitle.replace("FRE", "French")
        subtitle = subtitle.replace("GER", "German")
        subtitle = subtitle.replace("ITA", "Italian")
        subtitle = subtitle.replace("RUS", "Russian")
        subtitle = subtitle.replace("HIN", "Hindi")
        subtitle = subtitle.replace("RUM", "Romanian")
        subtitle = subtitle.replace("FIN", "Finnish")
        subtitle = subtitle.replace("MAY", "Malaysian")
        subtitle = subtitle.replace("SWE", "Swedish")
        subtitle = subtitle.replace("GRE", "Greek")
        subtitle = subtitle.replace("HEB", "Hebrew")
        subtitle = subtitle.replace("1080p, 95972F57.mkv", "English")
        subtitle = subtitle.replace("JPN", "Japanese")
        subtitle = subtitle.replace("POL", "Polish")
        subtitle = subtitle.replace("DUT", "Dutch")
        subtitle = subtitle.replace("FIL", "Filipino")
        subtitle = subtitle.replace("CES", "Czech")
        subtitle = subtitle.replace("HRV", "Croatian")
        subtitle = subtitle.replace("HUN", "Hungarian")
        subtitle = subtitle.replace("UKR", "Ukranian")
    
        os.rename(fpath,"video.mkv")
        await asyncio.sleep(5)
        main = await app.send_photo(KAYO_ID,photo=img, caption=title)
        compressed = await compress_video(duration,main,name)
    

        if compressed == "None" or compressed == None:

            print("Encoding Failed Uploading The Original File")

            os.rename("video.mkv",fpath)

        else:

            os.rename("out.mkv",fpath)
  
        print("Uploading --> ",name)
        video = await upload_video(msg,fpath,id,tit,name,size,main,subtitle,nyaasize)


        try:

            os.remove("video.mkv")

            os.remove("out.mkv")

            os.remove(file)

            os.remove(fpath)
        except:

            pass     

    except FloodWait as e:

        flood_time = int(e.x) + 5

        try:

            await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

        except:

            pass

        await asyncio.sleep(flood_time)
        
    return id, name, video

    
