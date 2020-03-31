import time
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import datetime



class COVID_Automation(object):

    def __init__(self, URL, sender, receiver, password):
        self.URL = URL
        self.sender = sender
        self.receiver = receiver
        self.password = password
        self.state_data = pd.DataFrame()
        self.stats = []
        

    def scrape(self):
        #Get Request
        content = requests.get(URL).content
        #parse the contents
        soup = BeautifulSoup(content, "html.parser")
        # remove any newlines and extra spaces
        extract_contents = lambda row: [x.text.replace('\n', '') for x in row]
        # find all table rows and data cells within
        stats = [] 
        all_rows = soup.find_all('tr')
        for row in all_rows:
            stat = extract_contents(row.find_all('td')) 
            if len(stat) == 5:
                stats.append(stat)
        self.stats = stats
        #convert scrapped data to DataFrame
        new_cols = ["Sr.No", "States/UT","Confirmed","Recovered","Deceased"]
        state_data = pd.DataFrame(data = stats, columns = new_cols)
        state_data["Confirmed"] = state_data["Confirmed"].astype(int)
        state_data["Recovered"] = state_data["Recovered"].astype(int)
        state_data["Deceased"] = state_data["Deceased"].astype(int)
        self.state_data = state_data

    def cosmetic_changes(self, new_cols):
        table = PrettyTable()
        table.field_names = (new_cols)
        for i in self.stats:
             table.add_row(i)
        table.add_row(["", "Total", sum(self.state_data['Confirmed']), 
                        sum(self.state_data['Recovered']), 
                        sum(self.state_data['Deceased'])])


    def color_cell(self, cell):
            return 'color: ' + ('red' if cell > 10 else 'green')

    def send_mail_notification(self, attachment=False):

        Date = datetime.today().strftime('%Y-%m-%d')
        for receiver in self.receiver:
            message = MIMEMultipart('alternative')
            message['Subject'] = 'COVID-19 cases in INDIA for latest updated DATE %s'%Date
            message['From'] = self.sender
            message['To'] = receiver
            if attachment:
                html = self.state_data.style.applymap(self.color_cell, subset=['Confirmed']).render()
                message.attach(MIMEText(html, 'html'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender, self.password)
            server.sendmail(self.sender, receiver, message.as_string())
            server.quit()


if __name__ == '__main__':
    URL = 'https://www.mohfw.gov.in/'
    sender_mail = 'XXXXXXXXXXXXX'
    receiver_mail = ['XXXXXXXXXXXXX']
    password = 'XXXXXXXXXXXXX'
    covid = COVID_Automation(URL, sender_mail, receiver_mail, password)

    while True:
        print('[Info] Scrapping COVID-19 data State Wise')
        covid.scrape()
        print('[Info] Sending Mail Notification')
        covid.send_mail_notification(True)
        time.sleep(10)




