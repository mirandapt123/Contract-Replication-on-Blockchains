#!/usr/bin/python3
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

p = brownie.project.load('/home/miranda/BrownieTeseProject', name="Tese")
p.load_config()
from brownie.project.Tese import TxtDocShare
import brownie.network as network


def menu():
    option = 0
    while int(option) != 9:
        print(
            "\n1 - Publicar contrato \n2 - Gerir documentos\n3 - Gerir token\n4 - Obter o balanço atual\n5 - Alterar private key/Infura ID\n9 - Sair.")
        option = switcher(input("Digite a sua opção: "))

def menuFile():
    option = 0

    try:
        while int(option) != 9:
            print(
                "\n1 - Adicionar documento. \n2 - Obter todos os documentos.\n3 - Obter um documento.\n4 - Editar um documento.\n9 - Voltar ao menu anterior.")
            option = input("Digite a sua opção: ")

            if int(option) == 1:
                openAddrFile("1", 1)
            elif int(option) == 2:
                openAddrFile("1", 2)
            elif int(option) == 3:
                openAddrFile("1", 3)
            elif int(option) == 4:
                openAddrFile("1", 4)
            elif int(option) == 9:
                print("\nA voltar ao menu principal.")
            else:
                print("\nOpção não reconhecida.")
    except:
        print("\nOpção não reconhecida/Ocorreu um erro. A voltar ao menu principal.")

def switcher(option):
    try:
        if int(option) == 1:
            publishcontract()
            return 1
        elif int(option) == 2:
            menuFile()
            return 2
        elif int(option) == 3:
            print("Opção número 3\n")
            return 3
        elif int(option) == 4:
            getbalance()
            return 4
        elif int(option) == 5:
            print("\nA abrir o ficheiro de configurações da private key/Infura ID.")
            os.system('vim ../.env')
            return 5
        elif int(option) == 9:
            print("\nAté uma próxima.")
            return 9
        else:
            print("\nOpção não reconhecida\n")
            return 0
    except:
        print("\nOcorreu um erro, tente novamente.\n")
        return 0

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

def addFile(Matrix):
    filename = input("Digite o nome do documento: ")
    text = input("Digite o texto do documento: ")

    if filename and text:
        fileIDKovan = addFileBlockChain(Matrix[0][1], "kovan", filename, text)
        if fileIDKovan > -1:
            fileIDGoerli = addFileBlockChain(Matrix[1][1], "goerli", filename, text)
            if fileIDGoerli > -1:
                fileIDRinkeby = addFileBlockChain(Matrix[2][1], "rinkeby", filename, text)
                if fileIDRinkeby > -1:
                    print("\nO documento foi adicionado com sucesso nas três testnets.")
                else:
                    print("Não foi possível adicionar o documento após 5 tentativas na blockchain 'rinkeby'. Tente novamente.")
                    fileReverter(Matrix[0][1], "kovan", fileIDKovan)
                    fileReverter(Matrix[1][1], "goerli", fileIDGoerli)
            else:
                print("Não foi possível adicionar o documento após 5 tentativas na blockchain 'goerli'. Tente novamente.")
                fileReverter(Matrix[0][1],"kovan", fileIDKovan)
        else:
            print("Não foi possível adicionar o documento após 5 tentativas na blockchain 'kovan'. Tente novamente.")
    else:
        print("\nTem de digitar um nome e um texto para o documento.")

def fileReverter(address, testnet, id):
    if network.is_connected():
        network.disconnect()

    network.connect(testnet)

    if testnet == "kovan":
        dev = network.accounts.add(os.getenv('PRIVATE_KEY_K'))
    elif testnet == "goerli":
        dev = network.accounts.add(os.getenv('PRIVATE_KEY'))
    else:
        dev = network.accounts.add(os.getenv('PRIVATE_KEY_R'))

    contract = TxtDocShare.at(address)

    contract.setStatus(id, {'from': dev})

