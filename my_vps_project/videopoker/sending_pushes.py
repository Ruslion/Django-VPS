import asyncio
import aiohttp
import time
import os
import json
from helpers import database_connect

class AsyncRateLimitedRequester:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.semaphore = asyncio.Semaphore(rate_limit)

    async def make_request(self, url, params, tg_id):
        async with self.semaphore:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            
            if time_since_last_request < 1 / self.rate_limit:
                await asyncio.sleep((1 / self.rate_limit) - time_since_last_request)
            
            async with aiohttp.ClientSession() as session:
                params['chat_id'] = tg_id
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        print(f"Request to {url} completed with status code: {response.status}. User id {tg_id}")
            
            self.last_request_time = time.time()

    async def process_urls(self, url, params, tg_list):
        tasks = [self.make_request(url, params, tg_id[0]) for tg_id in tg_list]
        await asyncio.gather(*tasks)

async def main():
    requester = AsyncRateLimitedRequester(rate_limit=25)
    url_begin = 'https://api.telegram.org/bot'
    token = os.environ['TEL_TOKEN']
    method_name = '/sendMessage'
    url_final = url_begin + token + method_name

    selection_sql = '''SELECT telegram_id FROM videopoker_users;
        '''
    telegram_id_list = database_connect.execute_select_sql(selection_sql, None)

    inline_keyboard_dict = {'inline_keyboard': [[{'text': 'Play!',
                                    'web_app': {'url': 'https://pychampion.site/videopoker/'}
                                  }]]}

    reply_markup = json.dumps(inline_keyboard_dict)

    params = {'chat_id': 0,
          'parse_mode':'HTML',
          'text': '''🃏 Video Poker Fans! Ready for a royal challenge? 👑
          
Did you know there are 2,598,960 unique hand combinations in 5-card draw? Yet, the elusive Royal Flush appears only once in 649,740 hands on average!

Can you beat the odds? Our game uses virtual chips, so it's all about skill, no financial risk!

🏆 In the leaderboard you may find who took the first row for the last week and month.

Will you top the leaderboard this week? Login now and show us your poker face!
Remember, every hand could be that 1 in 649,740.
Good luck!''',
          'disable_notification': 'true',
          'reply_markup':reply_markup
          }

    await requester.process_urls(url_final, params, telegram_id_list)

if __name__ == "__main__":
    asyncio.run(main())