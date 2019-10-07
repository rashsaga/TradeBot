def clearScreen():
    import os
    os.system('cls' if os.name=='nt' else 'clear')

def fStr(num, prec = 8):
    return (("{:."+str(prec)+"f}").format(num))

def getSystemDateTime():
    import datetime
    return (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def log(str):
    print(getSystemDateTime() + " : " + str)

def sleep(seconds):
    import time
    time.sleep(seconds)

def isFileExists(fullName):
    import os
    return (os.path.isfile(fullName))

def sendEmail(subject, body):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    try:
        fromaddr = "42Notification@gmail.com"
        toaddr = "42Notification@gmail.com"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, "Password/1")
        server.sendmail(fromaddr, toaddr, msg.as_string())
        server.quit()
    except:
        print("Exception in sending email")