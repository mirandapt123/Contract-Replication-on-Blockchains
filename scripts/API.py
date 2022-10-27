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


def addFile(Matrix, docname, text, addressK, addressG, addressR):
    if docname and text:
        fileIDKovan = asyncio.run(addFileBlockChain(Matrix[0][1], "kovan", docname, text, addressK))
        if fileIDKovan > -1:
            fileIDGoerli = asyncio.run(addFileBlockChain(Matrix[1][1], "goerli", docname, text, addressG))
            if fileIDGoerli > -1:
                fileIDRinkeby = asyncio.run(addFileBlockChain(Matrix[2][1], "rinkeby", docname, text, addressR))
                if fileIDRinkeby > -1:
                    return 1
                else:
                    fileReverter(Matrix[0][1], "kovan", fileIDKovan, addressK)
                    fileReverter(Matrix[1][1], "goerli", fileIDGoerli, addressG)
                    return -1
            else:
                fileReverter(Matrix[0][1], "kovan", fileIDKovan, addressK)
                return -1
        else:
            return -1
    else:
        return -1


def fileReverter(address, testnet, id, addressacc):
    connectNetwork(testnet)

    if testnet == "kovan":
        dev = network.accounts.add(addressacc)
    elif testnet == "goerli":
        dev = network.accounts.add(addressacc)
    else:
        dev = network.accounts.add(addressacc)

    contract = TxtDocShare.at(address)

    contract.setStatus(id, {'from': dev})


async def addFileBlockChain(address, testnet, filename, text, accAddress):
    connectNetwork(testnet)

    if testnet == "kovan":
        dev = network.accounts.add(accAddress)
    elif testnet == "goerli":
        dev = network.accounts.add(accAddress)
    else:
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
    connectNetwork('kovan')
    numKovan = TxtDocShare.at(Matrix[0][1]).getNumDocs()

    connectNetwork('goerli')
    numGoerli = TxtDocShare.at(Matrix[1][1]).getNumDocs()

    connectNetwork('rinkeby')
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
    connectNetwork('kovan')
    docKovan = TxtDocShare.at(Matrix[0][1]).getDoc(idDoc)

    connectNetwork('goerli')
    docGoerli = TxtDocShare.at(Matrix[1][1]).getDoc(idDoc)

    connectNetwork('rinkeby')
    docRink = TxtDocShare.at(Matrix[2][1]).getDoc(idDoc)

    lastupd = [datetime.fromtimestamp(docGoerli[6]), datetime.fromtimestamp(docKovan[6]),
               datetime.fromtimestamp(docRink[6])]
    lastupd.sort(reverse=True)

    if lastupd[0] == datetime.fromtimestamp(docKovan[6]):
        return [docKovan[0], docKovan[1], docKovan[2], docKovan[3], docKovan[4], docKovan[5], docKovan[6], "Kovan"]
    elif lastupd[0] == datetime.fromtimestamp(docGoerli[6]):
        return [docGoerli[0], docGoerli[1], docGoerli[2], docGoerli[3], docGoerli[4], docGoerli[5], docGoerli[6],
                "Goerli"]
    else:
        return [docRink[0], docRink[1], docRink[2], docRink[3], docRink[4], docRink[5], docRink[6], "Rinkeby"]


def getSingleFile(Matrix, idDoc):
    if idDoc < 0:
        return -1

    doc = getLastDoc(idDoc, Matrix)

    if not str(doc[0]):
        return -1

    return doc


