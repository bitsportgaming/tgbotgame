import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TASK_WEB_APP_URL = 'https://task.pooldegens.meme/?username={username}'  # Replace with your task page URL

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['game_scores']
scores_collection = db['scores']

# Database functions

def save_score(username: str, score: int) -> None:
    """Save the user's score to the database."""
    scores_collection.update_one({'username': username}, {'$set': {'score': score}}, upsert=True)


def get_score(username: str) -> int:
    """Retrieve the user's score from the database."""
    user = scores_collection.find_one({'username': username})
    return user['score'] if user else 0


def get_leaderboard(limit: int = 10) -> list:
    """Retrieve the top users from the database."""
    return list(scores_collection.find().sort('score', -1).limit(limit))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    logger.info("User %s started the bot.", user.first_name)

    # Description and banner (placeholder)
    description = "🎱 Welcome to Pool Degen! Play pool and compete with others."

    # Main menu buttons
    keyboard = [
        [InlineKeyboardButton("🎮 Start Playing", web_app=WebAppInfo(url=TASK_WEB_APP_URL.format(username=user.username)))],
        [
            InlineKeyboardButton("💬 Join Chat", url='https://t.me/pooldegen'),
            InlineKeyboardButton("🌐 Join Community", url='https://t.me/pooldegenportal')
        ],
        [
            InlineKeyboardButton("🐦 Twitter", url='https://twitter.com/pooldegen'),
            InlineKeyboardButton("📊 My Profile", callback_data='my_profile')
        ],
        [InlineKeyboardButton("📨 Invite Friends", switch_inline_query="Check out Pool Degen! 🎱 Join the fun and play 8-ball pool with me. Compete, earn, and have a blast! 🚀 [Join now](https://t.me/pooldegenbot)")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data='leaderboard')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(description, reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()

    if query.data == 'my_profile':
        username = update.effective_user.username
        score = get_score(username)
        await query.edit_message_text(text=f"Your profile:\nUsername: {update.effective_user.username}\nScore: {score}")
    elif query.data == 'leaderboard':
        await show_leaderboard(query)
    elif query.data == 'back_to_menu':
        await start(update, context)


async def show_leaderboard(query) -> None:
    """Send the leaderboard when the command /leaderboard is issued."""
    top_users = get_leaderboard()
    leaderboard_text = "🏆 Leaderboard 🏆\n\n"
    leaderboard_text += "Rank | Username | Score\n"
    leaderboard_text += "----------------------\n"
    for i, user in enumerate(top_users, start=1):
        leaderboard_text += f"{i}. {user['username']} - {user['score']}\n"
    
    # Add back button
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(leaderboard_text, reply_markup=reply_markup)


@app.route('/save_score', methods=['POST'])
def save_score_endpoint():
    data = request.json
    username = data['username']
    score = data['score']
    save_score(username, score)
    return jsonify({'status': 'success'})


def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("leaderboard", show_leaderboard))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == '__main__':
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5002))
    flask_thread.start()
    main()