#!/usr/bin/python3
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

p = brownie.project.load('/home/miranda/BrownieTeseProject', name="Tese")
p.load_config()
from brownie.project.Tese import TxtDocShare
import brownie.network as network

url = 'http://127.0.0.1:5000/'

#Blockchains names:
nameBlockchain1 = "Goerli"
nameBlockchain2 = "Goerli"
nameBlockchain3 = "Goerli"

#nameBlockchain1 = "Kovan"
#nameBlockchain2 = "Goerli"
#nameBlockchain3 = "Rinkeby"

def menu():
    try:
        response = requests.get(url+"online")

        if response.status_code == 200:
            option = 0
            while int(option) != 9:
                print(
                    "\n1 - Publicar contrato \n2 - Gerir documentos\n3 - Gerir token\n4 - Obter o balanço atual\n5 - Alterar private key/Infura ID\n9 - Sair.")
                option = switcher(input("Digite a sua opção: "))
        else:
            print("\nA REST API está em baixo, por favor, tente novamente mais tarde.")
    except:
        print("\nA REST API está em baixo, por favor, tente novamente mais tarde.")


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
    except Exception as e:
        print("\nOpção não reconhecida/Ocorreu um erro. A voltar ao menu principal." + e)


def menuToken():
    option = 0

    try:
        while int(option) != 9:
            print(
                "\n1 - Ver detalhes do token. \n2 - Transferir token.\n3 - Transferir token apartir da permissão.\n4 - Dar permissão de transferência.\n"
                + "5 - Ver todos os balanços.\n6 - Ver um balanço específico.\n7 - Ver todas as permissões.\n8 - Menu venda."
                +  "\n9 - Voltar ao menu anterior.")
            option = input("Digite a sua opção: ")

            if int(option) == 1:
                openToken(1)
            elif int(option) == 2:
                openToken(2)
            elif int(option) == 3:
                openToken(3)
            elif int(option) == 4:
                openToken(4)
            elif int(option) == 5:
                openToken(5)
            elif int(option) == 6:
                openToken(6)
            elif int(option) == 7:
                openToken(7)
            elif int(option) == 8:
                menuSellToken()
            elif int(option) == 9:
                print("\nA voltar ao menu principal.")
            else:
                print("\nOpção não reconhecida.")
    except:
        print("\nOpção não reconhecida/Ocorreu um erro. A voltar ao menu principal.")


def menuSellToken():
    option = 0

    try:
        while int(option) != 9:
            print(
                "\n1 - Começar venda."
                +  "\n2 - Ver detalhes da venda.\n3 - Comprar token.\n4 - Retirar dinheiro excedente.\n5 - Ver o meu balanço excedente."
                +   "\n6 - Definir preço de venda do token.\n7 - Definir número de tokens a ser vendidos.\n9 - Voltar ao menu anterior.")
            option = input("Digite a sua opção: ")

            if int(option) == 1:
                sellToken(1)
            elif int(option) == 2:
                sellToken(2)
            elif int(option) == 3:
                sellToken(3)
            elif int(option) == 4:
                sellToken(4)
            elif int(option) == 5:
                sellToken(5)
            elif int(option) == 6:
                sellToken(6)
            elif int(option) == 7:
                sellToken(7)
            elif int(option) == 9:
                print("\nA voltar ao menu anterior.")
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
            menuToken()
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


def addFile(num):
    contractName = input("Digite o nome do documento: ")
    text = input("Digite o texto do documento: ")

    if contractName and text:
        data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
                'addressR': os.getenv('PRIVATE_KEY_R'), 'docname': contractName, 'text': text}
        headers = {'context-type': 'application/json; charset=UTF-8'}

        print("\nA contactar a REST API para adicionar o documento ao contracto, aguarde por favor.")

        response = requests.post(url + "addfile", data=data, headers=headers)

        if str(json.loads(response.text)) == "200":
            print("\nO documento foi adicionado ao contracto com sucesso!")
        elif str(json.loads(response.text)) == "400":
            print("\nOcorreu um erro a adicionar o documento, por favor, verifique os campos enviados.")
        else:
            print("\nO contracto enviado não foi encontrado. Por favor, tente novamente.")
    else:
        print("\nTem de digitar um nome e um texto para o documento.")


