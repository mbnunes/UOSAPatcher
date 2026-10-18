#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import re
import struct
import binascii
import argparse


def addByteIP(ip, max_len=16):
	"""Formata o IP em bytes terminados em nulo com padding até max_len (padrão 16 bytes)."""
	raw = ip.encode('ascii')
	if len(raw) >= max_len:
		return raw[:max_len - 1] + b'\x00'
	return raw + b'\x00' * (max_len - len(raw))


def search(m=None, prefix=None, value=None, suffix=None):
	"""Função de busca legada mantida para compatibilidade reversa."""
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


def _set_status(message, text):
	"""Atualiza o widget da GUI se disponível e imprime no console."""
	print(text)
	if message is not None:
		try:
			message['text'] = text
		except Exception:
			pass


def find_ip_offsets(data):
	"""
	Localiza os offsets das strings de IP no binário UOSA.exe utilizando:
	1. Método Ternário (Assembly da função de login: rand() ? ip1 : ip2)
	2. Método Semântico (.rdata próximo a LoginManager::SendSelectedShard)
	3. Fallback histórico de IPs conhecidos da EA
	"""
	offsets = []

	# Método 1: Busca pelo operador ternário de push dos IPs (je / push ip1 / jmp / push ip2)
	p_ternary = re.compile(rb'\x74.\x68(....)\xeb.\x68(....)', re.DOTALL)
	ip_regex = re.compile(rb'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

	for m in p_ternary.finditer(data):
		va1, va2 = struct.unpack('<II', m.group(1) + m.group(2))
		off1 = va1 - 0x400000
		off2 = va2 - 0x400000
		if 0 <= off1 < len(data) and 0 <= off2 < len(data):
			s1 = data[off1:off1 + 20].split(b'\x00')[0]
			s2 = data[off2:off2 + 20].split(b'\x00')[0]
			if ip_regex.match(s1) and ip_regex.match(s2):
				print(f"[IP] Encontrado via ternário (código em {hex(m.start())}):")
				print(f"     IP 1: {s1.decode()} em {hex(off1)}")
				print(f"     IP 2: {s2.decode()} em {hex(off2)}")
				offsets.extend([off1, off2])
				return offsets

	# Método 2: Janela contextual próxima a 'LoginManager::SendSelectedShard'
	marker = b'LoginManager::SendSelectedShard'
	pos_marker = data.find(marker)
	if pos_marker != -1:
		window_start = max(0, pos_marker - 256)
		window = data[window_start:pos_marker]
		for match in re.finditer(rb'(?:[0-9]{1,3}\.){3}[0-9]{1,3}', window):
			off = window_start + match.start()
			if off not in offsets:
				print(f"[IP] Encontrado via contexto semântico: {match.group().decode()} em {hex(off)}")
				offsets.append(off)
		if offsets:
			return offsets

	# Método 3: Fallback por IPs históricos conhecidos da EA
	known_ips = [
		b'13.248.219.129',
		b'75.2.70.184',
		b'107.23.85.115',
		b'107.23.176.74'
	]
	for ip in known_ips:
		pos = 0
		while True:
			idx = data.find(ip, pos)
			if idx == -1:
				break
			if idx not in offsets:
				print(f"[IP] Encontrado via lista de IPs conhecidos: {ip.decode()} em {hex(idx)}")
				offsets.append(idx)
			pos = idx + len(ip)

	return offsets


def find_port_offsets(data):
	"""
	Localiza os offsets onde as portas 7775 (0x1E5F) e 7776 (0x1E60) são definidas.
	Instruções MSVC: mov word ptr [esp + disp8], imm16
	"""
	offsets_7775 = []
	offsets_7776 = []

	# mov word ptr [esp + disp8], 0x1E5F (7775) -> 66 C7 44 24 ?? 5F 1E
	p_port_7775 = re.compile(rb'\x66\xc7\x44\x24.(\x5f\x1e)')
	for m in p_port_7775.finditer(data):
		offsets_7775.append(m.start(1))

	# mov word ptr [esp + disp8], 0x1E60 (7776) -> 66 C7 44 24 ?? 60 1E
	p_port_7776 = re.compile(rb'\x66\xc7\x44\x24.(\x60\x1e)')
	for m in p_port_7776.finditer(data):
		offsets_7776.append(m.start(1))

	# Fallback mais permissivo se os padrões específicos de stack não derem match
	if not offsets_7775:
		p_port_fallback_7775 = re.compile(rb'\x66\xc7.{1,4}(\x5f\x1e)')
		for m in p_port_fallback_7775.finditer(data):
			offsets_7775.append(m.start(1))

	if not offsets_7776:
		p_port_fallback_7776 = re.compile(rb'\x66\xc7.{1,4}(\x60\x1e)')
		for m in p_port_fallback_7776.finditer(data):
			offsets_7776.append(m.start(1))

	return offsets_7775, offsets_7776


def find_encryption_patches(data):
	"""
	Localiza as 3 operações de XOR responsáveis pela cifragem dos pacotes.
	Retorna tuplas (offset, tamanho_nops, bytes_originais).
	"""
	patches = []

	# Encrypt 1: Login Crypt / Twofish Rotation (xor byte ptr [eax], cl -> 30 08)
	p_enc1 = re.compile(rb'\x8a.\x04(\x30.)\x8b.\x04\x8b.\x08')
	for m in p_enc1.finditer(data):
		off = m.start(1)
		patches.append((off, 2, 'Encrypt 1 (Login Crypt)'))

	# Encrypt 2: Twofish Stream Crypt / Tabela S-Box (xor byte ptr [ebp+0], al -> 30 45 00)
	p_enc2 = re.compile(rb'\x4c\x11\x00\x00(\x30\x45\x00)\x83\x83\x4c\x12\x00\x00\x01')
	for m in p_enc2.finditer(data):
		off = m.start(1)
		patches.append((off, 3, 'Encrypt 2 (Twofish Stream)'))

	# Encrypt 3: Packet Stream Crypt (xor byte ptr [eax], dl -> 30 10)
	p_enc3 = re.compile(rb'\x41\x8a\x54.\x08(\x30.)\x83\x46\x18\x01')
	for m in p_enc3.finditer(data):
		off = m.start(1)
		patches.append((off, 2, 'Encrypt 3 (Packet Stream)'))

	return patches


def injectClient(pathUOSA=None, address=None, portServer=0, message=None, removeEncrypt=False):
	"""
	Aplica o patch no UOSA.exe gerando uosa-patched.exe com novo IP, porta e remoção de criptografia.
	Compatível com qualquer versão do cliente UOSA.
	"""
	if not pathUOSA:
		pathUOSA = '.'

	pathUOSAOrigin = os.path.join(pathUOSA, 'UOSA.exe')
	pathUOSAFinal = os.path.join(pathUOSA, 'uosa-patched.exe')

	if not os.path.isfile(pathUOSAOrigin):
		_set_status(message, "UOSA.exe not found!")
		return False

	_set_status(message, "UOSA.exe found, applying patch, please wait...")

	try:
		shutil.copyfile(pathUOSAOrigin, pathUOSAFinal)
		_set_status(message, "Created new uosa-patched.exe")
	except Exception as err:
		_set_status(message, f"Error creating uosa-patched.exe: {err}")
		return False

	with open(pathUOSAFinal, 'r+b') as fh:
		data = fh.read()

		# --- 1. APLICAR IP ---
		_set_status(message, f"Locating and patching IP address to: {address}...")
		ip_offsets = find_ip_offsets(data)
		if ip_offsets:
			ip_payload = addByteIP(address, max_len=16)
			for off in ip_offsets:
				print(f"Patched IP at {hex(off)}")
				fh.seek(off)
				fh.write(ip_payload)
			_set_status(message, f"IP patched ({len(ip_offsets)} occurrences)")
		else:
			print("[WARN] No IP patterns matched!")

		# --- 2. APLICAR PORTAS ---
		try:
			port_int = int(portServer)
		except ValueError:
			port_int = 2593

		port_payload = struct.pack('<H', port_int)
		_set_status(message, f"Locating and patching ports to: {port_int}...")
		ports_7775, ports_7776 = find_port_offsets(data)

		total_ports = 0
		for off in ports_7775:
			print(f"Patched Port 7775 at {hex(off)} -> {port_int}")
			fh.seek(off)
			fh.write(port_payload)
			total_ports += 1

		for off in ports_7776:
			print(f"Patched Port 7776 at {hex(off)} -> {port_int}")
			fh.seek(off)
			fh.write(port_payload)
			total_ports += 1

		_set_status(message, f"PORT patched ({total_ports} occurrences)")

		# --- 3. REMOVER CRIPTOGRAFIA ---
		if removeEncrypt:
			_set_status(message, "Removing encryption...")
			enc_patches = find_encryption_patches(data)
			for off, size, name in enc_patches:
				print(f"NOPed {name} at {hex(off)} ({size} bytes)")
				fh.seek(off)
				fh.write(b'\x90' * size)
			_set_status(message, f"Encryption removed ({len(enc_patches)} patches applied)")

	_set_status(message, "Client patched. uosa-patched.exe created!")
	return True


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="UOSAPatcher - Patch IP, Port and Encryption in UOSA.exe")
	parser.add_argument("ip", nargs="?", default="127.0.0.1", help="IP do servidor (ex: 127.0.0.1)")
	parser.add_argument("port", nargs="?", type=int, default=2593, help="Porta do servidor (ex: 2593)")
	parser.add_argument("--path", default=".", help="Diretório contendo o UOSA.exe (padrão: diretório atual)")
	parser.add_argument("--encrypt", action="store_true", help="Manter criptografia ativa (padrão: remove criptografia)")
	parser.add_argument("--no-crypt", action="store_true", default=True, help="Remover criptografia (padrão)")

	args = parser.parse_args()
	remove_crypt = not args.encrypt

	injectClient(
		pathUOSA=args.path,
		address=args.ip,
		portServer=args.port,
		removeEncrypt=remove_crypt
	)
