from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)
import json
import os
import sys
import os.path
from os import path
import uuid
import brownie.project
import web3
import subprocess
import glob
from web3 import Web3
from brownie import *
from datetime import datetime
import time
import requests
from threading import Thread
import asyncio
import codecs
import random
import math

p = brownie.project.load('/home/miranda/flask_application/BrownieTeseProject', name="Tese")
p.load_config()
from brownie.project.Tese import TxtDocShare, TokenErc20, ProxyErc20
import brownie.network as network

#Blockchains: This solution have n = 3
inputBlockchain1 = "goerli"
inputBlockchain2 = "goerli"
inputBlockchain3 = "goerli"
#inputBlockchain1 = "kovan"
#inputBlockchain2 = "goerli"
#inputBlockchain3 = "rinkeby"

#Blockchains names:
nameBlockchain1 = "Goerli"
nameBlockchain2 = "Goerli"
nameBlockchain3 = "Goerli"
#nameBlockchain1 = "Kovan"
#nameBlockchain2 = "Goerli"
#nameBlockchain3 = "Rinkeby"


def getMatrix(file, type):
    substring = "0x"
    Matrix = []
    MatrixN = []
    count = 0
    for text in file:
        if text is not None and text.find(substring) != -1:
            text = text.replace("\n", "")
            MatrixY = text.split(":")

            MatrixN.append(MatrixY)
            count = count + 1

            if count == 3:
                guid = ""
                same = True
                for attr in MatrixN:
                    if guid == "":
                        guid = attr[2]
                    else:
                        if attr[2] != guid:
                            same = False
                if same is True and type == attr[3]:
                    Matrix.append(MatrixN)
                MatrixN = []
                count = 0

    return Matrix


def getAddress():
    accFile = '../config/address.txt'
    # readmode +, if do not exists, create a new one
    acc = open(accFile, 'r+')

    if os.path.getsize(accFile) == 0:
        return -1
    else:
        Matrix = []
        for text in acc:
            if text is not None:
                text = text.replace("\n", "")
                temp = text.split(":")

                Matrix.append(temp)

        return Matrix


def getJsonContractDocBlock(type):
    configFile = '../config/contracts.txt'
    # readmode +, if do not exists, create a new one
    file = open(configFile, 'r+')

    if os.path.getsize(configFile) == 0:
        return -1
    else:
        return getMatrix(file, type)


def getJsonContract():
    contracts = glob.glob("../contracts/*.sol")
    contracts.remove("../contracts/proxyErc20.sol")
    return contracts;


def addFile(Matrix, docname, text, address1, address2, address3):
    if docname and text:
        fileID1 = asyncio.run(addFileBlockChain(Matrix[0][1], inputBlockchain1, docname, text, address1))
        if fileID1 > -1:
            fileID2 = asyncio.run(addFileBlockChain(Matrix[1][1], inputBlockchain2, docname, text, address2))
            if fileID2 > -1:
                fileID3 = asyncio.run(addFileBlockChain(Matrix[2][1], inputBlockchain3, docname, text, address3))
                if fileID3 > -1:
                    return 1
                else:
                    fileReverter(Matrix[0][1], inputBlockchain1, fileID1, address1)
                    fileReverter(Matrix[1][1], inputBlockchain2, fileID2, address2)
                    return -1
            else:
                fileReverter(Matrix[0][1], inputBlockchain1, fileID1, address1)
                return -1
        else:
            return -1
    else:
        return -1


def fileReverter(address, testnet, id, addressacc):
    connectNetwork(testnet)

    dev = network.accounts.add(addressacc)

    contract = TxtDocShare.at(address)

    contract.setStatus(id, {'from': dev})


async def addFileBlockChain(address, testnet, filename, text, accAddress):
    connectNetwork(testnet)

    dev = network.accounts.add(accAddress)

    contract = TxtDocShare.at(address)

    result = -1
    count = 1
    while result <= 0 and count <= 5:
        tx = contract.addDoc(filename, text, {'from': dev})

        result = int(tx.status)

        count = count + 1

    return result


def getNumFiles(Matrix):
    connectNetwork(inputBlockchain1)
    numKovan = TxtDocShare.at(Matrix[0][1]).getNumDocs()

    connectNetwork(inputBlockchain2)
    numGoerli = TxtDocShare.at(Matrix[1][1]).getNumDocs()

    connectNetwork(inputBlockchain3)
    numRink = TxtDocShare.at(Matrix[2][1]).getNumDocs()

    if numKovan == numGoerli and numKovan == numRink:
        return numKovan
    else:
        return -1


def getAllFiles(Matrix):
    numFiles = getNumFiles(Matrix)

    if numFiles > 0:
        doc = []
        for x in range(numFiles):
            doc.append(getLastDoc(x, Matrix))

        return doc
    elif numFiles == -1:
        return -1
    else:
        return -1


def connectNetwork(testnet):
    if network.is_connected():
        network.disconnect()

    network.connect(testnet)
    network.accounts.clear()


def getLastDoc(idDoc, Matrix):
    #alterar para a versão
    connectNetwork(inputBlockchain1)
    doc1 = TxtDocShare.at(Matrix[0][1]).getDoc(idDoc)

    connectNetwork(inputBlockchain2)
    doc2 = TxtDocShare.at(Matrix[1][1]).getDoc(idDoc)

    connectNetwork(inputBlockchain3)
    doc3 = TxtDocShare.at(Matrix[2][1]).getDoc(idDoc)

    lastversion = [doc1[2], doc2[2], doc3[2]]
    lastversion.sort(reverse=True)

    if lastversion[0] == doc1[2]:
        return [doc1[0], doc1[1], doc1[2], doc1[3], doc1[4], doc1[5], doc1[6], nameBlockchain1]
    elif lastversion[0] == doc2[2]:
        return [doc2[0], doc2[1], doc2[2], doc2[3], doc2[4], doc2[5], doc2[6], nameBlockchain2]
    else:
        return [doc3[0], doc3[1], doc3[2], doc3[3], doc3[4], doc3[5], doc3[6], nameBlockchain3]


