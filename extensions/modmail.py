import lightbulb
import hikari
import json
import datetime
import aiosqlite
from .. import config
plugin = lightbulb.Plugin("modmail")

async def get_mail_by_user_id(user_id):
    db = await aiosqlite.connect("bot.db")
    sql = """SELECT * FROM modmail WHERE user_id=?"""
    cursor = await db.execute(sql, (user_id,))
    row = await cursor.fetchone()
    return row
async def get_mail_by_channel_id(channel_id):
    db = await aiosqlite.connect("bot.db")
    sql = """SELECT * FROM modmail WHERE channel_id=?"""
    cursor = await db.execute(sql, (channel_id,))
    row = await cursor.fetchone()
    return row

async def create_mail(user_id, channel_id):
    db = await aiosqlite.connect("bot.db")
    sql = """INSERT INTO modmail(user_id, channel_id) VALUES(?, ?) """
    await db.execute(sql, (user_id, channel_id))
    await db.commit()


async def delete_mail(channel_id):
    db = await aiosqlite.connect("bot.db")
    sql = """DELETE FROM modmail WHERE channel_id = ?"""
    await db.execute(sql, (channel_id,))
    await db.commit()

@plugin.command
@lightbulb.command("cmail", "Closes the modmail in the current channel")
@lightbulb.implements(lightbulb.SlashCommand)
async def Cmail(ctx: lightbulb.Context) -> None:
    row = await get_mail_by_channel_id(ctx.channel_id)
    if row:
        await delete_mail(ctx.channel_id)
        user = await ctx.bot.rest.fetch_user(row[0])
        dm = await user.fetch_dm_channel()
        await ctx.get_channel().delete()
        em = hikari.Embed(
            title="Staff has closed this modmail thread, if you still have any problem feel free to dm me",
            color=hikari.Colour.from_rgb(255, 0, 20),
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
        )
        guild = ctx.get_guild()
        em.set_footer(f"Staff", icon=guild.icon_url)
        await dm.send(embed=em)

    else:
        await ctx.respond("This channel is not a modmail thread")

    # f = open("modmails.json", "r")
    # mails = json.load(f)
    # m = mails.copy()
    # mails_channels = m.items()
    # for key, value in mails_channels:
    #     if value == f"{ctx.channel_id}":
    #         print(key)

    #         # await dm.send("Staff has closed this modmail thread, if you still have any problem feel free to dm me")
    #         channel = await ctx.bot.rest.fetch_channel(value)
    #         print(mails)
    #         print(mails[f"{key}"])
    #         mails.pop(f"{key}")

    #         await channel.delete()
    #         f = open("modmails.json", "w")
    #         json.dump(mails, f)
    #         f.close()
    #         return
    # await ctx.respond("Not a modmail thread")


@plugin.listener(hikari.GuildMessageCreateEvent)
async def onMessage(event: hikari.GuildMessageCreateEvent):
    if event.is_bot or not event.content:
        return
    row = await get_mail_by_channel_id(event.channel_id)
    print(row)
    if row:
        user = await  plugin.bot.rest.fetch_user(row[0])
        dm = await user.fetch_dm_channel()  
        em = hikari.Embed(
            title=event.message.content,
            color=hikari.Colour.from_rgb(0, 255, 20),
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
        )
        guild = event.get_guild()
        em.set_footer(f"Staff", icon=guild.icon_url)
        await dm.send(embed=em)

@plugin.listener(hikari.DMMessageCreateEvent)
async def onDM(event: hikari.DMMessageCreateEvent):
    if event.is_bot or not event.content:
        return

    row = await get_mail_by_user_id(event.author_id)
    guild = plugin.bot.cache.get_guild(927835307989159977)

    if row:
        channel = plugin.bot.cache.get_guild_channel(row[1])
    else:
        channel = await guild.create_text_channel(
             name=event.author_id,
             category=927841708392189963,
         )
        await create_mail(event.author_id, channel.id) 
    em = hikari.Embed(
        title=event.content,
        color=hikari.Colour.from_rgb(0, 255, 20),
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
    )
    em.set_footer(
        f"{event.author.username}#{event.author.discriminator}",
        icon=event.author.avatar_url,
    )
    await channel.send(embed=em)




def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)