import time
import random
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


def nowtime():
    return str(datetime.datetime.now()).split(".")[0]


def getProductId(url):
    if url.endswith("/"):
        url = url[:-1]
    return url.split("-")[-1]


class MailInfo(object):
    def __init__(self):
        self.smtpserver = "smtp.163.com"
        self.username = "15221856016@163.com"
        self.password = "OVHXVEKOGQBJDDZN"
        self.sender = "15221856016@163.com"
        self.receiver = [
            "792321264@qq.com",
        ]


class HermesReminder(object):
    def __init__(self, urls, receiver, driver_path="./chromedriver"):
        self.urls = urls
        self.mail_info = MailInfo()
        if receiver is not None:
            self.mail_info.receiver = receiver
        self.startWebdriver(driver_path)

    def startWebdriver(self, driver_path):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options, service=Service(driver_path))

    def genMailMessage(self, url):
        text = "爱马仕来货啦（商品编号{}）！快点击链接购买：\n{}".format(getProductId(url), url)
        text_plain = MIMEText(text, "plain", "utf-8")
        msg = MIMEMultipart("mixed")
        subject = "爱马仕来货啦（商品编号{}），赶紧购买！".format(getProductId(url))
        subject = Header(subject, "utf-8").encode()
        msg["Subject"] = subject
        msg["From"] = "<{}>".format(self.mail_info.sender)
        msg["To"] = "; ".join(["<{}>".format(r) for r in self.mail_info.receiver])
        msg["Date"] = str(nowtime())
        msg.attach(text_plain)
        return msg

    def sendMail(self, url):
        msg = self.genMailMessage(url)
        smtp = smtplib.SMTP()
        smtp.connect(self.mail_info.smtpserver)
        smtp.login(self.mail_info.username, self.mail_info.password)
        smtp.sendmail(self.mail_info.sender, self.mail_info.receiver, msg.as_string())
        smtp.quit()
        print("{} 邮件发送成功！".format(nowtime()))

    def run(self):
        while True:
            for url in self.urls:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(
                    "{} 正在检测下面商品（商品编号{}）：\n{}".format(nowtime(), getProductId(url), url)
                )
                self.driver.get(url)
                time.sleep(10)
                if "add-to-cart" in self.driver.page_source:
                    print("{} 该商品有货啦，赶紧购买！".format(nowtime()))
                    try:
                        self.sendMail(url)
                    except:
                        print("{} 邮件发送失败，重新发送...".format(nowtime()))
                elif "noiframe" in self.driver.page_source:
                    print("{} 该页面被禁止访问，等待重新访问...".format(nowtime()))
                else:
                    print("{} 该商品没货，继续检测...".format(nowtime()))
                wait_time = 30 + random.randint(1, 100)
                print("{} 等待{}秒，防止IP被封...".format(nowtime(), wait_time))
                time.sleep(wait_time)


if __name__ == "__main__":
    receiver = [
        # "1021038335@qq.com",
        "792321264@qq.com",
    ]
    urls = [
        # r"https://www.hermes.cn/cn/zh/product/hermes-bridleback-50-rocabar%E6%89%8B%E6%8F%90%E5%8C%85-H080761CKAA/",
        r"https://www.hermes.com/ca/en/product/picotin-lock-18-bag-H056289CK0L/",
        # r"https://www.hermes.cn/cn/zh/product/picotin-lock-22-casaque%E6%89%8B%E6%8F%90%E5%8C%85-H082380CKAH/",
    ]
    driver_path = "./chromedriver"
    app = HermesReminder(urls=urls, receiver=receiver, driver_path=driver_path)
    app.run()