def getSingleFile(Matrix, idDoc):
    if idDoc < 0:
        return -1

    doc = getLastDoc(idDoc, Matrix)

    if not str(doc[0]):
        return -1

    return doc


def editDocBlockchain(Matrix, idDoc, docname, text, address1, address2, address3, currentdocname, currenttext, version):
    if not docname and not text:
        return -1

    if not docname:
        docname = currentdocname

    if not text:
        text = currenttext
    #n = número total e f = total falha
    status1 = -1
    status2 = -1
    status3 = -1
    edit = -1

    while (status1 == -1 and status3 == -1) or (status3 == -1 and status2 == -1) or (status1 == -1 and status2 == -1):
        if status1 == -1:
            connectNetwork(inputBlockchain1)
            dev = network.accounts.add(address1)
            result = TxtDocShare.at(Matrix[0][1]).editDoc(idDoc, docname, text, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                status1 = 1
            else:
                status1 = -1

            if status1 != -1:
                edit = edit + 1

        if status2 == -1:
            connectNetwork(inputBlockchain2)
            dev = network.accounts.add(address2)
            result = TxtDocShare.at(Matrix[1][1]).editDoc(idDoc, docname, text, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                status2 = 1
            else:
                status2 = -1

            if status2 != -1:
                edit = edit + 1

        if status3 == -1:
            connectNetwork(inputBlockchain3)
            dev = network.accounts.add(address3)
            result = TxtDocShare.at(Matrix[2][1]).editDoc(idDoc, docname, text, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                status3 = result
            else:
                status3 = -1

            if status3 != -1:
                edit = edit + 1

        return edit


def editFile(Matrix, idDoc, docname, text, address1, address2, address3):
    if idDoc < 0:
        return -2

    doc = getLastDoc(idDoc, Matrix)

    if not str(doc[0]):
        return -2

    result = editDocBlockchain(Matrix, idDoc, docname, text, address1, address2, address3, doc[0], doc[1], int(doc[2]))

    if result < 1:
        return -1
    else:
        doc = getLastDoc(idDoc, Matrix)
        return doc


def hasItem(matrix, type):
    count = False

    for attr in matrix:
        if attr[0][0] == type:
            count = True

    return count


def publishcontract(ncontract, contractname, address1, address2, address3, symbol = "", total = ""):
    contractarr = glob.glob("../contracts/*.sol")
    contractarr.remove("../contracts/proxyErc20.sol")

    try:
        if contractarr[int(ncontract) - 1].find("../contracts/txtDocShare.sol") != -1:
            if hasname(contractname, "1") == -1:
                return -1

            publishbrownie(contractarr[int(ncontract) - 1], contractname, "1", address1, address2,
                           address3)
            return 1
        elif contractarr[int(ncontract) - 1].find("../contracts/tokenErc20.sol") != -1:
            if hasname(contractname, "2") == -1:
                return -1
            elif symbol == "" or total == "":
                return -1

            publishbrownie(contractarr[int(ncontract) - 1], contractname, "2", address1, address2,
                           address3, symbol, total)


            return 1
    except:
        return -1


def getGuid():
    isduplicate = True
    strguid = ""
    while isduplicate is True:
        isduplicate = False
        strguid = str(uuid.uuid4())
        configFile = '../config/contracts.txt'
        file = open(configFile, 'r')

        if os.path.getsize(configFile) == 0:
            return strguid
        else:
            for text in file:
                if text is not None:
                    text = text.replace("\n", "")
                    if text[-36:] == strguid:
                        isduplicate = True

    return strguid


def publishbrownie(name, contract, type, address1, address2, address3, symbol = "", total = ""):
    try:
        strguid = getGuid()
        add = asyncio.run(subpublishbrownie(inputBlockchain1, contract, type, address1, symbol, total))

        if len(add) == 42:
            writecontractfile(contract, add, strguid, type)
            add = asyncio.run(subpublishbrownie(inputBlockchain2, contract, type, address2, symbol, total))
            if len(add) == 42:
                writecontractfile(contract, add, strguid, type)
                add = asyncio.run(subpublishbrownie(inputBlockchain3, contract, type, address3, symbol, total))
                if len(add) == 42:
                    writecontractfile(contract, add, strguid, type)
                    return 1
                else:
                    return -1
            else:
                return -1
        else:
            return -1
    except Exception as ex:
        return -1


async def subpublishbrownie(testnet, name, type, address, symbol = "", total = ""):
    try:
        connectNetwork(testnet)
        network.accounts.clear()

        dev = network.accounts.add(address)

        #network.gas_limit(8599999)

        if type == "1":
            result = TxtDocShare.deploy({'from': dev})
        elif type == "2":
            result = TokenErc20.deploy(total, name, symbol, {'from': dev})

        time.sleep(10)

        newaddress = result.address

        if len(newaddress) != 42:
            return -1

        if type == "1":
            return newaddress

        if len(newaddress) == 42:
            connectNetwork(testnet)
            network.accounts.clear()
            dev = network.accounts.add(address)
            result1 = ProxyErc20.deploy(newaddress, {'from': dev})

            time.sleep(3)

            if len(result1.address) != 42:
                return -1

            return result1.address
        else:
            return -1

    except Exception as ex:
        print(ex)
        return -1


def writecontractfile(name, add, guid, type):
    file = open("../config/contracts.txt", "a+")
    str = name + ":" + add + ":" + guid + ":" + type + "\n"
    file.write(str)
    file.close()


def getbalance(addr1, addr2, addr3):
    try:
        ether = []
        connectNetwork(inputBlockchain1)
        network.accounts.add(addr1)

        balance = network.accounts[0].balance()
        ether.append(network.web3.fromWei(balance, 'ether'))

        connectNetwork(inputBlockchain2)
        network.accounts.add(addr2)

        balance = network.accounts[0].balance()
        ether.append(network.web3.fromWei(balance, 'ether'))

        connectNetwork(inputBlockchain3)
        network.accounts.add(addr3)

        balance = network.accounts[0].balance()
        ether.append(network.web3.fromWei(balance, 'ether'))

        return ether
    except:
        return -1


def hasname(name, type):
    try:
        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 1

        Matrix = getMatrix(file, type)

        if len(Matrix) < 1:
            return 1
        else:
            hasName = 1

            for attr in Matrix:
                if attr[0][0] == name:
                    hasName = -1

            return hasName

    except:
        return -1


def getDetail(Matrix):
    connectNetwork(inputBlockchain1)
    detailToken1 = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain2)
    detailToken2 = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain3)
    detailToken3 = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailToken1[3], detailToken2[3], detailToken3[3]]
    version.sort(reverse=True)

    if version[0] == detailToken1[3]:
        return [detailToken1[0], detailToken1[1], detailToken1[2], detailToken1[3], detailToken1[4], detailToken1[5], detailToken1[6],
                detailToken1[7], nameBlockchain1]
    elif version[0] == detailToken2[3]:
        return [detailToken2[0], detailToken2[1], detailToken2[2], detailToken2[3], detailToken2[4], detailToken2[5], detailToken2[6],
                detailToken2[7], nameBlockchain2]
    else:
        return [detailToken3[0], detailToken3[1], detailToken3[2], detailToken3[3], detailToken3[4], detailToken3[5], detailToken3[6],
                detailToken3[7], nameBlockchain3]