def getAllFiles(Matrix, num):
    data = {'ncontract': num}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para obter todos os documentos do contracto '" + Matrix[0][0] + "', aguarde por favor.")

    response = requests.post(url + "getalldocs", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nO contracto enviado não foi encontrado/Não existem ficheiros adicionados ao contracto. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a obter os documentos, por favor, verifique os campos enviados.")
    else:
        docArray = json.loads(response.text)

        if len(docArray) < 1:
            print("\nO contrato '" + Matrix[0][0] + "' não tem documentos adicionados.")
        else:
            print("\nDocumentos no contrato '" + Matrix[0][0] + "' :\n")
            for x in range(len(docArray)):
                printDoc(docArray[x], x)


def getIdFile():
    try:
        return int(input("Introduza o ID do documento (inteiro positivo ou 0): "))
    except:
        return -1


def getNumTokensTransfer():
    try:
        return int(input("Introduza o número de tokens a tranferir/delegar (inteiro positivo): "))
    except:
        return -1


def getGeral(text):
    try:
        return int(input(text))
    except:
        return -1


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


def getSingleFile(Matrix, num):
    idDoc = getIdFile()

    if idDoc < 0:
        print("\nTem de introduzir um número inteiro maior ou igual a 0.")
        return -1

    data = {'ncontract': num, 'iddoc': idDoc}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para obter o documento com ID "+str(idDoc)+" do contracto '" + Matrix[0][
        0] + "', aguarde por favor.")

    response = requests.post(url + "getdoc", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print(
            "\nO contracto enviado não foi encontrado/Não foi encontrado o documento mencionado. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a obter o documento, por favor, verifique os campos enviados.")
    else:
        docArray = json.loads(response.text)

        if len(docArray) < 1:
            print("\nNão foi encontrado nenhum documento com esse ID.\n")
        else:
            print("\nA mostrar o documento ID "+str(idDoc)+" do contrato '" + Matrix[0][0] + "':\n")
            printDoc(docArray, idDoc)


def editFile(Matrix, num):
    idDoc = getIdFile()


    if idDoc < 0:
        print("\nTem de introduzir um número inteiro maior ou igual a 0.")
        return -1

    docname = input("Digite o novo nome do documento (vazio para não modificar): ")
    text = input("Digite o texto do documento (vazio para não modificar): ")

    if not docname and not text:
        print("\nNão introduziu quaisquer modificações.")
        return -1

    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R'), 'docname': docname, 'text': text, 'iddoc': idDoc}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para editar o documento com ID " + str(idDoc) + " do contracto '" + Matrix[0][
        0] + "', aguarde por favor.")

    response = requests.put(url + "editdoc", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nNão foi encontrado nenhum documento com esse ID.\n")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a editar o documento, por favor, verifique os campos enviados.")
    else:
        doc = json.loads(response.text)
        print("\nO documento foi editado com sucesso.")
        print("A mostrar o documento ID " + str(idDoc) + " do contrato '" + Matrix[0][0] + "' editado:\n")
        printDoc(doc, idDoc)


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


def getAddress(Matrix):
    try:
        if len(Matrix) < 1:
            return -2
        else:
            count = 1

            print("\nEscolha o endereço: ")
            for attr in Matrix:
                print(count, ": Nome:", attr[0], " | Carteira: ", attr[1])
                count = count + 1

            print("Nota: Digite a posição do endereço (e.g. Para o 1º endereço digite 1). Pode adicionar mais endereços no ficheiro 'address.txt'.\n")
            ncontract = int(input("Digite a sua opção (digite -9 para ver o seu balanço): "))

            if ncontract == -9:
                return -9

            if ncontract > len(Matrix) or ncontract < 1:
                return -1

            return ncontract - 1

    except:
        return -1


def getAddressTransfer(Matrix):
    try:
        if len(Matrix) < 1:
            return -2
        else:
            count = 1

            print("\nEscolha o endereço: ")
            for attr in Matrix:
                print(count, ": Nome:", attr[0], " | Carteira: ", attr[1])
                count = count + 1

            print("Nota: Digite a posição do endereço (e.g. Para o 1º endereço digite 1). Pode adicionar mais endereços no ficheiro 'address.txt'.\n")
            ncontract = int(input("Digite a sua opção: "))

            if ncontract > len(Matrix) or ncontract < 1:
                return -1

            return ncontract - 1

    except:
        return -1


def getAddressOwner(Matrix):
    try:
        if len(Matrix) < 1:
            return -2
        else:
            count = 1

            print("\nEscolha o endereço do dono dos tokens a enviar: ")
            for attr in Matrix:
                print(count, ": Nome:", attr[0], " | Carteira: ", attr[1])
                count = count + 1

            print(
                "Nota: Digite a posição do endereço (e.g. Para o 1º endereço digite 1). Pode adicionar mais endereços no ficheiro 'address.txt'.\n")
            ncontract = int(input("Digite a sua opção: "))

            if ncontract > len(Matrix) or ncontract < 1:
                return -1

            return ncontract - 1

    except:
        return -1


