import tkinter
from tkinter import *
import sys
from tkinter.filedialog import askdirectory
from UoSAPyPatcher import *


class Application(tkinter.Tk):

	def __init__(self, parent):
		tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()

	def initialize(self):
		self.grid()

		self.pathUOSA = Label(text="UOSA Path")
		self.pathUOSA["font"] = ("Arial", "10", "bold")
		self.pathUOSA.grid(column=0, row=0, padx=5, pady=5)

		self.pathString = StringVar()
		self.pathEntry = Entry(textvariable=self.pathString)
		self.pathEntry["width"] = 30
		self.pathEntry["font"] = ("Arial", "10")
		self.pathEntry.grid(column=1, row=0, padx=5, pady=5)

		self.findPathButton = Button()
		self.findPathButton["text"] = "PATH"
		self.findPathButton["font"] = ("Calibri", "8")
		self.findPathButton["width"] = 12
		self.findPathButton["command"] = self.findPath
		self.findPathButton.grid(column=3, row=0, padx=5, pady=5)

		self.loginServer = Label(text="LoginServer:")
		self.loginServer["font"] = ("Arial", "10", "bold")
		self.loginServer.grid(column=0, row=1, padx=5, pady=5)

		self.loginString = StringVar()
		self.loginEntry = Entry(textvariable=self.loginString)
		self.loginEntry.insert(10,"127.0.0.1")
		self.loginEntry["width"] = 30
		self.loginEntry["font"] = ("Arial", "10")
		self.loginEntry.grid(column=1, row=1, padx=5, pady=5)

		self.encryptBoolVar = BooleanVar()
		self.encryptBool = Checkbutton(text='Remove Encrypt', var=self.encryptBoolVar)
		self.encryptBool["width"] = 15
		self.encryptBool["font"] = ("Arial", "10")
		self.encryptBool.grid(column=1, row=3)

		self.portServer = Label(text="Port:")
		self.portServer["font"] = ("Arial", "10", "bold")
		self.portServer.grid(column=0, row=2, padx=5, pady=5)

		self.portString = StringVar()
		self.portEntry = Entry(textvariable=self.portString)
		self.portEntry.insert(5, '2593')
		self.portEntry["width"] = 30
		self.portEntry["font"] = ("Arial", "10")
		self.portEntry.grid(column=1, row=2, padx=5, pady=5)

		self.pactherButton = Button()
		self.pactherButton["text"] = "Patcher"
		self.pactherButton["font"] = ("Calibri", "8")
		self.pactherButton["width"] = 12
		self.pactherButton["command"] = self.injectPatcher
		self.pactherButton.grid(column=3, row=4, padx=5, pady=5)

		self.exitButton = Button()
		self.exitButton["text"] = "Exit"
		self.exitButton["font"] = ("Calibri", "8")
		self.exitButton["width"] = 12
		self.exitButton["command"] = self.sair
		self.exitButton.grid(column=4, row=4, padx=5, pady=5)

		self.warningLabel = Label()
		self.warningLabel["font"] = ("Arial", "10", "bold")
		self.warningLabel.grid(column=0, row=4, padx=5, pady=5, columnspan=2)

	def findPath(self):
		filename = askdirectory(title='Select UOSA folder')
		self.pathEntry.delete(0, 'end')
		self.pathEntry.insert(10, filename)

	def sair(self):
		sys.exit()

	def injectPatcher(self):
		injectClient(
			self.pathEntry.get(),
			self.loginEntry.get(),
			self.portEntry.get(),
			self.warningLabel,
			self.encryptBoolVar.get()
		)