def getBalanceOfToken(Matrix):
    connectNetwork(inputBlockchain1)
    detailToken1 = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain2)
    detailToken2 = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain3)
    detailToken3 = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailToken1[3], detailToken2[3], detailToken3[3]]
    version.sort(reverse=True)

    if version[0] == detailToken1[3]:
        balanceList = getLastBalances(Matrix, inputBlockchain1, 0)
        blockchainversion = nameBlockchain1
    elif version[0] == detailToken2[3]:
        balanceList = getLastBalances(Matrix, inputBlockchain2, 1)
        blockchainversion = nameBlockchain2
    else:
        balanceList = getLastBalances(Matrix, inputBlockchain3, 2)
        blockchainversion = nameBlockchain3

    balanceList.append(blockchainversion)

    return balanceList


def getBalanceOfTokenEsp(Matrix, address1, address2, address3, myadd):
    connectNetwork(inputBlockchain1)
    detailToken1 = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain2)
    detailToken2 = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain3)
    detailToken3 = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailToken1[3], detailToken2[3], detailToken3[3]]
    version.sort(reverse=True)

    if version[0] == detailToken1[3]:
        balanceList = getLastBalancesEsp(Matrix, inputBlockchain1, 0, address1, myadd)
        blockchainversion = nameBlockchain1
    elif version[0] == detailToken2[3]:
        balanceList = getLastBalancesEsp(Matrix, inputBlockchain2, 1, address2, myadd)
        blockchainversion = nameBlockchain2
    else:
        balanceList = getLastBalancesEsp(Matrix, inputBlockchain3, 2, address3, myadd)
        blockchainversion = nameBlockchain3

    array = [0 for i in range(3)]
    array[0] = balanceList[0]
    array[1] = balanceList[1]
    array[2] = blockchainversion

    return array


def getAllowanceOfToken(Matrix):
    connectNetwork(inputBlockchain1)
    detailToken1 = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain2)
    detailToken2 = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain3)
    detailToken3 = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailToken1[3], detailToken2[3], detailToken3[3]]
    version.sort(reverse=True)

    if version[0] == detailToken1[3]:
        allowancelist = getLastAllow(Matrix, inputBlockchain1, 0)
        testnetversion = nameBlockchain1
    elif version[0] == detailToken2[3]:
        allowancelist = getLastAllow(Matrix, inputBlockchain2, 1)
        testnetversion = nameBlockchain2
    else:
        allowancelist = getLastAllow(Matrix, inputBlockchain3, 2)
        testnetversion = nameBlockchain3

    allowancelist.append(testnetversion)

    return allowancelist


def normalizeTokenBlockChain(Matrix, address1, address2, address3, isBuy = False, blockchain = "", numOfTokens = ""):
    connectNetwork(inputBlockchain1)
    detailToken1 = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain2)
    detailToken2 = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork(inputBlockchain3)
    detailToken3 = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailToken1[3], detailToken2[3], detailToken3[3]]
    version.sort(reverse=True)

    if (version[0] == version[1]) and isBuy is False:
        return version[0]

    if blockchain == "":
        if version[0] == detailToken1[3]:
            result = normalizeBalanceAllowance(Matrix, inputBlockchain2, inputBlockchain3, address2, address3, inputBlockchain1, 0)
        elif version[0] == detailToken2[3]:
            result = normalizeBalanceAllowance(Matrix, inputBlockchain1, inputBlockchain3,  address1, address3, inputBlockchain2, 1)
        else:
            result = normalizeBalanceAllowance(Matrix, inputBlockchain2, inputBlockchain1,  address2, address1, inputBlockchain3, 2)
    else:
        if blockchain == nameBlockchain1:
            result = normalizeBuyToken(Matrix, inputBlockchain1, address1, version[0], 0, 1, numOfTokens, inputBlockchain2)
        elif blockchain == nameBlockchain2:
            result = normalizeBuyToken(Matrix, inputBlockchain2, address2, version[0], 1, 2, numOfTokens, inputBlockchain3)
        else:
            result = normalizeBuyToken(Matrix, inputBlockchain3, address3, version[0], 2, 0, numOfTokens, inputBlockchain1)

    if result == -1:
        return result
    else:
        return version[0]

    return result


