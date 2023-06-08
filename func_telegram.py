import ccxt
from time import sleep, time
import json
#from mainFunctions import *
from json import dumps
import time
import config
import requests



class Notify_telegram:
    messages = []

    def append_message(self, client, channelName, message):
        self.messages.append(message)

    def get_messages(self):
        return self.messages

    def destroy(self):
        self.messages = []




def send_message_to_telegram(chat_id, message):
    """
    *** Send message to Telegram ***
    :param chat_id: Telegram chat ID
    :param message: message to send
    :return: response from Telegram

    """
    token ="5631556792:AAGfAHDNv4tN0ogCX4myTHSJir8xXmKdWO8"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }
    #response = requests.post(url, data=payload)
    return response.json()

def append_messages_new(old_message,new_message):
  #long_message = str(old_message) + '\n ||| \n'+ str(new_message) 
  error_messages.add_message(new_message)
  return new_message 
