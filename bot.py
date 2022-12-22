import logging
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler,
    filters, MessageHandler, ConversationHandler, PicklePersistence)
from bot_token import TOKEN
from content import *
from User import User
from database import Db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

default_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton(default_buttons[0])],
        [KeyboardButton(default_buttons[1]), KeyboardButton(default_buttons[2])],
        [KeyboardButton(default_buttons[3])]
    ],
    resize_keyboard=True
)

question_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton(CANCEL)]],
    resize_keyboard=True
)

off_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("Start")]],
    resize_keyboard=True
)

Q1, Q2, Q3, Q4, Q5 = range(5)

REG_CANCEL = filters.Regex(re.compile(f"^({CANCEL})(\.|!)?$", re.IGNORECASE))

async def user_register(update, context):
    user_current = update.effective_user
    user_id = user_current.id

    user = User.objects.get(user_id)
    if not user:
        user = User(user_id)
        logging.info(f"Added new user: {user.id} {user_current['name']} {user_current['full_name']}")

    user.id = user_id
    user.username = user_current['name']
    user.full_name = user_current['full_name']
    user.bot_active = True

    db.save(user)

async def check_user(update, context):
    user = User.objects.get(update.effective_user.id)
    if not user:
        await user_register(update, context)
    else:
        db.check_in(user)

async def start(update, context):

    await user_register(update, context)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=START_MES,
        reply_markup=default_keyboard
    )
    return ConversationHandler.END

async def off(update, context):
    user = User.objects.get(update.effective_user.id)
    if user:
        db.stop_activity(user)
        db.check_in(user)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=OFF_MES,
        reply_markup=off_keyboard
    )
    return ConversationHandler.END

async def user_message(update, context):
    user = User.objects.get(update.effective_user.id)
    if not user:
        await user_register(update, context)
    else:
        db.check_in(user)

    message = update.message.text
    if message.lower() == default_buttons[0].lower():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=replies[0],
            reply_markup=default_keyboard
        )
    elif message.lower() == default_buttons[1].lower():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=replies[1],
            reply_markup=default_keyboard
        )
    elif message.lower() == default_buttons[2].lower():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=replies[2],
            reply_markup=default_keyboard
        )
    else:
        await start(update, context)

async def questionnaire(update, context):
    user = User.objects.get(update.effective_user.id)
    if not user:
        await user_register(update, context)
    else:
        db.check_in(user)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[0],
        reply_markup=question_keyboard
    )
    return Q1

async def q1(update, context):
    user = User.objects.get(update.effective_user.id)

    if not user:
        await user_register(update, context)
        user = User.objects.get(update.effective_user.id)

    message = update.message.text
    user.quest = '1). ' + message + '\n\n'
    db.save(user)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[1],
        reply_markup=question_keyboard
    )
    return Q2

async def q2(update, context):
    user = User.objects.get(update.effective_user.id)

    if not user:
        await user_register(update, context)
        user = User.objects.get(update.effective_user.id)

    message = update.message.text
    user.quest += '2). ' + message + '\n\n'
    db.save(user)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[2],
        reply_markup=question_keyboard
    )
    return Q3

async def q3(update, context):
    user = User.objects.get(update.effective_user.id)

    if not user:
        await user_register(update, context)
        user = User.objects.get(update.effective_user.id)

    message = update.message.text
    user.quest += '3). ' + message + '\n\n'
    db.save(user)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[3],
        reply_markup=question_keyboard
    )
    return Q4

async def q4(update, context):
    user = User.objects.get(update.effective_user.id)

    if not user:
        await user_register(update, context)
        user = User.objects.get(update.effective_user.id)

    message = update.message.text
    user.quest += '4). ' + message + '\n\n'
    db.save(user)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[4],
        reply_markup=question_keyboard
    )
    return Q5

async def q5(update, context):
    user = User.objects.get(update.effective_user.id)

    if not user:
        await user_register(update, context)
        user = User.objects.get(update.effective_user.id)

    message = update.message.text
    user.quest += '5). ' + message + '\n\n'
    db.save(user)

    logging.info(f'User {user.id} {user.username} {user.full_name} completed the quest')

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=CONV_COMPLETE,
        reply_markup=default_keyboard
    )

    await context.bot.send_message(
        chat_id=REG_CHATID,
        text=f"{user.username}\n{user.full_name}:\n\n{user.quest}"
    )
    return ConversationHandler.END

async def cancel(update, context):
    user = User.objects.get(update.effective_user.id)
    if not user:
        await user_register(update, context)
    else:
        db.check_in(user)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Canceled.",
        reply_markup=default_keyboard
    )
    return ConversationHandler.END

if __name__ == '__main__':
    db = Db()
    users = User.objects

    persistence = PicklePersistence('persistence')

    builder = ApplicationBuilder().token(TOKEN)
    builder.read_timeout(20)
    builder.write_timeout(20)
    builder.connect_timeout(20)
    builder.pool_timeout(20)
    builder.get_updates_read_timeout(20)

    application = builder.persistence(persistence).build()

    start_handler = CommandHandler(['start', 'on'], start)
    off_handler = CommandHandler('off', off)
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(re.compile(f"^({default_buttons[3]})(\.|!)?$", re.IGNORECASE)), questionnaire)
        ],
        states={
            Q1: [MessageHandler(filters.TEXT & ~(filters.COMMAND | REG_CANCEL), q1)],
            Q2: [MessageHandler(filters.TEXT & ~(filters.COMMAND | REG_CANCEL), q2)],
            Q3: [MessageHandler(filters.TEXT & ~(filters.COMMAND | REG_CANCEL), q3)],
            Q4: [MessageHandler(filters.TEXT & ~(filters.COMMAND | REG_CANCEL), q4)],
            Q5: [MessageHandler(filters.TEXT & ~(filters.COMMAND | REG_CANCEL), q5)],
        },
        fallbacks=[
            MessageHandler(REG_CANCEL, cancel),
            CommandHandler('cancel', cancel),
            CommandHandler('off', off),
            CommandHandler(['start', 'on'], start)
        ],
        name="Questionnaire",
        persistent=True
    )
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), user_message)

    application.add_handler(conv_handler)
    application.add_handler(start_handler)
    application.add_handler(off_handler)
    application.add_handler(message_handler)

    application.run_polling()
