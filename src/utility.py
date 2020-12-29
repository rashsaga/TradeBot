from conf.SECRETS import EMAIL_ADDRESS, EMAIL_PASSWORD

def clear_screen():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def f_str(num, prec=8):
    return ("{:." + str(prec) + "f}").format(num)


def get_system_date_time():
    import datetime
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log(_str):
    print(get_system_date_time() + " : " + _str)


def sleep(seconds):
    import time
    time.sleep(seconds)


def is_file_exists(full_name):
    import os
    return os.path.isfile(full_name)


def send_email(subject, body):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    try:
        from_addr = to_addr = EMAIL_ADDRESS
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_addr, EMAIL_PASSWORD)
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()
    except:
        print("Exception in sending email")
