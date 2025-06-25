# Rainbows-Automated

## Welcome to QACY
In order to use this system, please follow the steps bellow

### Prerequisets 

1. Git
2. Python

If you do not have these installed, please go to the links down below in follow the instilation instructions

These instructions are also speciically set for windows, if you are using a different opperating system such as Linux os macOS, some of the commands may differ but the process is the same.

### 1.

Run the command ```git clone https://github.com/BradanCraig/Rainbows-Automated.git``` in your terminal
Make sure that you are in the directory that you want the folder to live in

### 2. 

Run the command ```python -m venv venv```
This will create a virtual enviorment in order to install all the dependencies so that they do not conflict with other things installed on your device.
Afterwards, run the command ```.\venv\Scripts\Activate.ps1``` if you are using PowerShell, or ```.\venv\Scripts\Activate.bat``` if you are using Command Prompt
You should see a little popup '(venv)' show up in your terminal

### 3.

Now that you are in your virtual enviorment, run the command ```python -m pip install -r requirements.txt```
This will install all of the libraries needed to run the code onto your machine.

### 4. 

Now you should be able to run ```python main.py``` in which the url should pop up that you can click on and visit
If you can not find it, you can type in "http://127.0.0.1:8000" into your browsers url and access the same page
