from requests import get
from matplotlib import pyplot as plt
from datetime import datetime

api_key = "[redacted]"
address = "0x91364516D3CAD16E1666261dbdbb39c881Dbe9eE"
ether_value = 10**18  # 1 ETH = 10**18 wei

'''https://api.etherscan.io/api
   ?module=account
   &action=balance
   &address=0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae
   &tag=latest
   &apikey=YourApiKeyToken'''

# base url and query parameters
BASE_URL = "https://api.etherscan.io/api"


def make_apiUrl(module, action, address, **kwargs):
    # kwargs to account for arbitrary entries
    url = BASE_URL + \
        f'?module={module}&action={action}&address={address}&apikey={api_key}'
    for key, value in kwargs.items():
        url += f'&{key}={value}'
    return url


def get_account_balance(address):
    get_balance_url = make_apiUrl("account", "balance", address, tag="latest")
    response = get(get_balance_url)
    data = response.json()  # daa returns dictionary
    value = f"this user has: {int(data['result'])/ether_value} eth"
    return value

# all the transactions associated with an ethereum account, (normal and internal transactions)


def get_transactions(address):
    # endpoint from etherscan
    '''https://api.etherscan.io/api
   ?module=account
   &action=txlist
   &address=0xc5102fE9359FD9a28f877a67E36B0F050d81a3CC
   &startblock=0
   &endblock=99999999
   &page=1
   &offset=10
   &sort=asc
   &apikey=YourApiKeyToken'''

    get_transactions_url = make_apiUrl(
        "account", "txlist", address, startblock=0, endblock=17384385, page=1, offset=10000, sort="asc")
    response = get(get_transactions_url)
    data = response.json()['result']

# combine with list of internal transaction to include smart contract calls, etc, not 'normal' person to person trxs
    get_internal_tx_url = make_apiUrl(
        "account", "txlistinternal", address, startblock=0, endblock=17384385, page=1, offset=10000, sort="asc")
    response2 = get(get_internal_tx_url)
    data2 = response2.json()['result']
    data.extend(data2)
    data.sort(key=lambda x: int(x['timeStamp']))

    current_balance = 0
    balances = []
    times = []

    # for each transaction in data
    for tx in data:
        to = tx['to']
        from_addr = tx['from']
        Value = int(tx['value'])/ether_value
        if 'gasPrice' in tx:
            gas = int(tx['gasUsed']) * int(tx['gasPrice'])/ether_value
        else:
            gas = int(tx['gasUsed'])/ether_value

        time_sent = datetime.fromtimestamp(int(tx['timeStamp']))
        # print('------------------------------')
        # print("to: ", to)
        # print('from: ', from_addr)
        # print('value: ', Value)
        # print('Gas used: ', gas)
        # print('Time: ', time_sent)
        # assigning value to comparison directly(boolean returned)

        # check if he to is our address, whether we are on the recieving end
        money_in = to.lower() == address.lower()
        if money_in:
            current_balance += Value
        else:
            # we pay gas when sending or when money_out/!(money_in)
            current_balance -= Value + gas
        balances.append(current_balance)
        times.append(time_sent)
    # get the address do some plottings
    print(current_balance)
    plt.plot(times, balances)
    plt.show()
    plt.title('Plot of Ethereum balance in eth vs time')
    plt.xlabel('time(year)')
    plt.ylabel('balances(ETH)')
# get the balance of an etherum account over time


print(get_transactions('0x91364516D3CAD16E1666261dbdbb39c881Dbe9eE'))
