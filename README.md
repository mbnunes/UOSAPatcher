## UOSAPatcher - Ultima Online Stygian Abyss Patcher

UOSAPatcher is an Open Source tool, build in Python 3 to change Ultima Online SA client:

Last tested client: ```4.0.76.47```

Systems: ```Linux / Windows``` (MacOS not tested yet)

### This fork:
 * Now scans UOSA.exe for hex patterns, instead of writing to a specific address
 * Tested with 4.0.74.28 and 4.0.76.47
  
### Features:
 * Change server IP
 * Change server PORT
 * Remove client encryption

### Hot to use?
 * Install python3 [(How to install python?)](https://realpython.com/installing-python)
 * Execute the tool from the command line ```python3 UoSAPatcher.py```
 * Select the client folder path to UOSA.exe
 * Define the server information (ip/port)
 * Patch the client

<p align="center">
  <img src="https://github.com/Mutilador/UOSAPatcher/blob/master/UOSAPatcher.png">
</p>

### Information
The patch will not change the original client file, it will create a ```uosa_patched.exe``` file instead.
There may be changes need to be done yet, feel free to contribute to the project and add more features.

### Author
 * Maurício Nunes - Brazil

### Collaborators
 * João Escribano - Brazil 
___
