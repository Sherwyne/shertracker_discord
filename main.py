import discord
from discord import Webhook, RequestsWebhookAdapter, Embed 
import os
from discord_webhook import DiscordWebhook
import time
from replit import db
import requests
from keepalive import keep_alive
from operator import itemgetter
from web3 import Web3
from threading import Timer
from datetime import datetime


#ENV VAR
bot_token = os.environ['BOT_TOKEN']
etherscan_key = os.environ['etherscan_key']
infura_project_id = os.environ['INFURA_PROJECT_ID']
infura_url = f'https://mainnet.infura.io/v3/{infura_project_id}'

web3 = Web3(Web3.HTTPProvider(infura_url))
is_connected = web3.isConnected()


#A database of wallets I wish to track
db['wallets'] = {
    'kimdamyun.eth': '0xbb257625458a12374daf2ad0c91d5a215732f206',
    'issajoke.eth': '0xdcd95ddd4466609dfc8c37bb93e31f1c8683223d',
    'Shuey': '0x0f9b589fd715bbe0fb2ecd64b88549e5200ca1df',
    'DR': '0xca3e3d41401ec40a5f16c98e8ebf70c4cd4b071a',
    'ilnam.eth': '0x9fc1ba61f696034f19db40432198d5603075ea0d',
    'joegrower420.eth': '0x8413f65e93d31f52706c301bcc86e0727fd7c025',
    'ryu-dummy': '0x066ece91f6242aaea094cb837c1fdee12ae5a7e3',
    'shinjiinu.eth': '0x83a4699a7526b979fca28633efb7f19d652f2773',
    'cryptolawph.eth': '0x74bec7a65a3baea58ab86fb08d42b6c5a96d1cc6'
  
}
name_list = list(db['wallets'].keys())
print(name_list)
db['hashes'] = []


async def get_transactions():
    webhook = os.environ['WEBHOOK']
    latest_block_number = int(web3.eth.get_block('latest')['number'])
    start_block = latest_block_number - 100
  
    for i in range(len(db['wallets'])):
        wallet = db['wallets'][name_list[i]]
        name = list(db['wallets'].keys())[i] 

        #API URL's Below
        normal_txns_url = f'https://api.etherscan.io/api?module=account&action=tokentx&address={wallet}&startblock={start_block}&endblock={latest_block_number}&sort=asc&apikey={etherscan_key}'
       
        #Fetch Etherscan Data
        response = requests.get(url=normal_txns_url)
        data = response.json()
        sorted_result = sorted(data['result'], key=itemgetter('timeStamp'))

        try:
            print(wallet)
            txn_hash = (sorted_result[-1]['hash'])
            fromAddress =  (sorted_result[-1]['from'])
            to =  (sorted_result[-1]['to'])
            tokenName =  (sorted_result[-1]['tokenName'])
            tokenSymbol =  (sorted_result[-1]['tokenSymbol'])
            contractAddress =  (sorted_result[-1]['contractAddress'])
            timeStamp =  int(sorted_result[-1]['timeStamp'])
          
            dexTools = None
            uniswap = None
            etherscan = f"https://etherscan.io/tx/{txn_hash}"
                  
            if to == wallet:
              action = f"bought [{tokenName} ({tokenSymbol})](https://etherscan.io/token/{contractAddress}#tokenTrade)"
              dexTools = f"https://www.dextools.io/app/ether/pair-explorer/{fromAddress}"
              uniswap = f"https://app.uniswap.org/#/swap?inputCurrency={fromAddress}&chain=mainnet"
            else:
              action = f"sold [{tokenName} ({tokenSymbol})](https://etherscan.io/token/{contractAddress}#tokenTrade"
              dexTools = f"<https://www.dextools.io/app/ether/pair-explorer/{to}>"
              uniswap = f"https://app.uniswap.org/#/swap?inputCurrency={to}&chain=mainnet"
            print(txn_hash)
            
            if txn_hash not in db['hashes']:

                web = Webhook.from_url(
                        f'https://discord.com/api/webhooks/{webhook}',
                        adapter=RequestsWebhookAdapter())
                      
                embed = discord.Embed(title="", description="")
                embed.add_field(name="🚨 Wallet Alert 🚨", value=f"""\n
[{name}](https://etherscan.io/address/{wallet}) {action} \n
[Etherscan]({etherscan}) – [Dextools]({dexTools}) – [Uniswap]({uniswap}) \n
                                
                                """)
                embed.timestamp = datetime.fromtimestamp(timeStamp)
                web.send(embed=embed)
                
              
                db['hashes'].append(txn_hash)
            else:
              print("TRANSACTION ALREADY IN DB")
        except:
            print("No Tx")
        
        time.sleep(5)     
        
    Timer(5.0, await get_transactions()).start()
            

  
client = discord.Client()

@client.event
async def on_ready():
    print(f"You have logged in as {client}")
    await get_transactions()
    time.sleep(10)

get_transactions()
keep_alive()
client.run(bot_token)
