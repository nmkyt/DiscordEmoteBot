import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import sqlite3

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Подключение к базе данных
conn = sqlite3.connect('reactions.db')
c = conn.cursor()

# Создание таблиц
c.execute(
    '''CREATE TABLE IF NOT EXISTS messages (message_id INTEGER PRIMARY KEY, correct_reaction TEXT, end_time TIMESTAMP)''')
c.execute(
    '''CREATE TABLE IF NOT EXISTS reactions (message_id INTEGER, user_id INTEGER, reaction TEXT, PRIMARY KEY (message_id, user_id))''')
c.execute('''CREATE TABLE IF NOT EXISTS scores (user_id INTEGER PRIMARY KEY, score INTEGER)''')
conn.commit()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_reactions.start()


@bot.command()
async def add_message(ctx, message_id: int, correct_reaction: str, duration: int):
    try:
        print(
            f'Command add_message invoked with message_id: {message_id}, correct_reaction: {correct_reaction}, duration: {duration}')
        end_time = datetime.utcnow() + timedelta(seconds=duration)
        c.execute("INSERT INTO messages (message_id, correct_reaction, end_time) VALUES (?, ?, ?)",
                  (message_id, correct_reaction, end_time))
        conn.commit()
        print('Message added to database')

        msg = await ctx.fetch_message(message_id)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        await ctx.send(f'Message {message_id} is now being tracked with a duration of {duration} seconds.')
        print('Reactions added to the message')
    except Exception as e:
        print(f'Error in add_message: {str(e)}')
        await ctx.send(f'Error: {str(e)}')


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message_id = reaction.message.id
    user_id = user.id
    emoji = str(reaction.emoji)

    try:
        c.execute("SELECT 1 FROM messages WHERE message_id = ?", (message_id,))
        if c.fetchone():
            print(f'Reaction {emoji} from user {user_id} on message {message_id} recorded')
            c.execute("INSERT OR REPLACE INTO reactions (message_id, user_id, reaction) VALUES (?, ?, ?)",
                      (message_id, user_id, emoji))
            conn.commit()
    except Exception as e:
        print(f'Error on reaction add: {str(e)}')


@tasks.loop(seconds=10)
async def check_reactions():
    now = datetime.utcnow()
    c.execute("SELECT message_id, correct_reaction FROM messages WHERE end_time <= ?", (now,))
    rows = c.fetchall()

    for message_id, correct_reaction in rows:
        try:
            c.execute("SELECT user_id, reaction FROM reactions WHERE message_id = ?", (message_id,))
            reactions = c.fetchall()
            for user_id, reaction in reactions:
                if reaction == correct_reaction:
                    c.execute("INSERT OR IGNORE INTO scores (user_id, score) VALUES (?, 0)", (user_id,))
                    c.execute("UPDATE scores SET score = score + 1 WHERE user_id = ?", (user_id,))

            c.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
            c.execute("DELETE FROM reactions WHERE message_id = ?", (message_id,))
            conn.commit()

            channel = bot.get_channel(1244694467265691699)  # Замените на ID канала
            message = await channel.fetch_message(message_id)
            await message.channel.send(
                f'Time is up! The correct reaction for message {message_id} was {correct_reaction}.')
        except Exception as e:
            print(f'Error in check_reactions: {str(e)}')


@bot.command()
async def score(ctx, user: discord.User = None):
    user = user or ctx.author
    try:
        c.execute("SELECT score FROM scores WHERE user_id = ?", (user.id,))
        score = c.fetchone()
        await ctx.send(f'{user.name} has {score[0] if score else 0} points.')
    except Exception as e:
        await ctx.send(f'Error: {str(e)}')


bot.run('ODY0Nzk3MDI5NjAyNjg5MDI0.YO6q_w.lkGk3xuabOk-r8fzN1p51mEK3dw')
