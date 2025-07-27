from collections import Counter
import os
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters 
from dotenv import load_dotenv
load_dotenv()
import json

with open('data/jobs.json', 'r') as file:
    jobs_data = json.load(file)

TOKEN: Final[str] = os.getenv("Token")
BOT_USERNAME: Final[str] = os.getenv("BOT_USERNAME")

# Extract all expertise mentions
expertise_list = []
for job in jobs_data:
    expertise_list.extend(job['expertise'])

# Count the occurrences of each expertise
expertise_counter = Counter(expertise_list)

# Sort expertise by popularity (descending order)
sorted_expertise = expertise_counter.most_common()


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Hey i am the nate bot"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"i am a nate emulator, start typing something to me and i will reply with a random message"
    )

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"this is a custom command"
    )

async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    jobs = []
    args = context.args
    if not args:
        await update.message.reply_text(
            "Please provide a job title or keyword."
        )
        return
    
    for job in jobs_data:
        if any(expertise in args for expertise in job['expertise']):
            jobs.append(job)
    if not jobs:
        await update.message.reply_text(
            "No jobs found matching your criteria."
        )
        return
    


    if jobs:
        for job in jobs:
            job_text = (
                f"🏢 <b>{job['title'].title()}</b> at <b>{job['company'].title()}</b>\n"
                f"🌍 Location: {job['location'].title()}\n"
                f"💼 Expertise: {', '.join(job['expertise'])}\n"
                f"💰 Salary: {job['salary']}\n"
                f"🔗 Source: {job['source'].title()}\n"
                f"🆔 Job ID: {job['id']}"
            )
            await update.message.reply_text(job_text, parse_mode="HTML")

async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args:
        for rank, (expertise, count) in enumerate(sorted_expertise, start=1):
            rank_text = (f"{rank}. {expertise} - {count} mentions")
            await update.message.reply_text(rank_text)
        return

    for arg in args:
        if arg.lower() in expertise_counter:
            count = expertise_counter[arg.lower()]
            rank_text = f"{arg.title()} is mentioned {count} times."
        else:
            rank_text = f"{arg.title()} is not found in the expertise list."
        await update.message.reply_text(rank_text)

def handle_response(text: str) -> str:
    if 'hello' in text.lower():
        return "Hello! How can I assist you today?"
    
    if 'help' in text.lower():
        return "Sure! What do you need help with?"
    
    if 'bye' in text.lower():
        return "Goodbye! Have a great day!"
    
    return "I don't understand what you wrote"
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            response = handle_response(text.replace(BOT_USERNAME, '').strip())
        else: 
            return
    else:
        response = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response) 

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f'Update "{update}" caused error "{context.error}"')

if __name__ == '__main__':
    print("starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('jobs', jobs_command))
    app.add_handler(CommandHandler('rank', rank_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    print("starting polling...")
    app.run_polling(poll_interval=3)
