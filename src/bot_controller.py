import asyncio
import threading
import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import models
from sqlalchemy.future import select
import gui
from tkinter import ttk
import customtkinter as ctk

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await calculation.start()


async def add_message(message_id: int, duration: int):
    try:
        print(
            f'Command add_message invoked with message_id: {message_id}, duration: {duration}')
        end_time = datetime.utcnow() + timedelta(seconds=duration)
        new_message = models.Message(message_id=message_id, end_time=end_time)
        models.session.add(new_message)
        models.session.commit()

    except Exception as e:
        print(f'Error in add_message: {str(e)}')


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message_id = reaction.message.id
    user_id = user.id
    emoji = str(reaction.emoji)

    try:
        if models.session.query(models.Message).filter_by(message_id=message_id).first():
            print(f'Reaction {emoji} from user {user_id} on message {message_id} recorded')
            new_reaction = models.session.query(models.Reaction).filter_by(message_id=message_id,
                                                                           user_id=user_id).first()
            if new_reaction:
                new_reaction.reaction = emoji
            else:
                new_reaction = models.Reaction(message_id=message_id, user_id=user_id, reaction=emoji)
            models.session.add(new_reaction)
            models.session.commit()
    except Exception as e:
        print(f'Error on reaction add: {str(e)}')


@tasks.loop(seconds=10)
async def calculation():
    now = datetime.utcnow()
    messages = models.session.query(models.Message).filter(models.Message.end_time <= now).all()

    for message in messages:
        try:
            reactions = models.session.query(models.Reaction).filter_by(message_id=message.message_id).all()
            print(message.correct_reaction)
            if message.correct_reaction is not None:
                for reaction in reactions:
                    if reaction.reaction == message.correct_reaction:
                        score = models.session.query(models.Score).filter_by(user_id=reaction.user_id).first()
                        if not score:
                            score = models.Score(user_id=reaction.user_id, score=1)
                        else:
                            score.score += 1
                        models.session.add(score)

                models.session.query(models.Reaction).filter_by(message_id=message.message_id).delete()
                models.session.query(models.Message).filter_by(message_id=message.message_id).delete()
                models.session.commit()

            else:
                return
        except Exception as e:
            print(f'Error in check_reactions: {str(e)}')


async def fill_correct_reaction(message_id, option):
    result = models.session.execute(select(models.Message).where(models.Message.message_id == message_id))
    message = result.scalar_one_or_none()

    if message:
        if option == 'Team 1':
            message.correct_reaction = '1️⃣'
            models.session.add(message)
            models.session.commit()
            print(f"Updated message {message_id} with new reaction.")
        elif option == 'Team 2':
            message.correct_reaction = '2️⃣'
            models.session.add(message)
            models.session.commit()
            print(f"Updated message {message_id} with new reaction.")
        else:
            print(f"No update made for option {option}.")
    else:
        print(f"Message with ID {message_id} not found.")


@bot.command()
async def score(ctx, user: discord.User = None):
    user = user or ctx.author
    try:
        score = models.session.query(models.Score).filter_by(user_id=user.id).first()
        await ctx.send(f'{user.name} has {score.score if score else 0} points.')
    except Exception as e:
        await ctx.send(f'Error: {str(e)}')


def process_input():
    global row_count

    value1 = gui.entry1.get()
    value2 = gui.entry2.get()
    asyncio.run(add_message(message_id=int(value1), duration=int(value2)))
    gui.entry1.delete(0, ctk.END)
    gui.entry2.delete(0, ctk.END)

    message_id_label = ttk.Label(gui.entries_frame, text=row_count)
    message_id_label.grid(row=row_count, column=0, padx=10, pady=5)

    duration_label = ttk.Label(gui.entries_frame, text=value2)
    duration_label.grid(row=row_count, column=1, padx=10, pady=5)

    option_var = ctk.StringVar(value="None")
    option_menu = ctk.CTkOptionMenu(gui.entries_frame, values=["None", "Team 1", "Team 2"], variable=option_var,
                                    command=lambda value: update_database(value1, value))
    option_menu.grid(row=row_count, column=2, padx=10, pady=5)

    row_count += 1


row_count = 1


def update_database(message_id, option):
    asyncio.run(fill_correct_reaction(message_id, option))


if __name__ == "__main__":
    gui = gui.botGUI

    # Run the bot in a separate thread to avoid blocking the GUI
    bot_thread = threading.Thread(target=lambda: bot.run('ENTER YOUR BOT TOKEN HERE'))
    bot_thread.start()

    gui.mainloop()
