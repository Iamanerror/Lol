import discord
import asyncio
import youtube_dl
import os
import colorsys
import logging
import typing
import json
import aiohttp
import requests
import string
import translate
from PIL import Image, ImageDraw, ImageFont, ImageOps
import discord, os, aiohttp
from io import BytesIO
import textwrap
import rethinkdb as r
import base64
import discord, datetime, time
from translate import Translator
from discord import Game, Embed, Color, Status, ChannelType
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions 
from discord.utils import get,find
from time import localtime, strftime
import requests as rq
import random

start_time = time.time()

def __init__(self, bot):
        self.bot = bot

async def __is_enabled(self, guild: int):
    if await r.table("imgwelcome").get(str(guild)).run(self.bot.r_conn):
        return True
    else:
        return False


with open("prefixes.json") as f:
    prefixes = json.load(f)
default_prefix = "t."

def prefix(bot, message):
    id = message.server.id
    return prefixes.get(id, default_prefix)

bot = commands.Bot(command_prefix=prefix)

@bot.command(name="prefix", pass_context=True)
@commands.has_permissions(administrator=True)
async def _prefix(ctx, new_prefix):
    # Do any validations you want to do
    prefixes[ctx.message.server.id] = new_prefix
    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)


@_prefix.error
async def prefix_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, you do not have a administrator permission to use this command.".format(ctx.message.author.mention)
		await bot.send_message(ctx.message.channel, text)	
	



async def status_task():
    while True:
        await bot.change_presence(game=discord.Game(name='>help', type=2))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name=str(len(set(bot.get_all_members())))+' users', type=3))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name=str(len(bot.servers))+' servers', type=3))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name='music'))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name='I need some vote;('))
        await asyncio.sleep(5)

	
@bot.event
async def on_ready():
   bot.loop.create_task(status_task())
   print(bot.user.name)
	
   print('Servers connected to:')
   for server in bot.servers:
        print(server.name)
	
	
	
	