def getAddressReceiver(Matrix):
    try:
        if len(Matrix) < 1:
            return -2
        else:
            count = 1

            print("\nEscolha o endereço para enviar os tokens: ")
            for attr in Matrix:
                print(count, ": Nome:", attr[0], " | Carteira: ", attr[1])
                count = count + 1

            print("Nota: Digite a posição do endereço (e.g. Para o 1º endereço digite 1). Pode adicionar mais endereços no ficheiro 'address.txt'.\n")
            ncontract = int(input("Digite a sua opção (Digite -9 para transferir para a sua conta): "))

            if ncontract == -9:
                return -9

            if ncontract > len(Matrix) or ncontract < 1:
                return -1

            return ncontract - 1

    except:
        return -1


def openToken(option):
    data = {'type': "2"}
    headers = {'context-type': 'application/json; charset=UTF-8'}
    response = requests.post(url + "getcontractadd", data=data, headers=headers)
    Matrix = json.loads(response.text)

    if len(Matrix) < 1:
        print("\nNão existem contractos publicados. Por favor, publique um.")
    else:
        add = getContract(Matrix)

        if add == -1:
            print("\nEsse contrato não foi encontrado. A voltar ao menu.\n")
        elif add != -1 and add != -2 and option == 1:
            detailsToken(add, Matrix[add])
        elif add != -1 and add != -2 and option == 2:
            response = requests.get(url + "getaddress")
            addMatrix = json.loads(response.text)
            address = getAddressTransfer(addMatrix)
            if address == -2:
                print("\nNão existem endereços adicionados. Pode adicionar endereços no ficheiro 'address.txt'.")
            elif address == -1:
                print("\nEndereço não reconhecido.")
            else:
                transferToken(addMatrix[address], add)
        elif add != -1 and add != -2 and option == 3:
            response = requests.get(url + "getaddress")
            addMatrix = json.loads(response.text)
            owner = getAddressOwner(addMatrix)
            receiver = getAddressReceiver(addMatrix)
            if len(addMatrix) < 1:
                print("\nNão existem endereços adicionados. Pode adicionar endereços no ficheiro 'address.txt'.")
            elif owner == -1 or receiver == -1:
                print("\nUm dos endereços não foi reconhecido.")
            elif owner == receiver:
                print("\nO endereço do dono dos tokens e o receptor não podem ser iguais.")
            else:
                if receiver == -9:
                    transferTokenFrom(addMatrix[owner], receiver, add, "1")
                else:
                    transferTokenFrom(addMatrix[owner], addMatrix[receiver], add, "0")
        elif add != -1 and add != -2 and option == 4:
            response = requests.get(url + "getaddress")
            addMatrix = json.loads(response.text)
            address = getAddressTransfer(addMatrix)
            if address == -2:
                print("\nNão existem endereços adicionados. Pode adicionar endereços no ficheiro 'address.txt'.")
            elif address == -1:
                print("\nEndereço não reconhecido.")
            else:
                approveToken(addMatrix[address], add)
        elif add != -1 and add != -2 and option == 5:
            getAllBalances(Matrix[add], add)
        elif add != -1 and add != -2 and option == 6:
            response = requests.get(url + "getaddress")
            addMatrix = json.loads(response.text)
            address = getAddress(addMatrix)
            if address == -2:
                print("\nNão existem endereços adicionados. Pode adicionar endereços no ficheiro 'address.txt'.")
            elif address == -1:
                print("\nEndereço não reconhecido.")
            else:
                if address == -9:
                    getMyTokenBalance(Matrix[add], add)
                else:
                    getEspBalance(addMatrix[address], add, Matrix[add])
        elif add != -1 and add != -2 and option == 7:
            getAllAllowances(Matrix[add], add)
        else:
            print(
                "\nNão foram encontrados contratos para ler/modificar. \nPor favor, publique um ou adicione no ficheiro de acordo com os parâmetros que constam no manual.")