def addFileBlockChain(address, testnet, filename, text):
    connectNetwork(testnet)

    if testnet == "kovan":
        dev = network.accounts.add(os.getenv('PRIVATE_KEY_K'))
    elif testnet == "goerli":
        dev = network.accounts.add(os.getenv('PRIVATE_KEY'))
    else:
        dev = network.accounts.add(os.getenv('PRIVATE_KEY_R'))

    contract = TxtDocShare.at(address)

    result = -1
    count = 1
    while result < 0 and count <= 5:
        print("\nTentativa " + str(count) + " de 5 na blockchain '" + testnet + "' :")
        numFiles = contract.getNumDocs()
        contract.addDoc(filename, text, {'from': dev})
        time.sleep(10)
        numFiles1 = contract.getNumDocs()

        if(numFiles < numFiles1):
            result = numFiles1 - 1

        if result > -1:
            print("Foi adicionado com sucesso o documento ao contrato '" + address + "' na blockchain '"+testnet+"'.")
        else:
            print("Ocorreu um erro a adicionar o documento ao contrato '" + address + "' na blockchain '" + testnet + "'.")

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
        print("\nDocumentos no contrato '" + Matrix[0][0] + "' :\n")
        for x in range(numFiles):
            doc = getLastDoc(x, Matrix)
            printDoc(doc, x)
    elif numFiles == -1:
        print("\nO contrato '" + Matrix[0][0] + "' tem um número incongruente de ficheiros.")
    else:
        print("\nO contrato '" + Matrix[0][0] + "' não tem documentos adicionados.")


def getIdFile():
    try:
        return int(input("Introduza o ID do documento (inteiro positivo ou 0): "))
    except:
        return -1

def connectNetwork(testnet):
    if network.is_connected():
        network.disconnect()

    network.connect(testnet)

def getLastDoc(idDoc, Matrix):
    connectNetwork('kovan')
    docKovan = TxtDocShare.at(Matrix[0][1]).getDoc(idDoc)

    connectNetwork('goerli')
    docGoerli = TxtDocShare.at(Matrix[1][1]).getDoc(idDoc)

    connectNetwork('rinkeby')
    docRink = TxtDocShare.at(Matrix[2][1]).getDoc(idDoc)

    lastupd = [datetime.fromtimestamp(docGoerli[6]), datetime.fromtimestamp(docKovan[6]), datetime.fromtimestamp(docRink[6])]
    lastupd.sort(reverse=True)

    if lastupd[0] == datetime.fromtimestamp(docKovan[6]):
        return [docKovan[0], docKovan[1], docKovan[2], docKovan[3], docKovan[4], docKovan[5], docKovan[6], "Kovan"]
    elif lastupd[0] == datetime.fromtimestamp(docGoerli[6]):
        return [docGoerli[0], docGoerli[1], docGoerli[2], docGoerli[3], docGoerli[4], docGoerli[5], docGoerli[6], "Goerli"]
    else:
        return [docRink[0], docRink[1], docRink[2], docRink[3], docRink[4], docRink[5], docRink[6], "Rinkeby"]


def printDoc(doc, idDoc):
    creationdate = datetime.fromtimestamp(doc[5])
    upddate = datetime.fromtimestamp(doc[6])
    print("Blockchain: "+doc[7]+"\nID: " + str(idDoc) + "\nNome do documento: " + doc[0] + "\nTexto: " + doc[
        1] + "\nVersão do documento: " + str(doc[2]) + "")
    print("Criado pelo address: " + doc[3] + "\nData de criação: " + str(creationdate) + "")

    if doc[3] == doc[4] and doc[5] == doc[6]:
        print("Ultima modificaçao(Address): Sem modificaçoes\nUltima modificaçao(Data): Sem modificaçoes\n")
    else:
        print("Ultima modificaçao(Address): " + doc[4] + "\nUltima modificaçao(Data): " + str(upddate) + "\n")


def getSingleFile(Matrix):
    idDoc = getIdFile()

    if idDoc < 0:
        print("\nTem de introduzir um número inteiro maior ou igual a 0.")
        return -1

    doc = getLastDoc(idDoc, Matrix)

    if not str(doc[0]):
        print("\nNão foi encontrado nenhum documento com esse ID.\n")
        return -1

    print("\nA mostrar o documento ID "+str(idDoc)+" do contrato '" + Matrix[0][0] + ":\n")
    printDoc(doc, idDoc)

