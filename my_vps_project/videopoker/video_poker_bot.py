import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, PreCheckoutQueryHandler
import os

import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from helpers import database_connect
import json

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)





# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! This bot and mini app is still in development. Please stay with us. Thank you!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Hello! This bot and mini app is still in development. Please stay with us. Thank you!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

# after (optional) shipping, it's the pre-checkout
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    try:
        payload = json.loads(query.invoice_payload)
    except ValueError as err:
        await query.answer(ok=False, error_message="Sorry! Payload is not correct. JSON format is incorrect.")
        return
    
    payload_keys = ['telegram_id', 'amount', 'price']

    for k in payload_keys:
        if k not in payload.keys():
            await query.answer(ok=False, error_message="Sorry! Payload is not correct. Key value error.")
            return
    
    if payload['telegram_id'] == "0":
        await query.answer(ok=False, error_message="Sorry! Telegram Id is not recognized.")
        return

    await query.answer(ok=True)
        


# finally, after contacting the payment provider...
async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirms the successful payment."""
    payment = update.message.successful_payment

    
    payload = json.loads(payment.invoice_payload)
    telegram_id = int(payload['telegram_id'])
    amount = int(payload['amount'])

    balance_update_sql = '''UPDATE videopoker_users SET balance = balance + %s WHERE telegram_id = %s RETURNING balance;'''
    result_balance = database_connect.execute_insert_update_sql(balance_update_sql, (amount, telegram_id))

    # do something after successfully receiving payment?
    await update.message.reply_text(f"Thank you for your payment! Your balance has been replenished by {amount} chips.")

##############################################################################


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    TEL_TOKEN = os.environ['TEL_TOKEN']
    application = Application.builder().token(TEL_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Pre-checkout handler to final check
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Success! Notify your user!
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

