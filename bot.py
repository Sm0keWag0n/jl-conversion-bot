from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re, os, discord

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER = os.getenv('ADMIN_USER')

def html_get(url):
    try:
        with closing(get(url, stream=True)) as response:
            if response.status_code == 200 and response.headers['Content-Type'].lower() is not None:
                return response.content
            else:
                return None
    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def get_famichiki_price():
    url = 'https://www.family.co.jp/goods/friedfoods/0253116.html'
    regex = '税込(.*?)円'

    raw_html = html_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')
    price_spans = html.find_all('span', {'class' : 'ly-kakaku-usual'})
    if len(price_spans) != 1:
        raise Exception("Error getting Famichiki price")
    raw_price = price_spans[0].text
    price = re.search(regex, raw_price).group(1)
    return int(price)

def get_nanachiki_price():
    url = 'https://www.sej.co.jp/products/a/item/150446/'
    regex = '税込(.*?)円'

    raw_html = html_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')
    price_divs = html.find_all('div', {'class' : 'item_price'})
    if len(price_divs) != 1:
        raise Exception("Error getting Nanachiki price")
    raw_price = price_divs[0].text
    price = re.search(regex, raw_price).group(1)
    return int(price)

famichiki_price = get_famichiki_price()
nanachiki_price = get_nanachiki_price()
strongzero_price = 130

commands = ['!famichiki', '!nanachiki', '!strongzero']

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    args = message.content.casefold().split()
    if args[0] in commands:
        if len(args) == 2:
            amount_string = args[1]
            amount_string_sanitized = re.sub("[^0-9]", "", amount_string)
            amount = int(amount_string_sanitized)
            if args[0] == "!famichiki":
                famichiki_count = (amount / famichiki_price).floor()
                remainder = amount - (famichiki_count * famichiki_price)
                response = '{0:,}円 will buy {1:,} Famichiki at {2}円 each. You have {3}円 left.'.format(amount, famichiki_count, famichiki_price, remainder)
                if remainder >= strongzero_price:
                    response += " Why not buy a Strong Zero too?"
            elif args[0] == "!nanachiki":
                nanachiki_count = (amount / nanachiki_price).floor()
                remainder = amount - (nanachiki_count * nanachiki_price)
                response = '{0:,}円 will buy {1:,} Nanachiki at {2}円 each. You have {3}円 left.'.format(amount, nanachiki_count, nanachiki_price, remainder)
                if remainder >= strongzero_price:
                    response += " Why not buy a Strong Zero too?"
            elif args[0] == "!strongzero":
                strongzero_count = (amount / strongzero_price).floor()
                remainder = amount - (strongzero_count * strongzero_price)
                response = '{0:,}円 will buy {1:,} Strong Zeros at {2}円 each. You have {3}円 left'.format(amount, strongzero_count, strongzero_price, remainder)
        else:
            response = "Only one amount of yen, please."
        await message.channel.send(response)

client.run(TOKEN)
