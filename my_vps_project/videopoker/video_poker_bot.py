import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, PreCheckoutQueryHandler
import os

import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from helpers import database_connect
import json
from datetime import datetime

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
        rf"Hi {user.mention_html()}! Welcome to our application. Have fun and play video poker!",
        # reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("""The goal of a video poker game is to create the best possible five-card poker hand after a single draw,
    aiming to match winning combinations listed in the game's paytable to win a payout. Playing chips are used to place a bet. 
    Playing chips cannot be converted, sold, gifted or used elsewhere but this application. Any suggestions to the application can be sent
    to the developers in a message to this bot with 'Suggestion:' prefix. Please limit your suggestions to 200 symbols.
    """)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    reply_text = "Have fun! :) - autoreply."
    user_id = int(update.effective_user.id)
    message = update.message.text
    if message[:11] == 'Suggestion:':
        # Suggestion received.
        message = message[11:] # Deleting prefix
        message = message[:200] # Trimming string
        suggestion_sql = '''INSERT INTO videopoker_suggestions (telegram_id, suggestion)
                        VALUES (%s, %s) RETURNING id;
        '''
        result_suggestion = database_connect.execute_insert_update_sql(suggestion_sql, (user_id,message))
        reply_text = 'Thank you for your suggestion!'

    await update.message.reply_text(reply_text)

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

    # Saving successful transaction to the SuccessfulPayment table.

    saving_transaction_sql = '''INSERT INTO videopoker_successfulpayment (date_time, currency, total_amount, chips_bought,
                                telegram_id, telegram_payment_charge_id, provider_payment_charge_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
    '''

    date_time = datetime.now()
    currency = payment.currency
    total_amount = payment.total_amount
    chips_bought = amount
    # telegram_id is already known
    telegram_payment_charge_id = payment.telegram_payment_charge_id
    provider_payment_charge_id = payment.provider_payment_charge_id

    result_transaction = database_connect.execute_insert_update_sql(saving_transaction_sql, (date_time, currency,  total_amount,
                                                    chips_bought, telegram_id, telegram_payment_charge_id, provider_payment_charge_id
                                                    ))


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