def editDocBlockchain(Matrix, idDoc, docname, text):
    connectNetwork('kovan')
    dev = network.accounts.add(os.getenv('PRIVATE_KEY_K'))
    result = TxtDocShare.at(Matrix[0][1]).editDoc(idDoc, docname, text, {'from': dev})

    if result == -1:
        print("\nOcorreu um erro a editar o documento na blockchain 'Kovan'.")
    else:
        print("\nO documento foi editado na blockchain 'Kovan'.")


    connectNetwork('goerli')
    dev = network.accounts.add(os.getenv('PRIVATE_KEY'))
    result = TxtDocShare.at(Matrix[1][1]).editDoc(idDoc, docname, text, {'from': dev})

    if result == -1:
        print("\nOcorreu um erro a editar o documento na blockchain 'Goerli'.")
    else:
        print("\nO documento foi editado na blockchain 'Goerli'.")

    connectNetwork('rinkeby')
    dev = network.accounts.add(os.getenv('PRIVATE_KEY_R'))
    result = TxtDocShare.at(Matrix[2][1]).editDoc(idDoc, docname, text, {'from': dev})

    if result == -1:
        print("\nOcorreu um erro a editar o documento na blockchain 'Rinkeby'.")
    else:
        print("\nO documento foi editado na blockchain 'Rinkeby'.")


def editFile(Matrix):
    idDoc = getIdFile()


    if idDoc < 0:
        print("\nTem de introduzir um número inteiro maior ou igual a 0.")
        return -1

    doc = getLastDoc(idDoc, Matrix)

    if not str(doc[0]):
        print("\nNão foi encontrado nenhum documento com esse ID.\n")
        return -1

    docname = input("Digite o novo nome do documento (vazio para não modificar): ")
    text = input("Digite o texto do documento (vazio para não modificar): ")

    if not docname and not text:
        print("\nNão introduziu quaisquer modificações.")
        return -1

    editDocBlockchain(Matrix, idDoc, docname, text)

    doc = getLastDoc(idDoc, Matrix)

    print("\nA mostrar o documento ID "+str(idDoc)+" do contrato '" + Matrix[0][0] + ":\n")
    printDoc(doc, idDoc)


def openAddrFile(type, option):
    configFile = '../config/contracts.txt'
    # readmode +, if do not exists, create a new one
    file = open(configFile, 'r+')

    if os.path.getsize(configFile) == 0:
        print(
            "Não foram encontrados contratos para ler/modificar. \nPor favor, publique um ou adicione no ficheiro de acordo com os parâmetros que constam no manual.")
    else:
        Matrix = getMatrix(file, type)
        add = getContract(Matrix)

        if add == -1:
            print("\nEsse contrato não foi encontrado. A voltar ao menu.\n")
        elif add != -1 and add != -2 and option == 1:
            addFile(Matrix[add])
        elif add != -1 and add != -2 and option == 2:
            getAllFiles(Matrix[add])
        elif add != -1 and add != -2 and option == 3:
            getSingleFile(Matrix[add])
        elif add != -1 and add != -2 and option == 4:
            editFile(Matrix[add])
        else:
            print(
                "\nNão foram encontrados contratos para ler/modificar. \nPor favor, publique um ou adicione no ficheiro de acordo com os parâmetros que constam no manual.")


def getContract(Matrix):
    try:
        if len(Matrix) < 1:
            return -2
        else:
            count = 1

            print("\nEscolha o contrato: ")
            for attr in Matrix:
                print(count, ": Nome do contrato:", attr[0][0])
                count = count + 1

            print("Nota: Digite a posição do contrato (e.g. Para o 1ºcontrato digite 1).\n")
            ncontract = int(input("Digite a sua opção: "))

            if ncontract > len(Matrix) or ncontract < 1:
                return -1

            return ncontract - 1

    except:
        return -1


def hasItem(matrix, type):
    count = False

    for attr in matrix:
        if attr[0][0] == type:
            count = True

    return count


def publishcontract():
    contractarr = glob.glob("../contracts/*.sol")

    try:
        count = 1
        print("\nEscolha o contrato que quer publicar: ")
        for name in contractarr:
            print(count, ":", name)
            count = count + 1

        print("Nota: Digite a posição do contrato (e.g. Para o 1ºcontrato digite 1).\n")
        ncontract = int(input("Digite a sua opção: "))

        if contractarr[ncontract - 1].find("../contracts/txtDocShare.sol") != -1:
            contractName = input("Digite o nome que deseja colocar no contracto: ")

            if contractName:
                publishbrownie(contractarr[ncontract - 1], "deployDocFile.py", contractName, "1")
            else:
                print("Não colocou nenhum nome, a colocar o nome por defeito.")
                publishbrownie(contractarr[ncontract - 1], "deployDocFile.py", "TxtDocShare", "1")
        elif contractarr[ncontract - 1].find("../contracts/teste1.sol") != -1:
            publishbrownie(contractarr[ncontract - 1], "testev2.py", "Teste")

    except:
        print("\nOcorreu um erro. A voltar ao menu.\n")
        return 0


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


