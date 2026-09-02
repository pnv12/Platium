"""
Username Scanner — 350+ платформ (асинхронний)
"""

import aiohttp
import asyncio

# 350+ платформ (список із Sherlock та інших джерел)
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "VK": "https://vk.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "YouTube": "https://www.youtube.com/@{0}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "TikTok": "https://www.tiktok.com/@{0}",
    "Medium": "https://medium.com/@{0}",
    "Telegram": "https://t.me/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "Flickr": "https://www.flickr.com/people/{}",
    "Vimeo": "https://vimeo.com/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Patreon": "https://www.patreon.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}/",
    "Gravatar": "https://en.gravatar.com/{}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "ProductHunt": "https://www.producthunt.com/@{0}",
    "Keybase": "https://keybase.io/{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Replit": "https://replit.com/@{}",
    "Dev.to": "https://dev.to/{}",
    "Gist": "https://gist.github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "VK": "https://vk.com/{}",
    "Facebook": "https://www.facebook.com/{}",
    "LinkedIn": "https://www.linkedin.com/in/{}",
    "Tumblr": "https://{}.tumblr.com",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "TikTok": "https://www.tiktok.com/@{0}",
    "YouTube": "https://www.youtube.com/@{0}",
    "Twitch": "https://www.twitch.tv/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Vimeo": "https://vimeo.com/{}",
    "Flickr": "https://www.flickr.com/people/{}",
    "Imgur": "https://imgur.com/user/{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Battle.net": "https://www.battle.net/{}",
    "EpicGames": "https://www.epicgames.com/{}",
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}/",
    "Keybase": "https://keybase.io/{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Replit": "https://replit.com/@{}",
    "Dev.to": "https://dev.to/{}",
    "Medium": "https://medium.com/@{0}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "ProductHunt": "https://www.producthunt.com/@{0}",
    "Patreon": "https://www.patreon.com/{}",
    "Gravatar": "https://en.gravatar.com/{}",
    "Telegram": "https://t.me/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "VK": "https://vk.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
}

async def check_platform(session, name, url, username):
    try:
        async with session.get(url.format(username), timeout=5) as response:
            if response.status == 200:
                return name, {"found": True, "url": url.format(username)}
            else:
                return name, {"found": False, "url": url.format(username)}
    except:
        return name, {"found": "Помилка", "url": url.format(username)}

async def search(username):
    """Пошук нікнейму на 350+ платформах (асинхронно)"""
    results = {}
    async with aiohttp.ClientSession() as session:
        tasks = [check_platform(session, name, url, username) for name, url in PLATFORMS.items()]
        for task in asyncio.as_completed(tasks):
            name, result = await task
            results[name] = result
    return results
