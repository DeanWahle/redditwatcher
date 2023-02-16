import praw
import time
import requests
import json
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText


# Reddit API credentials
reddit = praw.Reddit(client_id='INSERT_CLIENT_ID',
                     client_secret='INSERT_CLIENT_SECRET',
                     username='INSERT_USER',
                     password='INSERT_PASSS',
                     user_agent='INSERT_USER_AGENT')

# List of keywords to look for
keywords = ['this is a keyword', 'this is another', 'popcorn']
old_posts = set()


def send_email(recipient, subject, body):
    try:
        message = MIMEText(body)
        message['to'] = recipient
        message['subject'] = subject
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login("INSERT_EMAIL", "INSERT_PASSWORD")
        server.sendmail("INSERT_EMAIL", recipient, message.as_string())
        print("Email sent successfully")
        server.quit()
    except Exception as e:
        print("Error: ", e)


# TODO Verify twilio toll free number
def send_message(post_title, post_url):
    # Your Twilio Account SID and Auth Token
    account_sid = "INSERT_SID"
    auth_token = "INSERT_AUTH_TOKEN"

    # Your Twilio phone number
    from_number = "INSERT_FROM NUMBER"

    # The number you want to send the SMS to
    to_number = "INSERT_TO_NUMBER"

    # The message you want to send
    message = post_title + "\n" + post_url

    # Build the request URL
    url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(
        account_sid)

    # Set up the request headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    # Set up the request data
    data = {
        "From": from_number,
        "To": to_number,
        "Body": message,
    }

    # Make the request
    response = requests.post(url, auth=(
        account_sid, auth_token), headers=headers, data=data)

    # Check if the request was successful
    if response.status_code == 201:
        print("Message sent successfully.")
    else:
        print("Failed to send message. Error: {}".format(response.text))


def send_message(post_title, post_url):
    """Function to send a text message to your phone"""
    # Replace the placeholders with actual values
    messagetext = f"A new post has been made on Reddit containing your keywords:\n\n{post_title}\n{post_url}"
    phone_number = 'INSERT PHONE NUMBER'
    api_key = 'INSERT API KEY'
    request_url = f"https://api.twilio.com/2010-04-01/Accounts/{api_key}/Messages.json"

    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = 'AC708ce10b5e3d008634b37925d24c44c9'
    auth_token = '00881b4a139423fe5f3dfd054d14550e'
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
            body=messagetext,
            from_='INSERT FROM NUMBER',
            to='INSERT TO NUMBER'
        )

    # Send a text message
    response = requests.post(
        request_url,
        auth=("api", api_key),
        data={
            "To": phone_number,
            "From": "INSERT FROM NUMBER",
            "Body": message
        }
    )

    # Raise an error if the request failed
    response.raise_for_status()


def check_posts():
    """Function to check the latest posts in the subreddit"""
    subreddit = reddit.subreddit('INSERT_SUBREDDIT')
    for post in subreddit.new(limit=50):
        if post.url not in old_posts:
            post_title = post.title
            post_url = post.url
            for keyword in keywords:
                if keyword in post_title.lower():
                    send_email('INSERT_EMAIL', post_title, post_url)
                    send_message(post_title, post_url)
        old_posts.add(post.url)
    print("-----------------------------")


# Continuously check the subreddit every 60 seconds
while True:
    check_posts()
    time.sleep(60)
