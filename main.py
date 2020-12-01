import os
import re
import bs4
import urllib.request
from markdownify import markdownify as md
import discord
from discord.ext import commands
from discord import Embed
from typing import List, Tuple, Dict

bot = commands.Bot(command_prefix="!red")
comment_url_fmt = re.compile(
    r"https://(?:old)?.reddit.com/r/"
    r"(?P<subreddit>\w+)/comments/(?P<article_id>\w+)/(?P<title>\w+)/(?P<comment_id>\w+)/?(?:.*)"
)
subreddit_toplist_fmt = re.compile(r"https://(?:old)?.reddit.com/r/(?P<subreddit>\w+)/top/(?:.*)")


@bot.event
async def on_ready():
    print("Embeddit has entered chat; id: {0}".format(bot.user))


@bot.command(name='dit')
async def scrape(ctx, url: str):
    comment_request = comment_url_fmt.match(url)
    toplist_request = comment_url_fmt.match(url)
    if comment_request:
        await ctx.send(embed=parse_comment(url, comment_request))
    elif toplist_request:
        await ctx.send("Toplists not yet supported")
        # await ctx.send(embed=parse_toplist(url, toplist_request))
    else:
        await ctx.send("Unsupported URL")


def parse_comment(url: str, url_parts: re.Match) -> Embed:
    with urllib.request.urlopen(url) as response:
        contents = response.read()
    soup = bs4.BeautifulSoup(contents, 'html.parser')
    comment_div_id = "thing_t1_{}".format(url_parts.group('comment_id'))
    comment = soup.find("div", id=comment_div_id)
    content = comment.find("form").find("div").find("div", class_="md").contents[0]
    emb = Embed(title="Embeddit")
    # emb.set_thumbnail(url=bot.user.avatar_url)
    emb.add_field(name="Comment", value=content)  # TODO: improve content formatting; markdownify should do this
    emb.add_field(name="Subreddit", value=url_parts.group('subreddit'))
    emb.set_footer(text="[Link to thread]({})".format(url))
    return emb


def parse_toplist(soup: bs4.BeautifulSoup) -> Embed:
    pass


if __name__ == "__main__":
    DEBUGGING = False
    if DEBUGGING:
        test_url = "https://old.reddit.com/r/PrequelMemes/comments/k3vo6a/if_they_had_met_about_20_years_earlier/ge6w621/?context=3"
        comment_request = comment_url_fmt.match(test_url)
        if comment_request:
            parse_comment(test_url, comment_request)
    else:
        token = os.environ.get("EMBEDDIT_SECRET")
        bot.run(token)
