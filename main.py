#!python3

from UOSAPatcherGUI import Application

if __name__ == "__main__":
    app = Application(None)      #criamos uma aplicação sem nenhum pai, pois é a principal.
    app.title('UOSAPatcher')    #especificamos o título de nossa aplicação
    app.mainloop()  