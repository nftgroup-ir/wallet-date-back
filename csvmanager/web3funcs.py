from web3 import Web3
from datetime import datetime
from .models import *
timestamp = 1545730073
dt_obj = datetime.fromtimestamp(1140825600)

infura = 'https://mainnet.infura.io/v3/5e5b7b87ad6a4a899bd80becd958b765'
w3 = Web3(Web3.HTTPProvider(infura))


def removeHExBytes(string):
    return string.hex()

def TxWeb3BalanceByBlock(walletAddress,startBlock,endBlock):
    print("Searching for transactions to/from account \"" , walletAddress + "\" within blocks "  , startBlock , " and " , endBlock)
    for i in range(startBlock,endBlock):
        block = w3.eth.getBlock(i,True)
        if block != None and block.transactions != None:
            for i in block.transactions:
                print('from: ',i['from'],' to: ',i['to'])
    return "dare mishe"

def getBlocks(fromNumber,toNumber):
    toNumber += 1
    for i in range(fromNumber,toNumber):
        block = w3.eth.getBlock(i,True)
        if block != None:
            Block.objects.update_or_create(number=block.number,defaults = {
                                    'baseFeePerGas':  block.baseFeePerGas,
                                    'difficulty': block.difficulty,
                                    'extraData': block.extraData,
                                    'gasLimit': block.gasLimit,
                                    'gasUsed': block.gasUsed,
                                    'hash':  block.hash,
                                    'logsBloom': block.logsBloom,
                                    'miner': block.miner,
                                    'mixHash':  block.mixHash,
                                    'nonce': block.nonce,
                                    'parentHash':  block.parentHash,
                                    'receiptsRoot': block.receiptsRoot,
                                    'sha3Uncles': block.sha3Uncles,
                                    'size': block.size,
                                    'stateRoot':  block.stateRoot,
                                    'timestamp':  datetime.fromtimestamp(block.timestamp),
                                    'totalDifficulty': block.totalDifficulty,
                                    'transactions': len(block.transactions)
                                })
            if block.transactions != None:
                for i in block.transactions:
                    print('from: ',i['from'],' to: ',i['to'])
                    obj , created = Transaction.objects.update_or_create(
                                                        hash = removeHExBytes(i.hash),
                                                        defaults = {
                                                                'nonc': i.nonce,
                                                                'transaction_index': i.transactionIndex,
                                                                'from_address': i['from'],
                                                                'value': i.value,
                                                                'gas': i.gas,
                                                                'gas_price': i.gasPrice,
                                                                'input': i.input,
                                                                'block_timestamp': datetime.fromtimestamp(block.timestamp),
                                                                'block_number': block.number,
                                                                'block_hash': removeHExBytes(block.hash),
                                                                'transaction_type': i.type
                                                        }
                            )

                    address, adCreated = CSV.objects.get_or_create(address = i['from'])        
                    address, adCreated = CSV.objects.get_or_create(address = i['to'])        

    return "dare mishe"    