def publishbrownie(name, file, contract, type):
    try:
        strguid = getGuid()
        add = subpublishbrownie("kovan", name, type)

        if len(add) == 42:
            print("\nContracto adicionado na rede kovan.\n")
            writecontractfile(contract, add, strguid, type)
            add = subpublishbrownie("goerli", name, type)
            if len(add) == 42:
                print("\nContracto adicionado na rede goerli.\n")
                writecontractfile(contract, add, strguid, type)
                add = subpublishbrownie("rinkeby", name, type)
                if len(add) == 42:
                    print("\nContracto adicionado na rede rinkeby.\n")
                    writecontractfile(contract, add, strguid, type)
                    print("\nO contracto foi adicionado com sucesso nas 3 testnets.\n")
                else:
                    print("\nOcorreu um erro. A voltar ao menu.\n")
                    return 0
            else:
                print("\nOcorreu um erro. A voltar ao menu.\n")
                return 0
        else:
            print("\nOcorreu um erro. A voltar ao menu.\n")
            return 0
    except Exception as ex:
        template = "Ocorreu uma excepção do tipo {0}. Argumentos:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return 0


def subpublishbrownie(testnet, name, type):
    try:
        if network.is_connected():
            network.disconnect()

        network.connect(testnet)
        network.accounts.clear()

        if testnet == "kovan":
            filename = "42"
            dev = network.accounts.add(os.getenv('PRIVATE_KEY_K'))
        elif testnet == "goerli": #ropsten é 3
            filename = "5"
            dev = network.accounts.add(os.getenv('PRIVATE_KEY'))
        else:
            filename = "4"
            dev = network.accounts.add(os.getenv('PRIVATE_KEY_R'))

        contractpub1 = glob.glob("../build/deployments/" + filename + "/*.json")
        print("\nA utilizar a framework Brownie para publicar o contrato: ", name, " na rede ", testnet,
              ". Aguarde, por favor...\n")

        network.gas_limit(859999)

        if type == "1":
            TxtDocShare.deploy({'from': dev})

        contractpub2 = glob.glob("../build/deployments/" + filename + "/*.json")
        newadd = list(set(contractpub2) - set(contractpub1))
        newadd = newadd[0]
        head, tail = os.path.split(newadd)
        return tail.replace(".json", "")
    except Exception as ex:
        template = "Ocorreu uma excepção do tipo {0}. Argumentos:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return -1


def writecontractfile(name, add, guid, type):
    file = open("../config/contracts.txt", "a+")
    str = name + ":" + add + ":" + guid + ":" + type + "\n"
    file.write(str)
    file.close()


def getbalance():
    if network.is_connected():
        network.disconnect()

    network.connect("kovan")
    network.accounts.clear()
    network.accounts.add(os.getenv('PRIVATE_KEY_K'))

    balance = network.accounts[0].balance()
    ether_value = network.web3.fromWei(balance, 'ether')
    print("\nKovan: A conta '", network.accounts[0], "' tem ", ether_value, " ETH.")

    if network.is_connected():
        network.disconnect()

    network.connect("goerli")
    network.accounts.clear()
    network.accounts.add(os.getenv('PRIVATE_KEY'))

    balance = network.accounts[0].balance()
    ether_value = network.web3.fromWei(balance, 'ether')
    print("Goerli: A conta '", network.accounts[0], "' tem ", ether_value, " ETH.")

    if network.is_connected():
        network.disconnect()

    network.connect("rinkeby")
    network.accounts.clear()
    network.accounts.add(os.getenv('PRIVATE_KEY_R'))

    balance = network.accounts[0].balance()
    ether_value = network.web3.fromWei(balance, 'ether')
    print("Rinkeby: A conta '", network.accounts[0], "' tem ", ether_value, " ETH.")


if __name__ == '__main__':
    menu()
