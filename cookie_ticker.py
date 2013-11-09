#!/usr/bin/env python

import imaplib, re
import os
import time
import socket
import email

username = raw_input("Enter your Gmail email address: ")
password = raw_input("Enter your Gmail password: ")
label_name = "inbox"

#pattern for matching text in the form of "on/in + floor name"
floor_pattern = re.compile('.*(on|in)\s*(foo|black hole|bh|bmf|badass motherfuckers|pecker|destiny|loop|clam|bonfire|bonfaar).*', re.DOTALL)

filename = "food_list.txt"
food_list = [line.strip() for line in open(filename)] #list of food items

def isFoodAnnouncement(subject, message):
    if (containsFoodWord(subject) or containsFoodWord(message)) and(floor_pattern.match(subject) or floor_pattern.match(message)):
        return True
    else:
        return False

def containsFoodWord(text):
    for food in food_list:
        if food in text:
            return True
    return False

imap_host = 'imap.gmail.com'
mail = imaplib.IMAP4_SSL(imap_host, 993) #connect to GMail
mail.login(username, password)

last_id = 0 #  ID of latest checked message. All new messages checked should have an ID > than this value.
current_date = '\"' + time.strftime("%d-%b-%Y").lower() + '\"'
search_string = '(TO "r-h-t@mit.edu" SINCE ' + current_date + ")"

# Get ID of most recent message that matches the search string (if it exists)
try:
    print 'Connecting to ' + label_name + '..'
    mail.select(label_name)
    result, data = mail.search(None, search_string)
    uid_list = data[0].split()
    if uid_list:
        last_id = max(uid_list) #most recent ID
except:
    print 'Error'

while True:
    print 'Waiting for food announcements..'
    try:
        mail.select(label_name)
        result, data = mail.search(None, search_string)
        uid_list = data[0].split()

        for uid in uid_list: #go through each ID that hasn't been looked at and check if relevant message is a food announcement
            if uid > last_id:

                typ, message_data = mail.fetch(uid, '(RFC822)') #get message from ID

                for response_part in message_data:
                    if isinstance(response_part, tuple):
                        message = email.message_from_string(response_part[1])
                        payload = message.get_payload() #get message body if single-part
                        if message.is_multipart():
                            payload = message.get_payload()[0].get_payload() #get message body if multi-part

                        if isFoodAnnouncement(message['subject'].lower(), payload.lower()):
                            print "Food Announcement received!"
                            print message['subject']
                            print payload
                            last_id = uid
        time.sleep(30)
    except:
        print 'Error'
        time.sleep(120)
        imap_host = 'imap.gmail.com'
        mail = imaplib.IMAP4_SSL(imap_host, 993)
        mail.login(username, password)