def sellToken(option):
    data = {'type': "2"}
    headers = {'context-type': 'application/json; charset=UTF-8'}
    response = requests.post(url + "getcontractadd", data=data, headers=headers)
    Matrix = json.loads(response.text)

    if len(Matrix) < 1:
        print("\nNão existem contractos publicados. Por favor, publique um.")
    else:
        add = getContract(Matrix)

        if add == -1:
            print("\nEsse contrato não foi encontrado. A voltar ao menu.\n")
        elif add != -1 and add != -2 and option == 1:
            startsell(add)
        elif add != -1 and add != -2 and option == 2:
            getDetailsTokenSell(add, Matrix[add])
        elif add != -1 and add != -2 and option == 3:
            buytoken(add)
        elif add != -1 and add != -2 and option == 4:
            response = requests.get(url + "getaddress")
            addMatrix = json.loads(response.text)
            address = getAddress(addMatrix)
            if address == -2:
                print("\nNão existem endereços adicionados. Pode adicionar endereços no ficheiro 'address.txt'.")
            elif address == -1:
                print("\nEndereço não reconhecido.")
            else:
                if address == -9:
                    withdrawbalanceexceed(Matrix[add], add, "me")
                else:
                    withdrawbalanceexceed(Matrix[add], add, addMatrix[address])
        elif add != -1 and add != -2 and option == 5:
            getMyExceedBalance(Matrix[add], add)
        elif add != -1 and add != -2 and option == 6:
            setPriceSellToken(Matrix[add], add)
        elif add != -1 and add != -2 and option == 7:
            setNumSellToken(Matrix[add], add)
        else:
            print(
                "\nNão foram encontrados contratos para ler/modificar. \nPor favor, publique um ou adicione no ficheiro de acordo com os parâmetros que constam no manual.")


