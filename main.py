import sqlite3
import csv
import pandas as pd
import string
import random


conn = sqlite3.connect("Sms.db")
mycursor = conn.cursor()

mycursor.execute('''
    CREATE TABLE IF NOT EXISTS Sms (
        MessageId INTEGER PRIMARY KEY,
        MessageType TEXT,
        Contents TEXT
    )
''')

def importData():
    try:
        with open('SMS.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for row in csv_reader:
                if len(row) == 2:
                    mycursor.execute('''
                       INSERT INTO Sms (MessageType, Contents)
                       VALUES (?, ?)
                       ''', (row[0], row[1]))

                else:
                    print("Row incomplete")
            print("Data Imported")
    except sqlite3.Error as e:
        print("Error importing data:", str(e))

def printDatabase():
    mycursor.execute("SELECT * FROM Sms")
    rows = mycursor.fetchall()
    if len(rows) > 0:
        for row in rows:
            print(row)
    else:
        print("Database Empty")

def GetSpam():
    mycursor.execute("SELECT * FROM Sms")
    rows = mycursor.fetchall()
    spamvocabulary = []
    totalWords = 0
    for row in rows:
        key, message_type, contents = row
        formatted_string = formatMessage(contents)
        words = formatted_string.split()
        if (message_type == "spam"):
            for i in range(len(words)):
                totalWords += 1
                word = words[i]
                inlist = False
                for j in range(len(spamvocabulary)):
                    if spamvocabulary[j][0] == word:
                        spamvocabulary[j] = (word, spamvocabulary[j][1] + 1)
                        inlist = True
                        break
                if not inlist:
                    spamvocabulary.append((word, 1))
    return spamvocabulary

def GetHam():
    mycursor.execute("SELECT * FROM Sms")
    rows = mycursor.fetchall()
    hamvocabulary = []
    totalWords = 0
    for row in rows:
        key, message_type, contents = row
        formatted_string = formatMessage(contents)
        words = formatted_string.split()
        if (message_type == "ham"):
            for i in range(len(words)):
                totalWords += 1
                word = words[i]
                inlist = False
                for j in range(len(hamvocabulary)):
                    if hamvocabulary[j][0] == word:
                        hamvocabulary[j] = (word, hamvocabulary[j][1] + 1)
                        inlist = True
                        break
                if not inlist:
                    hamvocabulary.append((word, 1))
    return hamvocabulary

def GetHamTotalW():
    mycursor.execute("SELECT * FROM Sms")
    rows = mycursor.fetchall()
    totalWords = 0
    for row in rows:
        key, message_type, contents = row
        formatted_string = formatMessage(contents)
        words = formatted_string.split()
        if (message_type == "ham"):
            for i in range(len(words)):
                totalWords += 1
    return totalWords

def GetSpamTotalW():
    mycursor.execute("SELECT * FROM Sms")
    rows = mycursor.fetchall()
    totalWords = 0
    for row in rows:
        key, message_type, contents = row
        formatted_string = formatMessage(contents)
        words = formatted_string.split()
        if (message_type == "spam"):
            for i in range(len(words)):
                totalWords += 1
    return totalWords


def calcProbability():
    alpha = 1
    spamProbabilities = []
    hamProbabilities = []
    spam_vocabulary = GetSpam()
    ham_vocabulary = GetHam()
    total_spam_words = GetSpamTotalW()
    total_ham_words = GetHamTotalW()

    for word, count in spam_vocabulary:
        p_w_spam = (count + alpha) / (total_spam_words + alpha * (total_spam_words + total_ham_words))
        spamProbabilities.append((word, p_w_spam))

    for word, count in ham_vocabulary:
        p_w_ham = (count + alpha) / (total_ham_words + alpha * (total_spam_words + total_ham_words))
        hamProbabilities.append((word, p_w_ham))

    return spamProbabilities, hamProbabilities

def sentenceCheck():
    MessageSpamProb = 0
    MessageHamProb = 0
    NumWords = 0
    alpha = 1
    spamProbList, hamProbList = calcProbability()
    mycursor.execute("SELECT MAX(Contents) FROM Sms WHERE Messagetype = 'spam' ORDER BY RANDOM()")
    RandMessage = mycursor.fetchone()
    RandMessage = str(RandMessage)
    FormattedRandMessage = formatMessage(RandMessage)
    words = FormattedRandMessage.split()
    for word in words:
        NumWords += 1
        for w, prob in spamProbList:
            if w == word:
                MessageSpamProb += prob
            else:
                MessageSpamProb += 0
        for w, prob in hamProbList:
            if w == word:
                MessageHamProb += prob
            else:
                MessageHamProb += 0
    if (MessageSpamProb / NumWords * 100) >= (MessageHamProb / NumWords * 100) / 2:
        print(f"Message: {RandMessage}, Probability in Spam: {MessageSpamProb / NumWords * 100}, Probability in Ham: {(MessageHamProb / NumWords * 100) / 2} . This message is likey spam.")
    else:
        print(f"Message: {RandMessage}, Probability in Spam: {MessageSpamProb / NumWords * 100}, Probability in Ham: {(MessageHamProb / NumWords * 100) / 2} . This message is likey safe.")




def formatMessage(message):
    translator = str.maketrans("", "", string.punctuation)
    message_without_punctuation = message.translate(translator)
    formatted_message = message_without_punctuation.lower()

    return formatted_message

importData()
sentenceCheck()
mycursor.close()
conn.close()

