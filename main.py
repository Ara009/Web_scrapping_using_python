#importing libraries
import requests
import pandas as pd 
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#1.	Web Scraping:

def get_current_aapl_price():
    url = "https://finance.yahoo.com/quote/AAPL?p=AAPL"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    if price_tag:
        return float(price_tag.text.replace(',', ''))
    else:
        print("Price tag not found.")
        return None


#2.	Data Reconciliation:

def reconcile_price(current_price,csv_path='stock_data.csv'):
    df = pd.read_csv(csv_path) #Read “stock_data.csv” file using pandas.
    appl_row = df[df["Company"]=="AAPL"]
    if not appl_row.empty:
        stored_price = float(appl_row.iloc[0]['Price']) #once the we aapl filtered aapl the series will 0
        price_diff = current_price - stored_price
        percent_change = (price_diff/stored_price)*100
        return stored_price,price_diff,percent_change
    else:
        print("No AAPL record found in the CSV")
        return None,None,None

#3.	Email Alert: I will be importing 2 additional module based on the research
def send_email_alert(sender,password,recipient,subject,body):
    msg = MIMEMultipart()
    msg ["From"] = sender
    msg["To"] = recipient
    msg ['subject'] = subject
    msg.attach(MIMEText(body,'plain'))

    
    try:
        with smtplib.SMTP('smtp.gmail.com',587) as server:
            server.starttls()
            server.login(sender,password)
            server.send_message(msg)
        print('email sent successfully')
    except Exception as e:
        print(f"failed to send the emai:{e}")


#Main Logic
def main():
    threshold = 2.0
    sender_email = "aravindrajendran39@gmail.com"
    sender_password = 'lwuh kmnm hwga uufy'
    recipient_email = "aravindhrajendran@yahoo.com"

    current_price = get_current_aapl_price()
    if current_price is None:
        return
    stored_price, price_diff, percent_change = reconcile_price(current_price)
    if stored_price is None:
        return

    print(f'stored:{stored_price} | price_diff: {price_diff:.2f} | current price:{current_price} | Changes:{percent_change:.2f}%')
    if abs (percent_change) >= threshold:
        subject = f'AAPL alert:{'UP' if price_diff > 0 else 'DOWN'} {abs(percent_change):.2f}%'

        body = (
                f'APPLE (AAPL) stock price alert: \n\n'
                f'stored price: ${stored_price}\n'
                f'Current price: ${current_price}\n'
                f'Difference:${price_diff}\n'
                f'Threshold:{threshold}\n'
                f'Link:https://finance.yahoo.com/quote/AAPL/?p=AAPL'
                )
        send_email_alert(sender_email,sender_password,recipient_email,subject,body)
    else:
        print("No changes in the below threshold.No email sent")
        
if __name__ == "__main__":

    main()
