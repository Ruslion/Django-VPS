from . import database_connect
from datetime import datetime
ADSGRAM_VIEWS_LIMIT = 20
DAILY_LOGIN_REWARD = 300

def get_balance_id_adsgram_views_today_and_add_daily_bonus(telegram_id):
    # This function gets balance, id and updates balance for daily login bonus.
    # This function is overloaded to avoid unnecessary database requests.

    result_adsgram_views = database_connect.execute_select_sql("""SELECT balance, id, adsgram_views_today, 
                                username, first_name, last_name, photo_url, 
                                adsgram_viewed_day 
                                FROM videopoker_users WHERE telegram_id = %s""", (telegram_id,))
    if result_adsgram_views: # Record in database found
        today = datetime.today().date()
        if today > result_adsgram_views[0][7]:
            # Need to reset the adsgram_views to ADSGRAM_VIEWS_LIMIT
            update_adsgram_sql = '''UPDATE videopoker_users SET adsgram_views_today = %s,
                                    adsgram_viewed_day = %s,
                                    balance = balance + %s 
                                    WHERE telegram_id = %s RETURNING balance, id, adsgram_views_today, 
                                    username, first_name, last_name, photo_url;'''
            result_update_adsgram_views = database_connect.execute_insert_update_sql(update_adsgram_sql, (ADSGRAM_VIEWS_LIMIT,
                                                                                                            today, DAILY_LOGIN_REWARD, 
                                                                                                            telegram_id))
            return (result_update_adsgram_views, )
        else:
            return result_adsgram_views     
    else:
        # Record not found in the database
        return None