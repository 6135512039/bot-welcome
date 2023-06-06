import discord
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import requests

TOKEN = 'YOUR_TOKEN'
DEFAULT_CHANNEL_ID = '0000000000000000000'
FONT_PATH = '/Users/kongkoms/Desktop/bot-welcome/fonts/ArialCE.ttf'

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

background_url = None
default_bg_url = 'https://wallpaper.dog/large/20512965.png'

async def send_image(channel, member, message):
    if background_url is None:
        await channel.send('Please set the background image using the command !setbg')
        return

    response = requests.get(background_url)
    if response.status_code != 200:
        response = requests.get(default_bg_url)
        if response.status_code != 200:
            await channel.send('Failed to download the background image')
            return

    background = Image.open(BytesIO(response.content))
    background = background.resize((1980, 1080))

    font_size = 100
    font_color = (255, 255, 255)
    font = ImageFont.truetype(FONT_PATH, size=font_size)

    text = f'{member.name} #{member.discriminator}'
    text_width, text_height = font.getsize(text)
    text_position = ((background.width - text_width) // 2, (background.height - text_height) // 2 + 300)

    draw = ImageDraw.Draw(background)
    draw.text(text_position, text, font=font, fill=font_color)

    avatar_url = member.avatar.url
    response = requests.get(avatar_url)
    if response.status_code == 200:
        avatar = Image.open(BytesIO(response.content))
        avatar_size = (512, 512)
        avatar = avatar.resize(avatar_size)

        mask = Image.new("L", avatar_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + avatar_size, fill=255)

        avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        avatar.putalpha(mask)

        avatar_position = ((background.width - avatar.width) // 2, (background.height - avatar.height) // 2 - 100)
        background.paste(avatar, avatar_position, avatar)

    temp_image_path = 'temp_image.png'
    background.save(temp_image_path)

    with open(temp_image_path, 'rb') as f:
        image_data = f.read()

    await channel.send(message, file=discord.File(BytesIO(image_data), filename='welcome_image.png'))

    os.remove(temp_image_path)

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    await bot.user.edit(username='Bot Welcome')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(int(DEFAULT_CHANNEL_ID))
    await send_image(channel, member, f'Welcome {member.mention}')

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(int(DEFAULT_CHANNEL_ID))
    await send_image(channel, member, f'Good Bye {member.mention}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!setbg'):
        global background_url
        background_url = message.content.split(' ')[1]
        await message.channel.send('Background image has been set')

    if message.content.startswith('!setchannelid') or message.content.startswith('!sci'):
        global DEFAULT_CHANNEL_ID
        DEFAULT_CHANNEL_ID = message.content.split(' ')[1]
        await message.channel.send('Default Channel ID has been set')

    if message.content.startswith('!changenamebot') or message.content.startswith('!cnb'):
        new_name = message.content.split(' ')[1]
        await bot.user.edit(username=new_name)
        await message.channel.send(f'Bot name has been changed to {new_name}')

bot.run(TOKEN)