def normalizeBalanceAllowance(Matrix,testnet1, testnet2, address1, address2, testnetVersion, num):
    n = 2 #n = n total - 1
    f = 1

    n1 = -1
    n2 = -1
    total = 0

    balanceList = getLastBalances(Matrix, testnetVersion, num)
    allowedList = getLastAllow(Matrix, testnetVersion, num)

    if len(balanceList) < 0 or len(allowedList) < 0:
        return -1

    while (n - f) > total:
        if n1 == -1:
            connectNetwork(testnet1)
            if testnet1 == inputBlockchain1:
                num = 0
            elif testnet1 == inputBlockchain2:
                num = 1
            else:
                num = 2
            result = setBalances(Matrix, balanceList, num, address1)
            result1 = setAllow(Matrix, allowedList, num, address1)

            if result == 1 and result1 == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork(testnet2)
            if testnet2 == inputBlockchain1:
                num = 0
            elif testnet2 == inputBlockchain2:
                num = 1
            else:
                num = 2
            result = setBalances(Matrix, balanceList, num, address2)
            result1 = setAllow(Matrix, allowedList, num, address2)

            if result == 1 and result1 == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

    return 1


def normalizeBuyToken(Matrix,testnet1, address1, version, num, num1, numTokens, testnetVersion):
    isModified = False
    balanceList = getLastBalances(Matrix, testnetVersion, num1)
    print(balanceList)
    allowedList = getLastAllow(Matrix, testnetVersion, num1)
    print(allowedList)

    if len(balanceList) < 0 or len(allowedList) < 0:
        return -1

    while isModified is False:
        connectNetwork(testnet1)
        dev = network.accounts.add(address1)
        result = setBalances(Matrix, balanceList, num, address1)
        result1 = setAllow(Matrix, allowedList, num, address1)
        bool = ProxyErc20.at(Matrix[num][1]).setTokens.call(numTokens, version - 1, {'from': dev})
        result2 = ProxyErc20.at(Matrix[num][1]).setTokens(numTokens, version - 1, {'from': dev})
        result2 = int(result2.status)


        if result == 1 and result1 == 1 and bool is True and result2 == 1:
            isModified = True

    return 1


def setBalances(Matrix, balanceList, num, address):
    dev = network.accounts.add(address)
    for x in range(len(balanceList)):
        b = balanceList[x]
        result = ProxyErc20.at(Matrix[num][1]).setBalance(b[0], b[1], (b[2] - 1), {'from': dev})
        if int(result.status) != 1:
            return -1

    return 1


def setAllow(Matrix, allowedList, num, address):
    dev = network.accounts.add(address)
    for x in range(len(allowedList)):
        a = allowedList[x]
        result = ProxyErc20.at(Matrix[num][1]).setAllowance(a[0], a[1], a[2], (a[3] - 1), {'from': dev})
        if int(result.status) != 1:
            return -1

    return 1


def getLastBalances(Matrix, testnetVersion, num):
    connectNetwork(testnetVersion)
    numOfBalances = ProxyErc20.at(Matrix[num][1]).getNumBalances()
    balanceList = []

    for x in range(numOfBalances):
        arr = ProxyErc20.at(Matrix[num][1]).getBalanceStruct(x)
        balanceList.append(arr)

    return balanceList


def getLastBalancesEsp(Matrix, testnetVersion, num, address, myadd):
    connectNetwork(testnetVersion)

    if myadd == "1":
        address = network.accounts.add(address)

    return ProxyErc20.at(Matrix[num][1]).getBalance(address)


def getLastAllow(Matrix, testnetVersion, num):
    connectNetwork(testnetVersion)
    numOfAllow = ProxyErc20.at(Matrix[num][1]).getNumAllowance()
    allowList = []

    for x in range(numOfAllow):
        arr = ProxyErc20.at(Matrix[num][1]).getAllowance(x)
        allowList.append(arr)

    return allowList


def transferTokenOwnerBlockchain(Matrix, addressK, addressG, addressR, receiverK, receiverG, receiverR, numTokens):
    version = normalizeTokenBlockChain(Matrix, addressK, addressG, addressR)

    if version == -1:
        return version

    n = 3
    f = 1
    #n = número total e f = total falha
    n1 = -1
    n2 = -1
    n3 = -1
    total = 0

    while (n - f) > total:
        if n1 == -1:
            connectNetwork(inputBlockchain1)
            dev = network.accounts.add(addressK)
            result = ProxyErc20.at(Matrix[0][1]).transferErc20(receiverK, numTokens, version, receiverK, True, {'from': dev})
            result = int(result.status)

            if result == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork(inputBlockchain2)
            dev = network.accounts.add(addressG)
            result = ProxyErc20.at(Matrix[1][1]).transferErc20(receiverG, numTokens, version, receiverG, True, {'from': dev})
            result = int(result.status)

            if result == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

        if n3 == -1:
            connectNetwork(inputBlockchain3)
            dev = network.accounts.add(addressR)
            result = ProxyErc20.at(Matrix[2][1]).transferErc20(receiverR, numTokens, version, receiverR, True, {'from': dev})
            result = int(result.status)

            if result == 1:
                n3 = result
                total = total + 1
            else:
                n3 = -1

    return total