def editDocBlockchain(Matrix, idDoc, docname, text, addressK, addressG, addressR, currentdocname, currenttext, version):
    if not docname and not text:
        return -1

    if not docname:
        docname = currentdocname

    if not text:
        text = currenttext
    #n = número total e f = total falha
    statusK = -1
    statusR = -1
    statusG = -1
    edit = -1

    while (statusK == -1 and statusR == -1) or (statusR == -1 and statusG == -1) or (statusK == -1 and statusG == -1):
        if statusK == -1:
            connectNetwork('kovan')
            dev = network.accounts.add(addressK)
            result = TxtDocShare.at(Matrix[0][1]).editDoc(idDoc, docname, text, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                statusK = 1
            else:
                statusK = -1

            if statusK != -1:
                edit = edit + 1

        if statusG== -1:
            connectNetwork('goerli')
            dev = network.accounts.add(addressG)
            result = TxtDocShare.at(Matrix[1][1]).editDoc(idDoc, docname, text, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                statusG = 1
            else:
                statusG = -1

            if statusG != -1:
                edit = edit + 1

        if statusR == -1:
            connectNetwork('rinkeby')
            dev = network.accounts.add(addressR)
            result = TxtDocShare.at(Matrix[2][1]).editDoc(idDoc, docname, text, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                statusR = result
            else:
                statusR = -1

            if statusR != -1:
                edit = edit + 1

        return edit


def editFile(Matrix, idDoc, docname, text, addressK, addressG, addressR):
    if idDoc < 0:
        return -2

    doc = getLastDoc(idDoc, Matrix)

    if not str(doc[0]):
        return -2

    result = editDocBlockchain(Matrix, idDoc, docname, text, addressK, addressG, addressR, doc[0], doc[1], int(doc[2]))

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


def publishcontract(ncontract, contractname, addressK, addressG, addressR, symbol = "", total = ""):
    contractarr = glob.glob("../contracts/*.sol")
    contractarr.remove("../contracts/proxyErc20.sol")

    try:
        if contractarr[int(ncontract) - 1].find("../contracts/txtDocShare.sol") != -1:
            if hasname(contractname, "1") == -1:
                return -1

            publishbrownie(contractarr[int(ncontract) - 1], contractname, "1", addressK, addressG,
                           addressR)
            return 1
        elif contractarr[int(ncontract) - 1].find("../contracts/tokenErc20.sol") != -1:
            if hasname(contractname, "2") == -1:
                return -1
            elif symbol == "" or total == "":
                return -1

            publishbrownie(contractarr[int(ncontract) - 1], contractname, "2", addressK, addressG,
                           addressR, symbol, total)


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


def publishbrownie(name, contract, type, addressK, addressG, addressR, symbol = "", total = ""):
    try:
        strguid = getGuid()
        add = asyncio.run(subpublishbrownie("kovan", contract, type, addressK, symbol, total))

        if len(add) == 42:
            writecontractfile(contract, add, strguid, type)
            add = asyncio.run(subpublishbrownie("goerli", contract, type, addressG, symbol, total))
            if len(add) == 42:
                writecontractfile(contract, add, strguid, type)
                add = asyncio.run(subpublishbrownie("rinkeby", contract, type, addressR, symbol, total))
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

        network.gas_limit(8599999)

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


def getbalance(addrK, addrG, addrR):
    try:
        ether = []
        connectNetwork("kovan")
        network.accounts.add(addrK)

        balance = network.accounts[0].balance()
        ether.append(network.web3.fromWei(balance, 'ether'))

        connectNetwork("goerli")
        network.accounts.add(addrG)

        balance = network.accounts[0].balance()
        ether.append(network.web3.fromWei(balance, 'ether'))

        connectNetwork("rinkeby")
        network.accounts.add(addrR)

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
    connectNetwork('kovan')
    detailTokenKovan = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork('goerli')
    detailTokenGoerli = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork('rinkeby')
    detailTokenRink = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailTokenKovan[3], detailTokenGoerli[3], detailTokenRink[3]]
    version.sort(reverse=True)

    if version[0] == detailTokenKovan[3]:
        return [detailTokenKovan[0], detailTokenKovan[1], detailTokenKovan[2], detailTokenKovan[3], detailTokenKovan[4], detailTokenKovan[5], detailTokenKovan[6],
                detailTokenKovan[7], "Kovan"]
    elif version[0] == detailTokenGoerli[3]:
        return [detailTokenGoerli[0], detailTokenGoerli[1], detailTokenGoerli[2], detailTokenGoerli[3], detailTokenGoerli[4], detailTokenGoerli[5], detailTokenGoerli[6],
                detailTokenGoerli[7], "Goerli"]
    else:
        return [detailTokenRink[0], detailTokenRink[1], detailTokenRink[2], detailTokenRink[3], detailTokenRink[4], detailTokenRink[5], detailTokenRink[6],
                detailTokenRink[7], "Rinkeby"]


def getBalanceOfToken(Matrix):
    connectNetwork('kovan')
    detailTokenKovan = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork('goerli')
    detailTokenGoerli = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork('rinkeby')
    detailTokenRink = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailTokenKovan[3], detailTokenGoerli[3], detailTokenRink[3]]
    version.sort(reverse=True)

    if version[0] == detailTokenKovan[3]:
        balanceList = getLastBalances(Matrix, "kovan", 0)
        testnetversion = "Kovan"
    elif version[0] == detailTokenGoerli[3]:
        balanceList = getLastBalances(Matrix, "goerli", 1)
        testnetversion = "Goerli"
    else:
        balanceList = getLastBalances(Matrix, "rinkeby", 2)
        testnetversion = "Rinkeby"

    balanceList.append(testnetversion)

    return balanceList


def getBalanceOfTokenEsp(Matrix, addressK, addressG, addressR, myadd):
    connectNetwork('kovan')
    detailTokenKovan = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork('goerli')
    detailTokenGoerli = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork('rinkeby')
    detailTokenRink = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailTokenKovan[3], detailTokenGoerli[3], detailTokenRink[3]]
    version.sort(reverse=True)

    if version[0] == detailTokenKovan[3]:
        balanceList = getLastBalancesEsp(Matrix, "kovan", 0, addressK, myadd)
        testnetversion = "Kovan"
    elif version[0] == detailTokenGoerli[3]:
        balanceList = getLastBalancesEsp(Matrix, "goerli", 1, addressG, myadd)
        testnetversion = "Goerli"
    else:
        balanceList = getLastBalancesEsp(Matrix, "rinkeby", 2, addressR, myadd)
        testnetversion = "Rinkeby"

    array = [0 for i in range(3)]
    array[0] = balanceList[0]
    array[1] = balanceList[1]
    array[2] = testnetversion

    return array


