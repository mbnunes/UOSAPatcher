#!/bin/python3

import argparse, os.path, shutil, re, time

def addByteIP(ip):

	spaces = 15-len(ip)
	
	#originIP = b'\x00'+bytes(ip, 'ascii')
	originIP = bytes(ip, 'ascii')
	
	for let in range(spaces):
		originIP = originIP + b'\x00'

		
	return originIP

'''
Caso voce queira rodar somente por linha de comando basta descomentar essa parte aqui

parser = argparse.ArgumentParser()
parser.add_argument("ip", help="IP do host que deseja conectar")
parser.add_argument("port", help="port do host que deseja conectar", type=int)

args = parser.parse_args()

port = '{0:04x}'.format(args.port)
port = re.findall('..',port)
'''
def injectClient(pathUOSA=None, address=None, portServer=0, encrypt=None, message=None, removeEncrypt=False):	

	pathUOSAOrigin = pathUOSA+'/UOSA.exe'
	pathUOSAFinal = pathUOSA+'/uosa-patched.exe'

	port = '{0:04x}'.format(int(portServer))
	port = re.findall('..',port)

	if os.path.isfile(pathUOSAOrigin):
		message['text'] = "UOSA.exe encontrado! Aplicando path, aguarde..."
		
		try:
			shutil.copyfile(pathUOSAOrigin,pathUOSAFinal)
			message['text'] = "Criando o arquivo uosa-pached.exe"
			time.sleep(2)
		except:
			message['text'] = "Erro ao criar arquivo"
					
		with open(pathUOSAFinal, 'rb+') as fh:
			#Add IP in client.
			hexdata = fh.read()
			
			message['text'] = "Adding IP address in client..."
			#fh.seek(0x08B47F2)			
			#fh.write(b'\x00')
			#fh.seek(0x08B47F3)
			fh.seek(0x08B57EC)
			fh.write(addByteIP(address))
			#fh.seek(0x08B4803)
			fh.seek(0x08B57FC)
			fh.write(addByteIP(address))
			message['text'] = "IP added."
				
			message['text'] = "Adding PORT number in client..."
			
			#Add PORT in client
			
			#fh.seek(0x02123AB)
			fh.seek(0x0212687)
			fh.write(bytes.fromhex(port[1]))
			#fh.seek(0x02123AC)
			fh.seek(0x0212688)
			fh.write(bytes.fromhex(port[0]))
			
			#fh.seek(0x02122F7)
			fh.seek(0x0212732)
			fh.write(bytes.fromhex(port[1]))
			#fh.seek(0x02122F8)
			fh.seek(0x0212733)			
			fh.write(bytes.fromhex(port[0]))
			
			#fh.seek(0x02123A2)
			fh.seek(0x021273B)
			fh.write(bytes.fromhex(port[1]))
			#fh.seek(0x02123A3)
			fh.seek(0x021273C)
			fh.write(bytes.fromhex(port[0]))
			
			message['text'] = "PORT added"
			
			if removeEncrypt:
				message['text'] = "Removing encryption..."				
				#fh.seek(0x023B07A)
				fh.seek(0x023B7CA)
				fh.write(b'\x90')
				#fh.seek(0x023B07B)
				fh.seek(0x023B7CB)
				fh.write(b'\x90')
				
				#fh.seek(0x0238899)
				fh.seek(0x0238FE9)
				fh.write(b'\x90')
				#fh.seek(0x023889A)
				fh.seek(0x0238FEA)
				fh.write(b'\x90')
				#fh.seek(0x023889B)
				fh.seek(0x0238FEB)
				fh.write(b'\x90')
				
				#fh.seek(0x023A76B)
				fh.seek(0x023AEBB)
				fh.write(b'\x90')
				#fh.seek(0x023A76C)
				fh.seek(0x023AEBC)
				fh.write(b'\x90')

			message['text'] = "Client patched. uosa-patched.exe created!"
			
	else:
		message['text'] = "UOSA.exe não encontrado. Certifiquisse que o programa esteja rodando na mesma pasta do UOSA!"


	