def setPriceSellToken(Matrix, num):
    priceK = getGeral("Introduza o novo preço de venda do token na blockchain "+nameBlockchain1+": ")
    priceG = getGeral("Introduza o novo preço de venda do token na blockchain "+nameBlockchain2+": ")
    priceR = getGeral("Introduza o novo preço de venda do token na blockchain "+nameBlockchain3+": ")

    if priceK <= 0 or priceG <= 0 or priceR <= 0:
        print("\nTem de introduzir um número inteiro maior que 0.")
        return -1

    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R'), 'priceK': priceK, 'priceG': priceG, 'priceR': priceR}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para alterar o preço de venda do token '" + Matrix[0][
        0] + "', aguarde por favor.")

    response = requests.put(url + "setpricetoken", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nO contracto enviado não foi encontrado. Por favor, tente novamente./Não existe uma venda iniciada.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro alterar o preço do token. Por favor, verifique os campos enviados ou verique se é o dono da venda.")
    else:
        print("\nO preço do token foi alterado.")


def setNumSellToken(Matrix, num):
    numToken = getGeral("Introduza o novo número de tokens à venda: ")

    if numToken <= 0:
        print("\nTem de introduzir um número inteiro maior que 0.")
        return -1

    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R'), 'num': numToken}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para alterar o número de tokens à venda, relativo ao token '" + Matrix[0][
        0] + "', aguarde por favor.")

    response = requests.put(url + "setnumtoken", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nO contracto enviado não foi encontrado. Por favor, tente novamente./Não existe uma venda iniciada.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro alterar o número de tokens à venda. Por favor, verifique os campos enviados (se tem o número de tokens suficientes para vender) ou verique se é o dono da venda.")
    else:
        print("\nO número de tokens à venda foi alterado.")


def withdrawbalanceexceed(Matrix, num, addMatrix):
    blockchain = getGeral("Introduza a blockchain (1 - "+nameBlockchain1+" | 2 - "+nameBlockchain2+" | 3 - "+nameBlockchain3+"): ")

    if blockchain <= 0 or blockchain > 3:
        print("\nTem de introduzir um número inteiro entre 1 e 3.")
        return -1

    amount = getGeral("Introduza o montante a retirar: ")

    if amount <= 0:
        print("\nTem de introduzir um número inteiro maior que 0.")
        return -1

    if blockchain == "1":
        address = os.getenv('PRIVATE_KEY_K')
    elif blockchain == "2":
        address = os.getenv('PRIVATE_KEY')
    else:
        address = os.getenv('PRIVATE_KEY_R')

    if addMatrix == "me":
        data = {'ncontract': num, 'address': address, 'value': amount, 'to': addMatrix, 'blockchain': blockchain}
        headers = {'context-type': 'application/json; charset=UTF-8'}
    else:
        data = {'ncontract': num, 'address': address, 'value': amount, 'to': addMatrix[1], 'blockchain': blockchain}
        headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para retirar o balanço excedente relativo à compra do token '" + Matrix[0][
        0] + "', aguarde por favor.")

    response = requests.put(url + "withdrawmoney", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nO contracto enviado não foi encontrado. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a retirar o balanço excedente. Por favor, verifique os campos enviados.")
    else:
        print("\nO balanço excedente foi retirado.")


def getMyExceedBalance(Matrix, num):
    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R')}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para obter o seu balanço excedente relativo à compra do token '" + Matrix[0][0] + "', aguarde por favor.")

    response = requests.post(url + "getbalanceexceeds", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nO contracto enviado não foi encontrado. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a obter o seu balanço excedente, por favor, verifique os campos enviados.")
    else:
        tokenArray = json.loads(response.text)

        if len(tokenArray) < 1:
            print("\nO token '" + Matrix[0][0] + "' não tem a sua carteira adicionada nos balanços.")
        else:
            print("\nO meu balanço excedente relativo à compra do token '" + Matrix[0][0] + "' :\n")
            print("Blockchain: Kovan ")
            print("Número de ether excedente: " + str(tokenArray[0][0]) + "\nVersão: " + str(tokenArray[0][1]) + "\n")
            print("Blockchain: Goerli ")
            print("Número de ether excedente: " + str(tokenArray[1][0]) + "\nVersão: " + str(tokenArray[1][1]) + "\n")
            print("Blockchain: Rinkeby ")
            print("Número de ether excedente: " + str(tokenArray[2][0]) + "\nVersão: " + str(tokenArray[2][1]) + "\n")


def startsell(num):
    numTokens = getGeral("Introduza o número de tokens a vender: ")
    priceK = getGeral("Introduza o preço dos tokens na Blockchain "+nameBlockchain1+": ")
    priceG = getGeral("Introduza o preço dos tokens na Blockchain "+nameBlockchain2+": ")
    priceR = getGeral("Introduza o preço dos tokens na Blockchain "+nameBlockchain3+": ")

    if numTokens <= 0 or priceK <= 0 or priceG <= 0 or priceR <= 0:
        print("\nTem de introduzir um número inteiro maior que 0 para o número de tokens e preço.")
        return -1

    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R'), 'priceK': priceK, 'priceG': priceG, 'priceR': priceR, 'numOfTokens': numTokens}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para iniciar a venda dos tokens, aguarde por favor.")

    response = requests.put(url + "startsell", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nNão foi encontrado nenhum contrato com esse ID./Não tem o número de tokens colocados para venda.\n")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a iniciar a venda, por favor, verifique os campos enviados (nomeadamente o valor introduzido de tokens).")
    else:
        print("\nA venda de tokens foi iniciada com sucesso.")


def buytoken(num):
    amount = getGeral("Introduza o montante de tokens que quer comprar (será comprado aleatóriamente em 2 das 3 blockchains): ")

    if amount <= 0:
        print("\nTem de introduzir um número inteiro maior que 0 para o número de tokens.")
        return -1

    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R'), 'money': amount}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para iniciar a compra dos tokens, aguarde por favor.")

    response = requests.put(url + "buytoken", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nNão foi encontrado nenhum contrato com esse ID./Não tem o número de tokens colocados para venda.\n")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a comprar os tokens, por favor, verifique os campos enviados (nomeadamente o valor introduzido de ether).")
    else:
        print("\nA compra de tokens foi feita com sucesso. Verifique se sobrou algum dinheiro.")


def getDetailsTokenSell(num, Matrix):
    data = {'ncontract': num}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para obter os detalhes do token: '" + Matrix[0][0] + "', aguarde por favor.")

    response = requests.post(url + "getdetailssell", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print(
            "\nO contracto enviado não foi encontrado/A venda ainda não foi começada. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a obter os detalhes da venda do token, por favor, verifique os campos enviados.")
    else:
        tokenArray = json.loads(response.text)

        if len(tokenArray) < 1:
            print("\nNão foi encontrado nenhuma venda para o token em questão.\n")
        else:
            print("\nA mostrar os detalhes da venda do token:\n")
            printTokenStuff(tokenArray[0],"4", nameBlockchain1)
            printTokenStuff(tokenArray[1], "4", nameBlockchain2)
            printTokenStuff(tokenArray[2], "4", nameBlockchain3)


def openAddrFile(type, option):
    data = {'type': type}
    headers = {'context-type': 'application/json; charset=UTF-8'}
    response = requests.post(url + "getcontractadd", data=data, headers=headers)
    Matrix = json.loads(response.text)

    if len(Matrix) < 1:
        print("\nNão existem contractos publicados. Por favor, publique um.")
    else:
        add = getContract(Matrix)

        if add == -1:
            print("\nEsse contrato não foi encontrado. A voltar ao menu.\n")
        elif add != -1 and add != -2 and option == 1:
            addFile(add)
        elif add != -1 and add != -2 and option == 2:
            getAllFiles(Matrix[add], add)
        elif add != -1 and add != -2 and option == 3:
            getSingleFile(Matrix[add], add)
        elif add != -1 and add != -2 and option == 4:
            editFile(Matrix[add], add)
        else:
            print(
                "\nNão foram encontrados contratos para ler/modificar. \nPor favor, publique um ou adicione no ficheiro de acordo com os parâmetros que constam no manual.")


def hasItem(matrix, type):
    count = False

    for attr in matrix:
        if attr[0][0] == type:
            count = True

    return count


def publishcontract():
    response = requests.get(url+"getcontract")

    if response.status_code == 200:
        contractarr = json.loads(response.text)
        try:
            count = 1
            print("\nEscolha o contrato que quer publicar: ")
            for name in contractarr:
                print(count, ":", name)
                count = count + 1

            print("Nota: Digite a posição do contrato (e.g. Para o 1ºcontrato digite 1).\n")
            ncontract = int(input("Digite a sua opção: "))

            if contractarr[ncontract - 1].find("../contracts/txtDocShare.sol") != -1:
                name = False
                while name is False:
                    contractName = input("Digite o nome que deseja colocar no contracto (vazio para sair): ")

                    if not contractName:
                        return 0
                    else:
                        data = {'name': contractName, 'type': "1"}
                        headers = {'context-type': 'application/json; charset=UTF-8'}
                        response = requests.post(url + "hasname", data=data, headers=headers)

                        if str(json.loads(response.text)) == "1":
                            name = True
                        else:
                            print("\nO nome escolhido nao esta disponivel. Por favor, tente novamente.\n")

                data = {'ncontract': ncontract,'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
                        'addressR': os.getenv('PRIVATE_KEY_R'), 'name': contractName}
                headers = {'context-type': 'application/json; charset=UTF-8'}

                print("\nA contactar a REST API para publicar o contracto, aguarde por favor.")

                response = requests.post(url + "publishcontract", data=data, headers=headers)

                if str(json.loads(response.text)) == "1":
                    print("\nO contracto foi publicado com sucesso!")
                else:
                    print("\nOcorreu um erro a publicar o contracto. Por favor, tente novamente.")

            elif contractarr[ncontract - 1].find("../contracts/tokenErc20.sol") != -1:
                name = False
                while name is False:
                    contractName = input("Digite o nome que deseja colocar no token (vazio para sair): ")

                    if not contractName:
                        return 0
                    else:
                        data = {'name': contractName, 'type': "2"}
                        headers = {'context-type': 'application/json; charset=UTF-8'}
                        response = requests.post(url + "hasname", data=data, headers=headers)

                        if str(json.loads(response.text)) == "1":
                            name = True
                        else:
                            print("\nO nome escolhido não esta disponível. Por favor, tente novamente.\n")

                tokensymbol = input("Introduza o simbolo que deseja colocar no token: ")
                amount = getGeral("Introduza a quantidade de tokens: ")

                if not tokensymbol or amount <= 0:
                    return 0

                data = {'ncontract': ncontract, 'addressK': os.getenv('PRIVATE_KEY_K'),
                        'addressG': os.getenv('PRIVATE_KEY'),
                        'addressR': os.getenv('PRIVATE_KEY_R'), 'name': contractName, 'symbol':tokensymbol , 'total':amount}
                headers = {'context-type': 'application/json; charset=UTF-8'}

                print("\nA contactar a REST API para publicar o contracto, aguarde por favor.")

                response = requests.post(url + "publishcontract", data=data, headers=headers)

                if str(json.loads(response.text)) == "1":
                    print("\nO contracto foi publicado com sucesso!")
                else:
                    print("\nOcorreu um erro a publicar o contracto. Por favor, tente novamente.")

        except:
            print("\nNão foi encontrado esse contracto. A voltar ao menu.\n")
            return 0
    else:
        print("Não existem contractos para publicar.")


def getbalance():
    data = {'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'), 'addressR': os.getenv('PRIVATE_KEY_R')}
    headers = {'context-type': 'application/json; charset=UTF-8'}
    print("\nA contactar a REST API, aguarde por favor.")
    response = requests.post(url + "getbalance", data=data, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)
        print("\n"+nameBlockchain1+": A conta tem ", data[0], " ETH.")
        print(""+nameBlockchain2+": A conta tem ", data[1], " ETH.")
        print(""+nameBlockchain3+": A conta tem ", data[2], " ETH.")
    else:
        print("Ocorreu um erro a obter o balanço das contas.")


def detailsToken(num, Matrix):
    data = {'ncontract': num}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para obter os detalhes do token: '" + Matrix[0][0] + "', aguarde por favor.")

    response = requests.post(url + "gettokendetail", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print(
            "\nO contracto enviado não foi encontrado/Não foi encontrado o token mencionado. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a obter os detalhes do token, por favor, verifique os campos enviados.")
    else:
        tokenArray = json.loads(response.text)

        if len(tokenArray) < 1:
            print("\nNão foi encontrado nenhum token.\n")
        else:
            print("\nA mostrar os detalhes do token '" + tokenArray[0] + "':\n")
            printTokenStuff(tokenArray, "1")


def transferToken(addMatrix, num):
    numTokens = getNumTokensTransfer()

    if numTokens <= 0:
        print("\nTem de introduzir um número inteiro maior que 0.")
        return -1

    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R'), 'receiverK': addMatrix[1], 'receiverG': addMatrix[1], 'receiverR': addMatrix[1], 'numTokens': numTokens}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para transferir " + str(numTokens) + " tokens para a carteira '" + addMatrix[1] + "', aguarde por favor.")

    response = requests.put(url + "transfertoken", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nNão foi encontrado nenhum contrato com esse ID.\n")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a transferir os tokens, por favor, verifique os campos enviados (nomeadamente o valor introduzido de tokens).")
    else:
        print("\nForam transferidos com sucesso " + str(numTokens) + " tokens para a carteira '" + addMatrix[1] + "'.")


def transferTokenFrom(owner, receiver, num, myadd):
    numTokens = getNumTokensTransfer()

    if myadd == "1":
        if network.is_connected():
            network.disconnect()

        network.connect("kovan")
        network.accounts.clear()
        receiveradd = network.accounts.add(os.getenv('PRIVATE_KEY_K'))
    else:
        receiveradd = receiver[1]

    if numTokens <= 0:
        print("\nTem de introduzir um número inteiro maior que 0.")
        return -1

    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R'), 'ownerK': owner[1], 'ownerG': owner[1], 'ownerR': owner[1],
            'receiverK': receiveradd, 'receiverG': receiveradd, 'receiverR': receiveradd, 'numTokens': numTokens}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para transferir " + str(numTokens) + " tokens da carteira '"+owner[1]+"' para a carteira '" + receiveradd + "', aguarde por favor.")

    response = requests.put(url + "transfertokenfrom", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nNão foi encontrado nenhum contrato com esse ID.\n")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a transferir os tokens, por favor, verifique os campos enviados (nomeadamente o valor introduzido de tokens).")
    else:
        print("\nForam transferidos com sucesso " + str(numTokens) + " tokens da carteira '"+owner[1]+"' para a carteira '" + myadd + "'.")


def approveToken(addMatrix, num):
    numTokens = getNumTokensTransfer()

    if numTokens <= 0:
        print("\nTem de introduzir um número inteiro maior que 0.")
        return -1

    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R'), 'delegateK': addMatrix[1], 'delegateG': addMatrix[1], 'delegateR': addMatrix[1], 'numTokens': numTokens}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para delegar " + str(numTokens) + " tokens à carteira '" + addMatrix[1] + "', aguarde por favor.")

    response = requests.put(url + "approve", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nNão foi encontrado nenhum contrato com esse ID.\n")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a delegar os tokens, por favor, verifique os campos enviados (nomeadamente o valor introduzido de tokens).")
    else:
        print("\nForam delegados com sucesso " + str(numTokens) + " tokens para a carteira '" + addMatrix[1] + "'.")


def getAllBalances(Matrix, num):
    data = {'ncontract': num}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para obter todos os balanços do token '" + Matrix[0][0] + "', aguarde por favor.")

    response = requests.post(url + "gettokenbalance", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nO contracto enviado não foi encontrado. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a obter os balanços do token, por favor, verifique os campos enviados.")
    else:
        tokenArray = json.loads(response.text)

        if len(tokenArray) < 1:
            print("\nO token '" + Matrix[0][0] + "' não tem nenhuma carteira adicionada nos balanços.")
        else:
            print("\nBalanços no token '" + Matrix[0][0] + "' :\n")
            blockchain = tokenArray[len(tokenArray) - 1]
            print("Blockchain: " + blockchain + " \n")
            for x in range(len(tokenArray)-1):
                printTokenStuff(tokenArray[x], "2")


def getMyTokenBalance(Matrix, num):
    data = {'ncontract': num, 'addressK': os.getenv('PRIVATE_KEY_K'), 'addressG': os.getenv('PRIVATE_KEY'),
            'addressR': os.getenv('PRIVATE_KEY_R'), 'myadd': "1"}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para obter o seu balanço do token '" + Matrix[0][0] + "', aguarde por favor.")

    response = requests.post(url + "gettokenbalanceesp", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nO contracto enviado não foi encontrado. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a obter o seu balanço do token, por favor, verifique os campos enviados.")
    else:
        tokenArray = json.loads(response.text)

        if len(tokenArray) < 1:
            print("\nO token '" + Matrix[0][0] + "' não tem a sua carteira adicionada nos balanços.")
        else:
            print("\nO meu balanço no token '" + Matrix[0][0] + "' :\n")
            print("Blockchain: " + tokenArray[2] + " \n")
            print("Número de tokens: " + str(tokenArray[0]) + "\nVersão: " + str(tokenArray[1]) + "\n")


def getEspBalance(addMatrix, num, Matrix):
    data = {'ncontract': num, 'addressK': addMatrix[1], 'addressG': addMatrix[1],
            'addressR': addMatrix[1], 'myadd': "0"}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para obter o balanço de uma conta em específico do token '" + Matrix[0][0] + "', aguarde por favor.")

    response = requests.post(url + "gettokenbalanceesp", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nO contracto enviado não foi encontrado. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a obter o balanço do token, por favor, verifique os campos enviados.")
    else:
        tokenArray = json.loads(response.text)

        if len(tokenArray) < 1:
            print("\nO token '" + Matrix[0][0] + "' não tem nenhuma carteira '" + addMatrix[1] + "' adicionada nos balanços.")
        else:
            print("\nBalanço no token '" + Matrix[0][0] + "' :\n")
            print("Blockchain: " + tokenArray[2] + " \n")
            print("Nome Carteira: "+addMatrix[0]+"\nCarteira: "+addMatrix[1]+"\nNúmero de tokens: " + str(tokenArray[0]) + "\nVersão: " + str(tokenArray[1]) + "\n")


def getAllAllowances(Matrix, num):
    data = {'ncontract': num}
    headers = {'context-type': 'application/json; charset=UTF-8'}

    print("\nA contactar a REST API para obter todos os balanços do token '" + Matrix[0][0] + "', aguarde por favor.")

    response = requests.post(url + "getallowance", data=data, headers=headers)

    if str(json.loads(response.text)) == "404":
        print("\nO contracto enviado não foi encontrado. Por favor, tente novamente.")
    elif str(json.loads(response.text)) == "400":
        print("\nOcorreu um erro a obter as permissões do token, por favor, verifique os campos enviados.")
    else:
        tokenArray = json.loads(response.text)

        if len(tokenArray) < 1:
            print("\nO token '" + Matrix[0][0] + "' não tem nenhuma permissão adicionada.")
        else:
            print("\nPermissões dadas no token '" + Matrix[0][0] + "' :\n")
            blockchain = tokenArray[len(tokenArray) - 1]
            print("Blockchain: " + blockchain + " \n")
            for x in range(len(tokenArray)-1):
                printTokenStuff(tokenArray[x], "3")


def printTokenStuff(array, type, blockchain = ""):
    if type == "1":
        creationdate = datetime.fromtimestamp(array[6])
        upddate = datetime.fromtimestamp(array[7])
        print("Blockchain: "+array[8]+"\nNome: " + array[0] + "\nSímbolo: " + array[1] + "\nTotal de tokens: " + str(array[
            2]) + "\nVersão do token: " + str(array[3]) + "")
        print("Criado pelo address: " + array[4] + "\nData de criação: " + str(creationdate) + "")

        if array[4] == array[5] and array[6] == array[7]:
            print("Ultima modificaçao(Address): Sem modificaçoes\nUltima modificaçao(Data): Sem modificaçoes\n")
        else:
            print("Ultima modificaçao(Address): " + array[5] + "\nUltima modificaçao(Data): " + str(upddate) + "\n")
    elif type == "2":
        print(
            "Carteira: " + array[0] + "\nNúmero de tokens: " + str(array[1]) + "\nVersão: " + str(array[2]) + "\n")
    elif type == "3":
        print(
            "Dono: " + array[0] + "\nDelegado: " + array[1] + "\nNúmero de tokens delegados: " + str(array[2]) + "\nVersão: " + str(array[3]) + "\n")
    elif type == "4":
        if array == "-1":
            print("Não foi possível obter os dados da venda na blockchain " + blockchain + ".\n")
        else:
            creationdate = datetime.fromtimestamp(array[6])
            upddate = datetime.fromtimestamp(array[7])
            print("Blockchain: "+blockchain+"\nDono da venda: " + array[0] + "\nNúmero de tokens que falta vender: " + str(array[1]) + "\nPreço de cada token: " + str(array[
                2]) + "\nVersão do token: " + str(array[3]) + "")
            print("Criado pelo address: " + array[4] + "\nData de criação: " + str(creationdate) + "")

            if array[4] == array[5] and array[6] == array[7]:
                print("Ultima modificaçao(Address): Sem modificaçoes\nUltima modificaçao(Data): Sem modificaçoes\n")
            else:
                print("Ultima modificaçao(Address): " + array[5] + "\nUltima modificaçao(Data): " + str(upddate) + "\n")

if __name__ == '__main__':
    menu()
