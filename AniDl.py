import asyncio, aiohttp, os
from Utils.File import convertFilePath
from Utils.TechZApi import TechZApi
from Utils.Downloader import startM3U8Download, resetCache
from Utils.FFmpeg import ConvertTsToMp4
from pyrogram import Client, filters

import requests




# Bot Configuration
API_ID = "21347898"  # Get it from my.telegram.org
API_HASH = "98caf2e4f0c25e142c3cbb2e36e683ef"  # Get it from my.telegram.org
BOT_TOKEN = "7399155876:AAHQl0wABCiCrHSWVVy-sewHdeJSsgUUErw"  # Get it from BotFather


app = Client("Anime_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


TechZApi = TechZApi()



search = TechZApi.gogo_search("kimetsu-no-yaiba-dub")
anime = search[0] 
title = anime.get("title")
anime = TechZApi.gogo_anime(anime.get("id"))["results"]
episodes = anime["episodes"]
ep_range = "*"
quality = "1080"


# Keep track of the progress while uploading
async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


def download_file(url, save_path):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        # Open the specified file in binary write mode and save the content
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


async def StartDownload():
  async with app:
    resetCache()
    try:
        os.mkdir(convertFilePath(f"./Downloads/{anime.get('name')}"))
    except:
        pass
    session = aiohttp.ClientSession()
    workers = 20
    for ep in episodes:
        episode_id = ep[1]
        ep = ep[0]
        try:
            anime['name']= anime['name'].replace("/", " ").replace("\\",' ')
            image = anime['image']
            data = TechZApi.gogo_episode(episode_id)["results"]
            file = data["stream"]["sources"][0]["file"]
            await startM3U8Download(session, file, quality, workers)
            download_file(image, 'thumb.png')
            filepath = convertFilePath(f"./Downloads/{anime.get('name')}/{anime.get('name')} - Episode {ep} - {quality}p.mp4")
            ConvertTsToMp4(filepath)
            resetCache()
            await app.send_document(1039959953,filepath,thumb="thumb.png",progress=progress)
            os.remove(filepath)
            os.remove("thumb.png")
        except Exception as e:
            print("Failed To Download Episode", ep)
            print("Error: ", e)
            continue
    await session.close()



app.run(StartDownload())
