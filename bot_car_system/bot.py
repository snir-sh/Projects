import ast
import Logger
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, ConversationHandler, CallbackQueryHandler, 
                          CommandHandler, ContextTypes, filters, MessageHandler)

from car_recommendation import chat
from gpt_query_data import TELEGRAM_TOKEN, TEXTS
from enums import *

SUPPORTED_LANGUAGES = ["Hebrew", "English"]
CHOOSING, HANDLE_RECOMMENDATION, HANDLE_SEARCH, HANDLE_LANGUAGE = range(4)

Logger.info("System started. Waiting for action")

"\u200F"

async def safe_reply(update: Update, text: str, reply_markup=None):
    # is_rtl_language = context.user_data.get("language", "Hebrew") in ["Hebrew", "Arabic"]
    if update.message:
        return await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        return await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
    
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session_language = context.user_data.get("language", "Hebrew")
    Logger.info("Received 'start' command")
    keyboard = [
        [InlineKeyboardButton(TEXTS[session_language]["recommendation_title"], callback_data=Actions.RECOMMENDATION.value)],
        [InlineKeyboardButton(TEXTS[session_language]["search_title"], callback_data=Actions.SEARCH.value)],
        [InlineKeyboardButton(TEXTS[session_language]["choose_language_title"], callback_data=Actions.LANGUAGE.value)],
    ]

    if update.message:
        await update.message.reply_text(TEXTS[session_language]["start"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    if update.callback_query:
        return await update.callback_query.message.reply_text(TEXTS[session_language]["start"], 
                                                              reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING

async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Logger.info("Received 'start' command")
    query = update.callback_query
    await query.answer()

    if query.data == "language":
        keyboard = [
            [InlineKeyboardButton("עברית / Hebrew", callback_data="Hebrew")],
            [InlineKeyboardButton("אנגלית / English", callback_data="English")],
        ]

        await query.edit_message_text(
            "Choose your language:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return HANDLE_LANGUAGE
    elif query.data in SUPPORTED_LANGUAGES:
        context.user_data["language"] = query.data
        await query.edit_message_text(f"Language was set to: {query.data}")
        await start_command(update, context)
        return CHOOSING
    return


async def handler_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    session_language = context.user_data.get("language", "Hebrew")
    context.user_data["messages"] = list() # reset memory

    Logger.info(f"User {update.effective_user.id} chose '{query.data}'")
    if query.data == Actions.RECOMMENDATION.value:
        await query.edit_message_text(TEXTS[session_language]["recommendation"])
        return HANDLE_RECOMMENDATION
    elif query.data == Actions.SEARCH.value:
        await query.edit_message_text(TEXTS[session_language]["search"])
        return HANDLE_SEARCH
    elif query.data == Actions.LANGUAGE.value:
        return await handle_language(update, context) 
        # await query.edit_message_caption("Language set to:")
    else:
        await query.edit_message_text(TEXTS[session_language]["unknown"])
        return ConversationHandler.END

async def handle_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #message = update.message or update.callback_query.message
    context.user_data["messages"].append({
        "role": Role.USER.value,
        "content": update.message.text
    })
    
    #await update.message.reply_text(f"Handler recommendation received: {text}")
    response = await recommend(context.user_data["messages"], Actions.RECOMMENDATION.value, update)

    if response.get('relevant'):
        context.user_data["messages"].append({
            "role": Role.ASSISTANT.value,
            "content": response["answer"]
        })
    else:
        context.user_data["messages"].pop()


async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["messages"].append({
        "role": Role.USER.value,
        "content": text
    })
    #await update.message.reply_text(f"Handler search received: {text}")
    response = await recommend(context.user_data["messages"], Actions.SEARCH.value, update)

    if response.get('relevant'):
        context.user_data["messages"].append({
            "role": Role.ASSISTANT.value,
            "content": response["answer"]
        })
    else:
        context.user_data["messages"].pop()


async def cancel(update: Update, context):
    session_language = context.user_data.get("language", "Hebrew")
    Logger.info("Received 'cancel' command")
    await update.message.reply_text(TEXTS[session_language]["cancel"])
    return ConversationHandler.END

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session_language = context.user_data.get("language", "Hebrew")
    Logger.info("Received 'help' command")
    await update.message.reply_text(TEXTS[session_language]["help"])

async def training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session_language = context.user_data.get("language", "Hebrew")
    Logger.info("Received 'training' command")
    await update.message.reply_text(TEXTS[session_language]["training"])

async def error_handler(update, context):
    """Log the error and send a telegram message to notify the user."""
    # print(f"Update {update} caused error {context.error}")
    Logger.error(f'System error: {update} caused error {context.error}')
    if not update:
        return

    session_language = context.user_data.get("language", "Hebrew")

    if update.message:
        await update.message.reply_text(TEXTS[session_language]["system_error"])
    if update.callback_query:
        return await update.callback_query.message.reply_text(TEXTS[session_language]["system_error"], 
                                                              reply_markup=None)

async def recommend(history, chat_type, update: Update):
    Logger.info(f'Chat request: {history[-1]}')
    response = await chat(history, chat_type)
    response = json.loads(response)
    # response = ast.literal_eval(response)
    if not response.get('relevant', True):
        Logger.warning(f'Illegal request. Chat response: {response}')
        await update.message.reply_text(f"{response['answer']}") #, finish={response['finish']}")
        return response

    Logger.info(f'Chat response: {response}')
    # await send_as_list(cars, update)
    # await update.message.reply_text(response['relevant'])
    await safe_reply(update, f"{response['answer']}") #, finish={response['finish']}")
    return response

async def send_as_list(items, update):
    text = "\n".join(
        f"* Model: {item['degem_nm']} | Manufacturer: {item['tozeret_nm']} | Price: {item['price_ils']}"
        f"* Model: {item['degem_nm']} | Price: {item['price_ils']} Description: {item['description']}"
        for item in items
    )
    await update.message.reply_text(text)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler(Commands.START.value, start_command)],

    states={
        CHOOSING: [CallbackQueryHandler(handler_buttons)],         # handles button clicks
        HANDLE_RECOMMENDATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_recommendation)], 
        HANDLE_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search)],
        HANDLE_LANGUAGE: [CallbackQueryHandler(handle_language)],
    },

    fallbacks=[CommandHandler(Commands.CANCEL.value, cancel)],
)

app.add_handler(CommandHandler(Commands.TRAIN.value, training))
app.add_error_handler(error_handler)

# app.add_handler(CommandHandler("start", start_command))
# app.add_handler(CallbackQueryHandler(buttons))
# app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.add_handler(CommandHandler(Commands.HELP.value, help))
app.add_handler(conv)
app.run_polling()
