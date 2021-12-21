import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import os
import json
import aiohttp
import random
from dotenv import load_dotenv
from DB import Database
from ParseGames import Games_parse


intents = discord.Intents.all()


client = commands.Bot(command_prefix='!', intents=intents)
client.remove_command('help')

GUILD_WELCOME = 922396282637676567  # id of the main chat

database = Database()
parse = Games_parse()
g_parse = parse.games()
list_iter = 0

@client.event   # start of the program
async def on_ready():
    print('I`m ready\n')
    database.fill([member for member in client.get_all_members() if not member.bot])
    print('\nWe have logged in as {0.user}'.format(client))


@client.event   # dialog
async def on_message(message):
    if message.author == client.user:   # author verification
        return
    else:
        timer_lvl = database.new_message(str(message.author))
        if timer_lvl > 0:
            await message.channel.send(f'{message.author.mention} получает {timer_lvl} уровень!!!')

    # msg = message.content
    #
    # if msg.startswith('$hello'):
    #     await message.channel.send('Hello!')
    await client.process_commands(message)


@client.event   # Greetings
async def on_member_join(member):
    channelsadg = client.get_channel(GUILD_WELCOME)
    if database.connect(str(member)):
        await channelsadg.send(f'Привет, {member}! Ты попал в канал {member.guild.name}.')
    else:
        await channelsadg.send(f'С возвращением, {member}! Мы всегда рады видеть тебя у нас, в {member.guild.name}.')


@client.event   # Parting
async def on_member_remove(member):
    channelsadg = client.get_channel(GUILD_WELCOME)
    messages = await channelsadg.history(limit=1).flatten()
    if ('исключает' not in str(messages[0].content)) and ('забанен' not in str(messages[0].content)):
        await channelsadg.send(f'К сожалению, {member}, покидает наш канал.')


@client.command()   # giphy
async def giphy(ctx, *, search=None):
    embed = discord.Embed(colour=discord.Colour.blue())
    session = aiohttp.ClientSession()

    if search == None:
        response = await session.get('https://api.giphy.com/v1/gifs/random?api_key='+os.getenv('GIPHY'))
        data = json.loads(await response.text())
        embed.set_image(url=data['data']['images']['original']['url'])
    else:
        search.replace(' ', '+')
        response = await session.get('http://api.giphy.com/v1/gifs/search?q=' + search + '&api_key='+os.getenv('GIPHY')+'&limit=10')
        data = json.loads(await response.text())
        gif_choice = random.randint(0, 9)
        embed.set_image(url=data['data'][gif_choice]['images']['original']['url'])

    await session.close()
    await ctx.send(embed=embed)


@client.command()   # Help
async def help(ctx):
    author = ctx.message.author
    preview = f"""Здравствуй {author.mention}, мы приветствуем тебя на канале {author.guild.name}\n
Я UJ здешний бот\n
Мои команды:\n
!giphy 'поисковый запрос' - с помощью этой команды вы можете отправить любую gif с вашим поисковым запросом. Пример ''!giphy Brad Pitt'\n
!help - позволяет узнать мои команды\n
!kick 'Имя пользователя' - исключить пользователя(Имеет право только администратор) Пример '!kick qwerfsdg#7109'\n
!ban 'Имя пользователя' - забанить пользователя(Имеет право только администратор) Пример '!ban qwerfsdg#7109'\n
!unban 'Имя пользователя' - разбанить пользователя(Имеет право только администратор) Пример '!unban qwerfsdg#7109'\n
!ban_list - узнать пользователей в бане\n
!lvl_list - узнать список уровней\n
!listgames - Список игр на этом канале"""
    await ctx.send(preview)


@client.command()   # kick user
async def kick(ctx, member: discord.Member):
    if ctx.message.author.top_role.permissions.administrator:
        await ctx.send(f'{ctx.message.author.mention} исключает {member.mention}')
        await member.kick(reason=f'{ctx.message.author} исключает {member.mention}')
        Admin_kick = True
    else:
        await ctx.send(f'Простите, {ctx.message.author.mention}, но вы не можете это сделать, т.к. не являетесь администратором')


@client.command()   # ban user
async def ban(ctx, member: discord.Member):
    if ctx.message.author.top_role.permissions.administrator:
        await ctx.send(f'{member.mention} забанен')
        await member.ban(reason=f'{member.mention} забанен')
    else:
        await ctx.send(f'Простите, {ctx.message.author.mention}, но вы не можете это сделать, т.к. не являетесь администратором')


@client.command()   # unban user
async def unban(ctx, member = None):
    if ctx.message.author.top_role.permissions.administrator:
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} разбанен')
    else:
        await ctx.send(f'Простите, {ctx.message.author.mention}, но вы не можете это сделать, т.к. не являетесь администратором')


@client.command()   # banlist
async def ban_list(ctx):
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        await ctx.send(f'{user.mention} в бане')


@client.command()   # lvl_list
async def lvl_list(ctx):
    users, lvls = database.lvl_list()
    for user, lvl in zip(users, lvls):
        await ctx.send(f'У пользователя {str(user[0])} уровень = {str(lvl[0])}')


@client.event   # Handling Missing Arguments
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("""Что-то пошло не так, возможно команда была введена неправильно, попробуйте ещё раз\n
Для того чтобы посмотреть какие существуют команды воспользуйтесь !help""")


@client.command() # listgames
async def listgames(ctx):
    # embedVar = discord.Embed(title=f'{g_parse[list_iter]["name"]}', description=f'{g_parse[list_iter]["author"]}', color=0xffd800)
    # embedVar.set_image(url=f'{g_parse[list_iter]["image"]}')    #the image itself
    # embedVar.set_footer(text=f'Rating: {g_parse[list_iter]["rating"]}')   #image in icon_url

    pages = []
    for i in range(len(g_parse)):
        embedVar = discord.Embed(title=f'{g_parse[i]["name"]}', description=f'{g_parse[i]["author"]}', color=0xffd800)
        embedVar.set_image(url=f'{g_parse[i]["image"]}')    #the image itself
        embedVar.set_footer(text=f'Rating: {g_parse[i]["rating"]}')   #image in icon_url
        pages.append(embedVar)


    message = await ctx.send(embed = pages[0])
    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')

    def check(reaction, user):
        return user == ctx.author

    i = 0
    reaction = None

    while True:
        if str(reaction) == '⏮':
            i = 0
            await message.edit(embed = pages[i])
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '▶':
            if i < len(pages)-1:
                i += 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '⏭':
            i = len(pages)-1
            await message.edit(embed = pages[i])

        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 30.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()

load_dotenv()
client.run(os.getenv('TOKEN'))  # Running