@bot.command(pass_context=True)
async def info(ctx, user: discord.Member):
    embed = discord.Embed(title="{}'s info".format(user.name), description="Here's what I could find.", color=0xe67e22)
    embed.add_field(name="Name", value=user.name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Status", value=user.status, inline=True)
    embed.add_field(name="Highest role", value=user.top_role)
    embed.add_field(name="Joined", value=user.joined_at)
    embed.add_field(name="Created at", value=user.created_at)
    
    embed.add_field(name="nickname", value=user.nick)
    embed.add_field(name="Bot", value=user.bot)
    embed.set_thumbnail(url=user.avatar_url)
    await bot.say(embed=embed)	
	
	
@bot.command(pass_context=True)  
async def serverinfo(ctx):
    server = ctx.message.server
    roles = [x.name for x in server.role_hierarchy]
    role_length = len(roles)
    if role_length > 50: #Just in case there are too many roles...
        roles = roles[:50]
        roles.append('>>>> Displaying[50/%s] Roles'%len(roles))
    roles = ', '.join(roles);
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    online = len([m.status for m in server.members if m.status == discord.Status.online or m.status == discord.Status.idle])
    embed = discord.Embed(name="{} Server information".format(server.name), color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_thumbnail(url = server.icon_url)
    embed.add_field(name="Server name", value=server.name, inline=True)
    embed.add_field(name="Owner", value=server.owner.mention)
    embed.add_field(name="Server ID", value=server.id, inline=True)
    embed.add_field(name="Roles", value=len(server.roles), inline=True)
    embed.add_field(name="Members", value=len(server.members), inline=True)
    embed.add_field(name="Online", value=f"**{online}/{len(server.members)}**")
    embed.add_field(name="Created at", value=server.created_at.strftime("%d %b %Y %H:%M"))
    embed.add_field(name="Emojis", value=f"{len(server.emojis)}/100")
    embed.add_field(name="Server Region", value=str(server.region).title())
    embed.add_field(name="Total Channels", value=len(server.channels))
    embed.add_field(name="AFK Channel", value=str(server.afk_channel))
    embed.add_field(name="AFK Timeout", value=server.afk_timeout)
    embed.add_field(name="Verification Level", value=server.verification_level)
    embed.add_field(name="Roles {}".format(role_length), value = roles)
    await bot.send_message(ctx.message.channel, embed=embed)	
     
@bot.command(name="toggle")
async def imgwelcome_toggle(self, ctx):
        """Toggle on/off the imgwelcomer"""
        if await self.__is_enabled(ctx.guild.id):
            await r.table("imgwelcome").get(str(ctx.guild.id)).delete().run(self.bot.r_conn)
            await ctx.send("Disabled imgwelcoming")
        else:
            await r.table("imgwelcome").insert({
                "id": str(ctx.guild.id),
                "channel": str(ctx.channel.id),
                "content": "V2VsY29tZSB1c2VyIHRvIHNlcnZlciE="
            }).run(self.bot.r_conn)
            await ctx.send("Enabled imgwelcoming")

@bot.command(name="img")
async def imgwelcome_img(self, ctx):
        """Set the image"""
        if not await self.__is_enabled(ctx.guild.id):
            return await ctx.send("Enable imgwelcoming with n!imgwelcome toggle")

        if len(ctx.message.attachments) == 0:

            await ctx.send("Send an image or type anything without sending an image to reset back to default.")

            def check(m):
                return m.author == ctx.message.author and m.channel == ctx.message.channel

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=20)
            except:
                return await ctx.send("Timed out.")

        else:
            msg = ctx.message

        if len(msg.attachments) >= 1:
            attachment = str(msg.attachments[0].url).rpartition(".")[2]
            if attachment.lower() not in ["png", "jpg", "jpeg", "gif"]:
                return await ctx.send("Not a valid image type <:bakaa:432914537608380419>")
            if os.path.exists(f"data/imgwelcome/{ctx.guild.id}.png"):
                os.remove(f"data/imgwelcome/{ctx.guild.id}.png")
            try:
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(msg.attachments[0].url) as r:
                        imgdata = await r.read()
                img = Image.open(BytesIO(imgdata)).convert("RGBA").resize((500, 150))
                bg = Image.new("RGBA", (500, 150), (0, 0, 0, 0))
                bg.alpha_composite(img, (0, 0))
                bg.save(f"data/imgwelcome/{ctx.guild.id}.png")
                await ctx.send("Set image!")
            except Exception as e:
                await ctx.send("Failed to set image... `%s`" % e)
        else:
            if os.path.exists(f"data/imgwelcome/{ctx.guild.id}.png"):
                os.remove(f"data/imgwelcome/{ctx.guild.id}.png")
            await ctx.send("Reset Image.")

@bot.command(name="text")
async def imgwelcome_text(self, ctx, *, text: str):
        """Change the welcome text,
            user = the user's name
            server = the server's name
        Example:
            n!imgwelcome text Welcome user to server!
        """

        if not await self.__is_enabled(ctx.guild.id):
            return await ctx.send("Enable imgwelcoming with n!imgwelcome toggle")

        text = (base64.b64encode(text.encode("utf8"))).decode("utf8")
        await r.table("imgwelcome").get(str(ctx.guild.id)).update({"content": text}).run(self.bot.r_conn)
        await ctx.send("Updated text!")

@bot.command(name="channel")
async def imgwelcome_channel(self, ctx, channel: discord.TextChannel):
        """Select a channel to use for imgwelcoming, can be a channel mention or the exact name of it"""
        if not await self.__is_enabled(ctx.guild.id):
            return await ctx.send("Enable imgwelcoming with n!imgwelcome toggle")

        await r.table("imgwelcome").get(str(ctx.guild.id)).update({"channel": str(channel.id)}).run(self.bot.r_conn)
        await ctx.send("Updated to %s" % channel.name)


@bot.event
async def on_member_join(self, member):
        guild = member.guild

        try:
            if await r.table("autorole").get(str(guild.id)).run(self.bot.r_conn):
                data = await r.table("autorole").get(str(guild.id)).run(self.bot.r_conn)
                role = discord.utils.get(guild.roles, id=int(data["role"]))
                await member.add_roles(role, reason="Autorole")
        except:
            pass

        if not await self.__is_enabled(guild.id):
            return

        data = await r.table("imgwelcome").get(str(guild.id)).run(self.bot.r_conn)

        channel = self.bot.get_channel(int(data["channel"]))
        if not channel:
            return
        await channel.trigger_typing()

        if os.path.exists(f"data/imgwelcome/{guild.id}.png"):
            background = Image.open(f"data/imgwelcome/{guild.id}.png").convert("RGBA")
        else:
            background = Image.open("data/imgwelcome/transparent.png")

        async with aiohttp.ClientSession() as cs:
            async with cs.get(member.avatar_url_as(format="png")) as res:
                imgdata = await res.read()

        welcome_picture = ImageOps.fit(background, (500, 150), centering=(0.5, 0.5))
        welcome_picture.paste(background)
        welcome_picture = welcome_picture.resize((500, 150), Image.NEAREST)

        profile_area = Image.new("L", (512, 512), 0)
        draw = ImageDraw.Draw(profile_area)
        draw.ellipse(((0, 0), (512, 512)), fill=255)
        profile_area = profile_area.resize((128, 128), Image.ANTIALIAS)
        profile_picture = Image.open(BytesIO(imgdata))
        profile_area_output = ImageOps.fit(profile_picture, (128, 128), centering=(0, 0))
        profile_area_output.putalpha(profile_area)

        mask = Image.new('L', (512, 512), 0)
        draw_thumb = ImageDraw.Draw(mask)
        draw_thumb.ellipse((0, 0) + (512, 512), fill=255, outline=0)
        circle = Image.new("RGBA", (512, 512))
        draw_circle = ImageDraw.Draw(circle)
        draw_circle.ellipse([0, 0, 512, 512], fill=(255, 255, 255, 180), outline=(255, 255, 255, 250))
        circle_border_size = self._circle_border((128, 128))
        circle = circle.resize((circle_border_size), Image.ANTIALIAS)
        circle_mask = mask.resize((circle_border_size), Image.ANTIALIAS)
        circle_pos = (7 + int((136 - circle_border_size[0]) / 2))
        border_pos = (11 + int((136 - circle_border_size[0]) / 2))
        drawtwo = ImageDraw.Draw(welcome_picture)
        welcome_picture.paste(circle, (circle_pos, circle_pos), circle_mask)
        welcome_picture.paste(profile_area_output, (border_pos, border_pos), profile_area_output)

        uname = (str(member.name) + "#" + str(member.discriminator))

        def _outline(original_position: tuple, text: str, pixel_displacement: int, font, textoutline):
            op = original_position
            pd = pixel_displacement

            left = (op[0] - pd, op[1])
            right = (op[0] + pd, op[1])
            up = (op[0], op[1] - pd)
            down = (op[0], op[1] + pd)

            drawtwo.text(left, text, font=font, fill=(textoutline))
            drawtwo.text(right, text, font=font, fill=(textoutline))
            drawtwo.text(up, text, font=font, fill=(textoutline))
            drawtwo.text(down, text, font=font, fill=(textoutline))

            drawtwo.text(op, text, font=font, fill=(textoutline))

        welcome_font = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 50)

        _outline((150, 16), "Welcome", 1, welcome_font, (0, 0, 0, 255))
        drawtwo.text((150, 16), "Welcome", font=welcome_font, fill=(255, 255, 255, 230))
        name_font = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 30)
        name_font_medium = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 22)
        name_font_small = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 18)
        name_font_smallest = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 12)
        server_font = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 22)

        if len(uname) <= 17:
            _outline((152, 63), uname, 1, name_font, (0, 0, 0, 255))
            drawtwo.text((152, 63), uname, font=name_font, fill=(255, 255, 255, 230))

        if len(uname) > 17:
            if len(uname) <= 23:
                _outline((152, 66), uname, 1, name_font_medium, (0, 0, 0, 255))
                drawtwo.text((152, 66), uname, font=name_font_medium, fill=(255, 255, 255, 230))

        if len(uname) >= 24:
            if len(uname) <= 32:
                _outline((152, 70), uname, 1, name_font_small, (0, 0, 0, 255))
                drawtwo.text((152, 70), uname, font=name_font_small, fill=(255, 255, 255, 230))

        if len(uname) >= 33:
            drawtwo.text((152, 73), uname, 1, name_font_smallest, (0, 0, 0, 255))
            drawtwo.text((152, 73), uname, font=name_font_smallest, fill=(255, 255, 255, 230))

        server_text = "\n".join(textwrap.wrap(f"Welcome to {guild.name}!", 25))
        _outline((152, 100), server_text, 1, server_font, (0, 0, 0, 255))
        drawtwo.text((152, 100), server_text, font=server_font, fill=(255, 255, 255, 230))

        welcome_picture.save("data/welcome.png")

        try:
            content = ((base64.b64decode(str(data["content"]).encode("utf8"))).decode("utf8")).replace("user",
                                                                                                       member.name.replace(
                                                                                                           "@",
                                                                                                           "@\u200B")).replace(
                "server", guild.name)
        except:
            content = "Welcome %s to %s!" % (member.name.replace("@", "@\u200B"), guild.name)

        file = discord.File("data/welcome.png", filename="welcome.png")
        await channel.send(file=file, content=content)       




bot.run(os.environ['BOT_TOKEN'])