def transferFromTokenOwnerBlockchain(Matrix, addressK, addressG, addressR, ownerK, ownerG,ownerR, receiverK, receiverG, receiverR, numTokens):
    version = normalizeTokenBlockChain(Matrix, addressK, addressG, addressR)

    if version == -1:
        return version

    n = 3
    f = 1
    #n = número total e f = total falha
    n1 = -1
    n2 = -1
    n3 = -1
    total = 0


    while (n - f) > total:
        if n1 == -1:
            connectNetwork(inputBlockchain1)
            dev = network.accounts.add(addressK)
            result = ProxyErc20.at(Matrix[0][1]).transferFromErc20(ownerK, receiverK, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork(inputBlockchain2)
            dev = network.accounts.add(addressG)
            result = ProxyErc20.at(Matrix[1][1]).transferFromErc20(ownerG, receiverG, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

        if n3 == -1:
            connectNetwork(inputBlockchain3)
            dev = network.accounts.add(addressR)
            result = ProxyErc20.at(Matrix[2][1]).transferFromErc20(ownerR, receiverR, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n3 = result
                total = total + 1
            else:
                n3 = -1

    return total


def approveBlockchain(Matrix, addressK, addressG, addressR, approveK, approveG, approveR, numTokens):
    version = normalizeTokenBlockChain(Matrix, addressK, addressG, addressR)

    if version == -1:
        return version

    n = 3
    f = 1
    #n = número total e f = total falha
    n1 = -1
    n2 = -1
    n3 = -1
    total = 0

    while (n - f) > total:
        if n1 == -1:
            connectNetwork(inputBlockchain1)
            dev = network.accounts.add(addressK)
            result = ProxyErc20.at(Matrix[0][1]).approve(approveK, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork(inputBlockchain2)
            dev = network.accounts.add(addressG)
            result = ProxyErc20.at(Matrix[1][1]).approve(approveG, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

        if n3 == -1:
            connectNetwork(inputBlockchain3)
            dev = network.accounts.add(addressR)
            result = ProxyErc20.at(Matrix[2][1]).approve(approveR, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n3 = result
                total = total + 1
            else:
                n3 = -1

    return total


def startSellBlockchain(Matrix, addressK, addressG, addressR, priceK, priceG, priceR, numTokens):
    version = normalizeTokenBlockChain(Matrix, addressK, addressG, addressR)

    if version == -1:
        return version

    n = 3
    f = 1
    #n = número total e f = total falha
    n1 = -1
    n2 = -1
    n3 = -1
    total = 0

    while (n - f) > total:
        if n1 == -1:
            connectNetwork(inputBlockchain1)
            dev = network.accounts.add(addressK)
            kovanbool = ProxyErc20.at(Matrix[0][1]).setSellTokens.call(priceK, numTokens, version, {'from': dev})
            result = ProxyErc20.at(Matrix[0][1]).setSellTokens(priceK, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork(inputBlockchain2)
            dev = network.accounts.add(addressG)
            goerlibool = ProxyErc20.at(Matrix[1][1]).setSellTokens.call(priceG, numTokens, version, {'from': dev})
            result = ProxyErc20.at(Matrix[1][1]).setSellTokens(priceG, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

        if n3 == -1:
            connectNetwork(inputBlockchain3)
            dev = network.accounts.add(addressR)
            rinkbool = ProxyErc20.at(Matrix[2][1]).setSellTokens.call(priceR, numTokens, version, {'from': dev})
            result = ProxyErc20.at(Matrix[2][1]).setSellTokens(priceR, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n3 = result
                total = total + 1
            else:
                n3 = -1

    if (rinkbool is False and goerlibool is False) or (kovanbool is False and goerlibool is False) or (rinkbool is False and kovanbool is False):
        return -1

    return total


def getDetailSell(Matrix):
    connectNetwork(inputBlockchain1)
    detailSell1 = ProxyErc20.at(Matrix[0][1]).getSellDetails()

    connectNetwork(inputBlockchain2)
    detailSell2 = ProxyErc20.at(Matrix[1][1]).getSellDetails()

    connectNetwork(inputBlockchain3)
    detailSell3 = ProxyErc20.at(Matrix[2][1]).getSellDetails()

    version = [detailSell1[3], detailSell2[3], detailSell3[3]]
    version.sort(reverse=True)


    if version[0] == detailSell1[3]:
        if detailSell1[0] == "0x0000000000000000000000000000000000000000":
            return -1
        return [detailSell1[0], detailSell1[1], detailSell1[2], detailSell1[3], detailSell1[4], detailSell1[5], detailSell1[6],
                detailSell1[7], nameBlockchain1]
    elif version[0] == detailSell2[3]:
        if detailSell2[0] == "0x0000000000000000000000000000000000000000":
            return -1
        return [detailSell2[0], detailSell2[1], detailSell2[2], detailSell2[3], detailSell2[4], detailSell2[5], detailSell2[6],
                detailSell2[7], nameBlockchain2]
    else:
        if detailSell3[0] == "0x0000000000000000000000000000000000000000":
            return -1
        return [detailSell3[0], detailSell3[1], detailSell3[2], detailSell3[3], detailSell3[4], detailSell3[5], detailSell3[6],
                detailSell3[7], nameBlockchain3]


def getDetailSellExtended(Matrix):
    connectNetwork(inputBlockchain1)
    detailSellKovan = ProxyErc20.at(Matrix[0][1]).getSellDetails()

    connectNetwork(inputBlockchain2)
    detailSellGoerli = ProxyErc20.at(Matrix[1][1]).getSellDetails()

    connectNetwork(inputBlockchain3)
    detailSellRink = ProxyErc20.at(Matrix[2][1]).getSellDetails()

    detailList = []
    count = 0

    if detailSellKovan[0] == "0x0000000000000000000000000000000000000000":
        detailList.append("-1")
        count = count + 1
    else:
        detailList.append(detailSellKovan)

    if detailSellGoerli[0] == "0x0000000000000000000000000000000000000000":
        detailList.append("-1")
        count = count + 1
    else:
        detailList.append(detailSellGoerli)

    if detailSellRink[0] == "0x0000000000000000000000000000000000000000":
        detailList.append("-1")
        count = count + 1
    else:
        detailList.append(detailSellRink)

    if count > 1:
        return -1

    return detailList


def getBalanceExceedsBlockchain(Matrix, addressK, addressG, addressR):
    connectNetwork(inputBlockchain1)
    dev = network.accounts.add(addressK)
    balanceKovan = ProxyErc20.at(Matrix[0][1]).getMyBalanceExceed.call({'from': dev})

    connectNetwork(inputBlockchain2)
    dev = network.accounts.add(addressG)
    balanceGoerli = ProxyErc20.at(Matrix[1][1]).getMyBalanceExceed.call({'from': dev})

    connectNetwork(inputBlockchain3)
    dev = network.accounts.add(addressR)
    balanceRink = ProxyErc20.at(Matrix[2][1]).getMyBalanceExceed.call({'from': dev})

    list = []
    list.append(balanceKovan)
    list.append(balanceGoerli)
    list.append(balanceRink)

    return list


def BuyTokenBlockchain(Matrix, addressK, addressG, addressR, money):
    arrayDetail = getDetailSellExtended(Matrix)
    version = normalizeTokenBlockChain(Matrix, addressK, addressG, addressR)

    if version == -1:
        return version

    n = 3
    f = 1
    #n = número total e f = total falha
    n1 = -1
    n2 = -1
    n3 = -1
    total = 0
    randomNumList = [0, 1, 2]

    while (n - f) > total:
        randomBlock = random.choice(randomNumList)
        if n1 == -1 and total < 2 and randomBlock == 0:
            connectNetwork(inputBlockchain1)
            dev = network.accounts.add(addressK)
            amount = math.ceil(arrayDetail[0][2] * money)
            result = dev.transfer(Matrix[0][1], amount)
            result = int(result.status)

            if result == 1:
                n1 = 1
                total = total + 1
                randomNumList.remove(randomBlock)
            else:
                n1 = -1

        if n2 == -1 and total < 2 and randomBlock == 1:
            connectNetwork(inputBlockchain2)
            dev = network.accounts.add(addressG)
            amount = math.ceil(arrayDetail[1][2] * money)
            result = dev.transfer(Matrix[1][1], amount)
            result = int(result.status)

            if result == 1:
                n2 = 1
                total = total + 1
                randomNumList.remove(randomBlock)
            else:
                n2 = -1

        if n3 == -1 and total < 2 and randomBlock == 2:
            connectNetwork(inputBlockchain3)
            dev = network.accounts.add(addressR)
            amount = math.ceil(arrayDetail[2][2] * money)
            result = dev.transfer(Matrix[2][1], amount)
            result = int(result.status)

            if result == 1:
                n3 = result
                total = total + 1
                randomNumList.remove(randomBlock)
            else:
                n3 = -1

    addressK = os.getenv('PRIVATE_KEY_K')
    addressG = os.getenv('PRIVATE_KEY')
    addressR = os.getenv('PRIVATE_KEY_R')
    numTokens = arrayDetail[0][1] - money

    if randomNumList[0] == 0:
        normalizeTokenBlockChain(Matrix, addressK, addressG, addressR, True, nameBlockchain1, numTokens)
    elif randomNumList[0] == 1:
        normalizeTokenBlockChain(Matrix, addressK, addressG, addressR, True, nameBlockchain2, numTokens)
    else:
        normalizeTokenBlockChain(Matrix, addressK, addressG, addressR, True, nameBlockchain3, numTokens)

    return total


def withdrawmoneyblockchain(Matrix, addressK, addressG, addressR, value, to, blockchain):
    version = normalizeTokenBlockChain(Matrix, addressK, addressG, addressR)

    if version == -1:
        return version

    if blockchain == 1:
        num = 0
        testnet = inputBlockchain1
        address = addressK
    elif blockchain == 2:
        num = 1
        testnet = inputBlockchain2
        address = addressG
    else:
        num = 2
        testnet = inputBlockchain3
        address = addressR

    connectNetwork(testnet)
    dev = network.accounts.add(address)

    if to == "me":
        to = dev

    result = ProxyErc20.at(Matrix[num][1]).withdrawMoney.call(to, value, {'from': dev})
    result1 = ProxyErc20.at(Matrix[num][1]).withdrawMoney(to, value, {'from': dev})

    if int(result1.status) == 1:
        return result

    return False


def setPriceTokenBlockchain(Matrix, addressK, addressG, addressR, priceK, priceG, priceR):
    version = normalizeTokenBlockChain(Matrix, addressK, addressG, addressR)

    if version == -1:
        return version

    n = 3
    f = 1
    #n = número total e f = total falha
    n1 = -1
    n2 = -1
    n3 = -1
    total = 0

    while (n - f) > total:
        if n1 == -1:
            connectNetwork(inputBlockchain1)
            dev = network.accounts.add(addressK)
            result = ProxyErc20.at(Matrix[0][1]).setPriceForToken.call(priceK, version, {'from': dev})
            result1 = ProxyErc20.at(Matrix[0][1]).setPriceForToken(priceK, version, {'from': dev})
            result1 = int(result1.status)

            if result is True and result1 == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork(inputBlockchain2)
            dev = network.accounts.add(addressG)
            result = ProxyErc20.at(Matrix[1][1]).setPriceForToken.call(priceG, version, {'from': dev})
            result1 = ProxyErc20.at(Matrix[1][1]).setPriceForToken(priceG, version, {'from': dev})
            result1 = int(result1.status)

            if result is True and result1 == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

        if n3 == -1:
            connectNetwork(inputBlockchain3)
            dev = network.accounts.add(addressR)
            result = ProxyErc20.at(Matrix[2][1]).setPriceForToken.call(priceR, version, {'from': dev})
            result1 = ProxyErc20.at(Matrix[2][1]).setPriceForToken(priceR, version, {'from': dev})
            result1 = int(result1.status)

            if result is True and result1 == 1:
                n3 = result
                total = total + 1
            else:
                n3 = -1

    return total


def setNumTokenBlockchain(Matrix, addressK, addressG, addressR, num):
    version = normalizeTokenBlockChain(Matrix, addressK, addressG, addressR)

    if version == -1:
        return version

    if int(num) <= 0:
        return -1

    n = 3
    f = 1
    #n = número total e f = total falha
    n1 = -1
    n2 = -1
    n3 = -1
    total = 0

    while (n - f) > total:
        if n1 == -1:
            connectNetwork(inputBlockchain1)
            dev = network.accounts.add(addressK)
            kovanbool = ProxyErc20.at(Matrix[0][1]).setTokens.call(num, version, {'from': dev})
            result1 = ProxyErc20.at(Matrix[0][1]).setTokens(num, version, {'from': dev})
            result1 = int(result1.status)

            if result1 == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork(inputBlockchain2)
            dev = network.accounts.add(addressG)
            goerlibool = ProxyErc20.at(Matrix[1][1]).setTokens.call(num, version, {'from': dev})
            result1 = ProxyErc20.at(Matrix[1][1]).setTokens(num, version, {'from': dev})
            result1 = int(result1.status)

            if result1 == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

        if n3 == -1:
            connectNetwork(inputBlockchain3)
            dev = network.accounts.add(addressR)
            rinkbool = ProxyErc20.at(Matrix[2][1]).setTokens.call(num, version, {'from': dev})
            result1 = ProxyErc20.at(Matrix[2][1]).setTokens(num, version, {'from': dev})
            result1 = int(result1.status)

            if result1 == 1:
                n3 = 1
                total = total + 1
            else:
                n3 = -1

    if (rinkbool is False and goerlibool is False) or (kovanbool is False and goerlibool is False) or (rinkbool is False and kovanbool is False):
        return -1

    return total


class AddFilePost(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('docname', required=True)
        parser.add_argument('text', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "1")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = addFile(MatrixContract, args['docname'], args['text'], args['addressK'], args['addressG'],
                                 args['addressR'])

                if result == 1:
                    return 200

                return 400

            except Exception as exc:
                print(exc)
                return 400

    pass


class GetContract(Resource):
    def get(self):
        contractJson = getJsonContract()

        if contractJson == "[]":
            return 404
        else:
            return make_response(jsonify(contractJson), 200)

    pass


class GetContractAdd(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', required=True)
        args = parser.parse_args()

        contractDocJson = getJsonContractDocBlock(args['type'])

        if contractDocJson == -1 or contractDocJson == "[]":
            return 404
        else:
            return make_response(jsonify(contractDocJson), 200)

    pass


class PublishContractPost(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('symbol', required=False)
        parser.add_argument('total', required=False)
        args = parser.parse_args()

        result = publishcontract(args['ncontract'], args['name'], args['addressK'], args['addressG'], args['addressR'], args['symbol'], args['total'])

        if result == -1:
            return -1
        else:
            return 1

    pass


class NameIsAvaliable(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('type', required=True)
        args = parser.parse_args()

        if args['type'] != "1" and args['type'] != "2":
            return -1

        result = hasname(args['name'], args['type'])

        if result == -1:
            return -1
        else:
            return 1

    pass


class GetAllDocs(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "1")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = getAllFiles(MatrixContract)

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class GetDoc(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('iddoc', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "1")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = getSingleFile(MatrixContract, int(args['iddoc']))

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class EditDoc(Resource):

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('iddoc', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('docname', required=False)
        parser.add_argument('text', required=False)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "1")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = editFile(MatrixContract, int(args['iddoc']), args['docname'], args['text'], args['addressK'],
                                  args['addressG'], args['addressR'])

                if result == -2:
                    return 404
                elif result == -1:
                    return 400
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class GetBalance(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        args = parser.parse_args()

        try:
            result = getbalance(args['addressK'], args['addressG'], args['addressR'])

            if result == -1:
                return 400
            else:
                return make_response(jsonify(result), 200)

        except Exception as exc:
            print(exc)
            return 400

    pass


class Online(Resource):
    def get(self):
        return 200


class GetAllTokens(Resource):
    def get(self):
        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < 1:
                    return 404

                return make_response(jsonify(Matrix), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class GetDetailsToken(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = getDetail(MatrixContract)

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class GetAddress(Resource):
    def get(self):
        add = getAddress()

        if add == "[]":
            return 404
        else:
            return make_response(jsonify(add), 200)

    pass


class GetBalanceToken(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = getBalanceOfToken(MatrixContract)

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class GetBalanceTokenEsp(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('myadd', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = getBalanceOfTokenEsp(MatrixContract, args['addressK'], args['addressG'], args['addressR'], args['myadd'])

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class TransferToken(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('receiverK', required=True)
        parser.add_argument('receiverG', required=True)
        parser.add_argument('receiverR', required=True)
        parser.add_argument('numTokens', required=True)

        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = transferTokenOwnerBlockchain(MatrixContract, args['addressK'], args['addressG'], args['addressR'],
                                            args['receiverK'], args['receiverG'], args['receiverR'], args['numTokens'])

                if result == -1:
                    return 400
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class TransferTokenFrom(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('ownerK', required=True)
        parser.add_argument('ownerG', required=True)
        parser.add_argument('ownerR', required=True)
        parser.add_argument('receiverK', required=True)
        parser.add_argument('receiverG', required=True)
        parser.add_argument('receiverR', required=True)
        parser.add_argument('numTokens', required=True)

        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = transferFromTokenOwnerBlockchain(MatrixContract, args['addressK'], args['addressG'], args['addressR'],
                                                          args['ownerK'], args['ownerG'], args['ownerR'],
                                                          args['receiverK'], args['receiverG'], args['receiverR'], args['numTokens'])

                if result == -1:
                    return 400
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class Approve(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('delegateK', required=True)
        parser.add_argument('delegateG', required=True)
        parser.add_argument('delegateR', required=True)
        parser.add_argument('numTokens', required=True)

        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = approveBlockchain(MatrixContract, args['addressK'], args['addressG'], args['addressR'],
                                                          args['delegateK'], args['delegateG'], args['delegateR'], args['numTokens'])

                if result == -1:
                    return 400
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class Allowance(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = getAllowanceOfToken(MatrixContract)

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class StartSell(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('priceK', required=True)
        parser.add_argument('priceG', required=True)
        parser.add_argument('priceR', required=True)
        parser.add_argument('numOfTokens', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = startSellBlockchain(MatrixContract, args['addressK'], args['addressG'], args['addressR'], int(args['priceK']),
                                             int(args['priceG']), int(args['priceR']), int(args['numOfTokens']))

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class GetDetailsSell(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                result = getDetailSellExtended(MatrixContract)

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class BuyToken(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('money', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                if getDetailSell(MatrixContract) == -1:
                    return 404

                result = BuyTokenBlockchain(MatrixContract, args['addressK'], args['addressG'], args['addressR'], int(args['money']))

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                return 400

    pass


class GetBalanceExceeds(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                if getDetailSell(MatrixContract) == -1:
                    return 404

                result = getBalanceExceedsBlockchain(MatrixContract, args['addressK'], args['addressG'], args['addressR'])

                if result == -1:
                    return 404
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class WithdrawMoney(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('value', required=True)
        parser.add_argument('to', required=True)
        parser.add_argument('blockchain', required=True)
        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                if getDetailSell(MatrixContract) == -1:
                    return 404

                result = withdrawmoneyblockchain(MatrixContract, args['addressK'], args['addressG'], args['addressR'], int(args['value']), args['to'], int(args['blockchain']))

                if result is False:
                    return 400
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class SetPriceToken(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('priceK', required=True)
        parser.add_argument('priceG', required=True)
        parser.add_argument('priceR', required=True)

        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                if getDetailSell(MatrixContract) == -1:
                    return 404

                result = setPriceTokenBlockchain(MatrixContract, args['addressK'], args['addressG'], args['addressR'],
                                            int(args['priceK']), int(args['priceG']), int(args['priceR']))

                if result == -1:
                    return 400
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


class SetNumToken(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ncontract', required=True)
        parser.add_argument('addressK', required=True)
        parser.add_argument('addressG', required=True)
        parser.add_argument('addressR', required=True)
        parser.add_argument('num', required=True)

        args = parser.parse_args()

        configFile = '../config/contracts.txt'
        # readmode +, if do not exists, create a new one
        file = open(configFile, 'r+')

        if os.path.getsize(configFile) == 0:
            return 404
        else:
            Matrix = getMatrix(file, "2")

            try:
                if len(Matrix) < int(args['ncontract']):
                    return 404

                MatrixContract = Matrix[int(args['ncontract'])]

                if getDetailSell(MatrixContract) == -1:
                    return 404

                result = setNumTokenBlockchain(MatrixContract, args['addressK'], args['addressG'], args['addressR'],
                                            int(args['num']))

                if result == -1:
                    return 400
                else:
                    return make_response(jsonify(result), 200)

            except Exception as exc:
                print(exc)
                return 400

    pass


api.add_resource(NameIsAvaliable, '/hasname')
api.add_resource(PublishContractPost, '/publishcontract')
api.add_resource(AddFilePost, '/addfile')
api.add_resource(GetContract, '/getcontract')
api.add_resource(GetContractAdd, '/getcontractadd')
api.add_resource(GetAllDocs, '/getalldocs')
api.add_resource(GetDoc, '/getdoc')
api.add_resource(EditDoc, '/editdoc')
api.add_resource(GetBalance, '/getbalance')
api.add_resource(Online, '/online')
api.add_resource(GetAllTokens, '/getalltokens')
api.add_resource(GetDetailsToken, '/gettokendetail')
api.add_resource(GetAddress, '/getaddress')
api.add_resource(GetBalanceToken, '/gettokenbalance')
api.add_resource(GetBalanceTokenEsp, '/gettokenbalanceesp')
api.add_resource(TransferToken, '/transfertoken')
api.add_resource(TransferTokenFrom, '/transfertokenfrom')
api.add_resource(Approve, '/approve')
api.add_resource(Allowance, '/getallowance')
api.add_resource(StartSell, '/startsell')
api.add_resource(GetDetailsSell, '/getdetailssell')
api.add_resource(BuyToken, '/buytoken')
api.add_resource(GetBalanceExceeds, '/getbalanceexceeds')
api.add_resource(WithdrawMoney, '/withdrawmoney')
api.add_resource(SetPriceToken, '/setpricetoken')
api.add_resource(SetNumToken, '/setnumtoken')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
