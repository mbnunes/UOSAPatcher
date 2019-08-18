#!/bin/python3

import os.path, shutil, re, time, mmap, binascii


def addByteIP(ip):

	spaces = 15-len(ip)

	originIP = bytes(ip, 'ascii')

	for let in range(spaces):
		originIP = originIP + b'\x00'

	return originIP


def search(m=None, prefix=None, value=None, suffix=None):

	if m is None or value is None:
		return -1

	if prefix is not None and len(prefix) % 2 != 0:
		return -1

	if value is not None and len(value) % 2 != 0:
		return -1

	if suffix is not None and len(suffix) % 2 != 0:
		return -1

	s = value

	if prefix is not None:
		s = prefix + s

	if suffix is not None:
		s = s + suffix

	pos = m.find(binascii.unhexlify(s), 0)

	if pos > 0 and prefix is not None:
		pos += len(prefix) // 2

	return pos


def injectClient(pathUOSA=None, address=None, portServer=0, message=None, removeEncrypt=False):

	pathUOSAOrigin = pathUOSA+'/UOSA.exe'
	pathUOSAFinal = pathUOSA+'/uosa-patched.exe'

	port = '{0:04x}'.format(int(portServer))
	port = re.findall('..', port)

	if os.path.isfile(pathUOSAOrigin):
		message['text'] = "UOSA.exe found, applying patch, please wait..."

		try:
			shutil.copyfile(pathUOSAOrigin, pathUOSAFinal)
			message['text'] = "Created new uosa-pached.exe"
			time.sleep(2)
		except:
			message['text'] = "Error creating new uosa-pached.exe"

		with open(pathUOSAFinal, 'rb+') as fh:
			# Read file into mmap
			m = mmap.mmap(fh.fileno(), 0)

			# Add IP in client.
			message['text'] = "Adding IP address in client..."

			# Find IP 1 - 107.23.85.115
			i = search(m, prefix='0000', value='3130372E32332E38352E313135', suffix='000000')
			if i > 0:
				print('IP 1 found at: ' + hex(i))
				fh.seek(i)
				fh.write(addByteIP(address))

			# Find IP 2 - 107.23.176.74
			i = search(m, prefix='000000', value='3130372E32332E3137362E3734', suffix='000000')
			if i > 0:
				print('IP 2 found at: ' + hex(i))
				fh.seek(i)
				fh.write(addByteIP(address))

			# Find Port 1 - 7776
			i = search(m, prefix='66C7442418', value='601E', suffix='8D4C241CE8')
			if i > 0:
				print('Port 1 found at: ' + hex(i))
				fh.seek(i)
				fh.write(bytes.fromhex(port[1]))
				fh.seek(i+1)
				fh.write(bytes.fromhex(port[0]))

			# Find Port 2 - 7775
			i = search(m, prefix='66C7442418', value='5F1E', suffix='E9CA000000')
			if i > 0:
				print('Port 2 found at: ' + hex(i))
				fh.seek(i)
				fh.write(bytes.fromhex(port[1]))
				fh.seek(i+1)
				fh.write(bytes.fromhex(port[0]))

			# Find Port 3 - 7775
			i = search(m, prefix='66C7442418', value='5F1E', suffix='750766C744')
			if i > 0:
				print('Port 3 found at: ' + hex(i))
				fh.seek(i)
				fh.write(bytes.fromhex(port[1]))
				fh.seek(i+1)
				fh.write(bytes.fromhex(port[0]))

			message['text'] = "PORT added"

			if removeEncrypt:
				message['text'] = "Removing encryption..."

				# Find Encrypt 1 - 3008
				i = search(m, prefix='00008A4E04', value='3008', suffix='8B4E048B46088B')
				if i > 0:
					print('Encrypt 1 found at: ' + hex(i))
					fh.seek(i)
					fh.write(b'\x90')
					fh.seek(i+1)
					fh.write(b'\x90')

				# Find Encrypt 2 - 304500
				i = search(m, prefix='4C110000', value='304500', suffix='83834C120000015D5B')
				if i > 0:
					print('Encrypt 2 found at: ' + hex(i))
					fh.seek(i)
					fh.write(b'\x90')
					fh.seek(i+1)
					fh.write(b'\x90')
					fh.seek(i+2)
					fh.write(b'\x90')

				# Find Encrypt 3 - 3010
				i = search(m, prefix='418A543108', value='3010', suffix='834618018B450C83C7013B')
				if i > 0:
					print('Encrypt 3 found at: ' + hex(i))
					fh.seek(i)
					fh.write(b'\x90')
					fh.seek(i+1)
					fh.write(b'\x90')

			message['text'] = "Client patched. uosa-patched.exe created!"

	else:
		message['text'] = "UOSA.exe not found!"



