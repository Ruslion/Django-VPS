from . import database_connect
from datetime import datetime
ADSGRAM_VIEWS_LIMIT = 20

def get_adsgram_views_today_and_add_daily_bonus(user_id):
    result_adsgram_views = database_connect.execute_select_sql("SELECT adsgram_views_today, adsgram_viewed_day FROM videopoker_users WHERE telegram_id = %s", (user_id,))
    if result_adsgram_views: # Record in database found
        today = datetime.today().date()
        if today > result_adsgram_views[0][1]:
            # Need to reset the adsgram_views to ADSGRAM_VIEWS_LIMIT
            update_adsgram_sql = '''UPDATE videopoker_users SET adsgram_views_today = %s,
                                    adsgram_viewed_day = %s,
                                    balance = balance + 300 
                                    WHERE telegram_id = %s RETURNING adsgram_views_today;'''
            result_update_adsgram_views = database_connect.execute_insert_update_sql(update_adsgram_sql, (ADSGRAM_VIEWS_LIMIT,
                                                                                                            today, user_id))
            return ADSGRAM_VIEWS_LIMIT
        else:
            return result_adsgram_views[0][0]     
    else:
        # Record not found in the database
        print(f"Record {user_id} not found in the database. update_adsgram_div.html")
        return 0