def getAllowanceOfToken(Matrix):
    connectNetwork('kovan')
    detailTokenKovan = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork('goerli')
    detailTokenGoerli = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork('rinkeby')
    detailTokenRink = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailTokenKovan[3], detailTokenGoerli[3], detailTokenRink[3]]
    version.sort(reverse=True)

    if version[0] == detailTokenKovan[3]:
        allowancelist = getLastAllow(Matrix, "kovan", 0)
        testnetversion = "Kovan"
    elif version[0] == detailTokenGoerli[3]:
        allowancelist = getLastAllow(Matrix, "goerli", 1)
        testnetversion = "Goerli"
    else:
        allowancelist = getLastAllow(Matrix, "rinkeby", 2)
        testnetversion = "Rinkeby"

    allowancelist.append(testnetversion)

    return allowancelist


def normalizeTokenBlockChain(Matrix, addressK, addressG, addressR, isBuy = False, blockchain = "", numOfTokens = ""):
    connectNetwork('kovan')
    detailTokenKovan = ProxyErc20.at(Matrix[0][1]).getNameSymbolSupply()

    connectNetwork('goerli')
    detailTokenGoerli = ProxyErc20.at(Matrix[1][1]).getNameSymbolSupply()

    connectNetwork('rinkeby')
    detailTokenRink = ProxyErc20.at(Matrix[2][1]).getNameSymbolSupply()

    version = [detailTokenKovan[3], detailTokenGoerli[3], detailTokenRink[3]]
    version.sort(reverse=True)

    if (version[0] == version[1]) and isBuy is False:
        return version[0]

    if blockchain == "":
        if version[0] == detailTokenKovan[3]:
            result = normalizeBalanceAllowance(Matrix, "goerli", "rinkeby", addressG, addressR, "kovan", 0)
        elif version[0] == detailTokenGoerli[3]:
            result = normalizeBalanceAllowance(Matrix, "kovan", "rinkeby",  addressK, addressR, "goerli", 1)
        else:
            result = normalizeBalanceAllowance(Matrix, "goerli", "kovan",  addressG, addressK, "rinkeby", 2)
    else:
        if blockchain == "Kovan":
            result = normalizeBuyToken(Matrix, "kovan", addressK, version[0], 0, 1, numOfTokens, "goerli")
        elif blockchain == "Goerli":
            result = normalizeBuyToken(Matrix, "goerli", addressG, version[0], 1, 2, numOfTokens, "rinkeby")
        else:
            result = normalizeBuyToken(Matrix, "rinkeby", addressR, version[0], 2, 0, numOfTokens, "kovan")

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
            if testnet1 == "kovan":
                num = 0
            elif testnet1 == "goerli":
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
            if testnet2 == "kovan":
                num = 0
            elif testnet2 == "goerli":
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
            connectNetwork('kovan')
            dev = network.accounts.add(addressK)
            result = ProxyErc20.at(Matrix[0][1]).transferErc20(receiverK, numTokens, version, receiverK, True, {'from': dev})
            result = int(result.status)

            if result == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork('goerli')
            dev = network.accounts.add(addressG)
            result = ProxyErc20.at(Matrix[1][1]).transferErc20(receiverG, numTokens, version, receiverG, True, {'from': dev})
            result = int(result.status)

            if result == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

        if n3 == -1:
            connectNetwork('rinkeby')
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
            connectNetwork('kovan')
            dev = network.accounts.add(addressK)
            result = ProxyErc20.at(Matrix[0][1]).transferFromErc20(ownerK, receiverK, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork('goerli')
            dev = network.accounts.add(addressG)
            result = ProxyErc20.at(Matrix[1][1]).transferFromErc20(ownerG, receiverG, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

        if n3 == -1:
            connectNetwork('rinkeby')
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
            connectNetwork('kovan')
            dev = network.accounts.add(addressK)
            result = ProxyErc20.at(Matrix[0][1]).approve(approveK, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n1 = 1
                total = total + 1
            else:
                n1 = -1

        if n2 == -1:
            connectNetwork('goerli')
            dev = network.accounts.add(addressG)
            result = ProxyErc20.at(Matrix[1][1]).approve(approveG, numTokens, version, {'from': dev})
            result = int(result.status)

            if result == 1:
                n2 = 1
                total = total + 1
            else:
                n2 = -1

        if n3 == -1:
            connectNetwork('rinkeby')
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
            connectNetwork('kovan')
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
            connectNetwork('goerli')
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
            connectNetwork('rinkeby')
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
    connectNetwork('kovan')
    detailSellKovan = ProxyErc20.at(Matrix[0][1]).getSellDetails()

    connectNetwork('goerli')
    detailSellGoerli = ProxyErc20.at(Matrix[1][1]).getSellDetails()

    connectNetwork('rinkeby')
    detailSellRink = ProxyErc20.at(Matrix[2][1]).getSellDetails()

    version = [detailSellKovan[3], detailSellGoerli[3], detailSellRink[3]]
    version.sort(reverse=True)


    if version[0] == detailSellKovan[3]:
        if detailSellKovan[0] == "0x0000000000000000000000000000000000000000":
            return -1
        return [detailSellKovan[0], detailSellKovan[1], detailSellKovan[2], detailSellKovan[3], detailSellKovan[4], detailSellKovan[5], detailSellKovan[6],
                detailSellKovan[7], "Kovan"]
    elif version[0] == detailSellGoerli[3]:
        if detailSellGoerli[0] == "0x0000000000000000000000000000000000000000":
            return -1
        return [detailSellGoerli[0], detailSellGoerli[1], detailSellGoerli[2], detailSellGoerli[3], detailSellGoerli[4], detailSellGoerli[5], detailSellGoerli[6],
                detailSellGoerli[7], "Goerli"]
    else:
        if detailSellRink[0] == "0x0000000000000000000000000000000000000000":
            return -1
        return [detailSellRink[0], detailSellRink[1], detailSellRink[2], detailSellRink[3], detailSellRink[4], detailSellRink[5], detailSellRink[6],
                detailSellRink[7], "Rinkeby"]


def getDetailSellExtended(Matrix):
    connectNetwork('kovan')
    detailSellKovan = ProxyErc20.at(Matrix[0][1]).getSellDetails()

    connectNetwork('goerli')
    detailSellGoerli = ProxyErc20.at(Matrix[1][1]).getSellDetails()

    connectNetwork('rinkeby')
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
    connectNetwork('kovan')
    dev = network.accounts.add(addressK)
    balanceKovan = ProxyErc20.at(Matrix[0][1]).getMyBalanceExceed.call({'from': dev})

    connectNetwork('goerli')
    dev = network.accounts.add(addressG)
    balanceGoerli = ProxyErc20.at(Matrix[1][1]).getMyBalanceExceed.call({'from': dev})

    connectNetwork('rinkeby')
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
            connectNetwork('kovan')
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
            connectNetwork('goerli')
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
            connectNetwork('rinkeby')
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
        normalizeTokenBlockChain(Matrix, addressK, addressG, addressR, True, "Kovan", numTokens)
    elif randomNumList[0] == 1:
        normalizeTokenBlockChain(Matrix, addressK, addressG, addressR, True, "Goerli", numTokens)
    else:
        normalizeTokenBlockChain(Matrix, addressK, addressG, addressR, True, "Rinkeby", numTokens)

    return total


def withdrawmoneyblockchain(Matrix, addressK, addressG, addressR, value, to, blockchain):
    version = normalizeTokenBlockChain(Matrix, addressK, addressG, addressR)

    if version == -1:
        return version

    if blockchain == 1:
        num = 0
        testnet = "kovan"
        address = addressK
    elif blockchain == 2:
        num = 1
        testnet = "goerli"
        address = addressG
    else:
        num = 2
        testnet = "rinkeby"
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
            connectNetwork('kovan')
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
            connectNetwork('goerli')
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
            connectNetwork('rinkeby')
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
            connectNetwork('kovan')
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
            connectNetwork('goerli')
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
            connectNetwork('rinkeby')
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
