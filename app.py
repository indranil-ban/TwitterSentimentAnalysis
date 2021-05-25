from string import punctuation
from flask import Flask, app, request, url_for, redirect, render_template
from werkzeug.serving import run_simple

import numpy as np
import pandas as pd
import re
import tweepy
import pickle

# Twitter API Keys
consumer_key = '2yQ5So6NP0k8OTDuKEyE5W8bI'
consumer_secret = 'RcEUgWvKMYOgwedPJwQhwUkEWDboW40AGKDcysSqdYOsmDCBXM'
access_token = '1235877260407607296-Ata6aQEqfY1BfcK5zsD2522UwRd4e9'
access_token_secret = 'PjnogWUP87fPwnkluOpL1qAdo8SZH05GESUauZJNo0X8f'

# emojis defined
emoji_pattern = re.compile("["
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)


def replace_emojis(t):
    emoji_happy = ["\U0001F600", "\U0001F601", "\U0001F602", "\U0001F603", "\U0001F604", "\U0001F605",
                   "\U0001F606", "\U0001F607", "\U0001F609", "\U0001F60A", "\U0001F642", "\U0001F643", "\U0001F923", r"\U0001F970", "\U0001F60D", r"\U0001F929", "\U0001F618", "\U0001F617",
                   r"\U000263A", "\U0001F61A", "\U0001F619", r"\U0001F972", "\U0001F60B", "\U0001F61B", "\U0001F61C", r"\U0001F92A",
                   "\U0001F61D", "\U0001F911", "\U0001F917", r"\U0001F92D", r"\U0001F92B", "\U0001F914", "\U0001F910", r"\U0001F928", "\U0001F610", "\U0001F611",
                   "\U0001F636", "\U0001F60F", "\U0001F612", "\U0001F644", "\U0001F62C", "\U0001F925", "\U0001F60C", "\U0001F614", "\U0001F62A",
                   "\U0001F924", "\U0001F634", "\U0001F920", r"\U0001F973", r"\U0001F978", "\U0001F60E", "\U0001F913", r"\U0001F9D0"]
    emoji_sad = ["\U0001F637", "\U0001F912", "\U0001F915", "\U0001F922", r"\U0001F92E", "\U0001F927", r"\U0001F975", r"\U0001F976", r"\U0001F974",
                 "\U0001F635", r"\U0001F92F", "\U0001F615", "\U0001F61F", "\U0001F641", r"\U0002639", "\U0001F62E", "\U0001F62F", "\U0001F632",
                 "\U0001F633", r"\U0001F97A", "\U0001F626", "\U0001F627", "\U0001F628", "\U0001F630", "\U0001F625", "\U0001F622", "\U0001F62D",
                 "\U0001F631", "\U0001F616", "\U0001F623"	, "\U0001F61E", "\U0001F613", "\U0001F629", "\U0001F62B", r"\U0001F971",
                 "\U0001F624", "\U0001F621", "\U0001F620", r"\U0001F92C", "\U0001F608", "\U0001F47F", "\U0001F480", r"\U0002620"]
    words = t.split()
    reformed = []
    for w in words:
        if w in emoji_happy:
            reformed.append("happy")
        elif w in emoji_sad:
            reformed.append("sad")
        else:
            reformed.append(w)
    t = " ".join(reformed)
    return t


def replace_smileys(t):
    emoticons_happy = set([':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}', ':D',
                           ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
                           '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
                           'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)', '<3'])

    emoticons_sad = set([':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
                         ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
                         ':c', ':{', '>:\\', ';('])

    words = t.split()
    reformed = []
    for w in words:
        if w in emoticons_happy:
            reformed.append("happy")
        elif w in emoticons_sad:
            reformed.append("sad")
        else:
            reformed.append(w)
    t = " ".join(reformed)
    return t


def replace_contractions(t):
    cont = {"aren't": 'are not', "can't": 'cannot', "couln't": 'could not', "didn't": 'did not', "doesn't": 'does not',
            "hadn't": 'had not', "haven't": 'have not', "he's": 'he is', "she's": 'she is', "he'll": "he will",
            "she'll": 'she will', "he'd": "he would", "she'd": "she would", "here's": "here is",
            "i'm": 'i am', "i've"	: "i have", "i'll": "i will", "i'd": "i would", "isn't": "is not",
            "it's": "it is", "it'll": "it will", "mustn't": "must not", "shouldn't": "should not", "that's": "that is",
            "there's": "there is", "they're": "they are", "they've": "they have", "they'll": "they will",
            "they'd": "they would", "wasn't": "was not", "we're": "we are", "we've": "we have", "we'll": "we will",
            "we'd": "we would", "weren't": "were not", "what's": "what is", "where's": "where is", "who's": "who is",
            "who'll": "who will", "won't": "will not", "wouldn't": "would not", "you're": "you are", "you've": "you have",
            "you'll": "you will", "you'd": "you would", "mayn't": "may not"}
    words = t.split()
    reformed = []
    for w in words:
        if w in cont:
            reformed.append(cont[w])
        else:
            reformed.append(w)
    t = " ".join(reformed)
    return t


def remove_single_letter_words(t):
    words = t.split()
    reformed = []
    for w in words:
        if len(w) > 1:
            reformed.append(w)
    t = " ".join(reformed)
    return t


def cleantweet(t):
    # replace handwritten emojis with their feeling associated
    t = replace_smileys(t)
    t = t.lower()  # convert to lowercase
    # replace short forms used in english  with their actual words
    t = replace_contractions(t)
    # replace unicode emojis with their feeling a@ashchanchlanissociated
    t = replace_emojis(t)
    t = emoji_pattern.sub(r'', t)  # remove emojis other than smiley emojis
    t = re.sub('\\\\u[0-9A-Fa-f]{4}', '', t)  # remove NON- ASCII characters
    t = re.sub("[0-9]", "", t)  # remove numbers # re.sub("\d+", "", t)
    t = re.sub('#', '', t)  # remove '#'
    t = re.sub('@[A-Za-z0–9]+', '', t)  # remove '@'
    t = re.sub('@[^\s]+', '', t)  # remove usernames
    t = re.sub('RT[\s]+', '', t)  # remove retweet 'RT'
    t = re.sub('((www\.[^\s]+)|(https?://[^\s]+))',
               '', t)  # remove links (URLs/ links)
    # remove punctuations
    t = re.sub('[!"$%&\'()*+,-./:@;<=>?[\\]^_`{|}~]', '', t)
    t = t.replace('\\\\', '')
    t = t.replace('\\', '')
    t = remove_single_letter_words(t)  # removes single letter words
    return t

app = Flask(__name__)
posneg_model = pickle.load(open('posneg_model.pkl', 'rb'))
posneg_vec = pickle.load(open('posneg_vec.pkl', 'rb'))
abuse_model = pickle.load(open('abuse_model.pkl', 'rb'))
abuse_vec = pickle.load(open('abuse_vec.pkl', 'rb'))

@app.route("/", methods=["POST", "GET"])
def dashboard():
    total_tweets = 0
    pos_tweets = 0
    neg_tweets = 0
    neu_tweets = 0
    positive = 0
    negative = 0
    neutral = 0
    val = [x for x in request.form.values()]
    if len(val) != 0:
        keyWord = val[0]
        noOfTweets = int(val[1])
        # print(keyWord)
        # print(noOfTweets)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        tweets = tweepy.Cursor(api.search, q=keyWord).items(noOfTweets)
        tweet_list = []
        for tweet in tweets:
            tweet_list.append(tweet.text)
        tweet_list = pd.DataFrame(tweet_list)
        tweet_list["text"] = tweet_list[0].apply(cleantweet)
        X_final = posneg_vec.transform(tweet_list["text"])
        tweet_list["labels"] = posneg_model.predict(X_final)
        total_tweets = len(tweet_list)
        pos_tweets = len(tweet_list[(tweet_list["labels"] == 4)])
        neu_tweets = len(tweet_list[(tweet_list["labels"] == 2)])
        neg_tweets = len(tweet_list[(tweet_list["labels"] == 0)])
        # Clculated result
        positive = round(((pos_tweets * 100)/total_tweets), 1)
        negative = round(((neg_tweets * 100)/total_tweets), 1)
        neutral = round(((neu_tweets * 100)/total_tweets), 1)
    return render_template("index.html", positive=positive, negative=negative, neutral=neutral, total_tweets=total_tweets, val=val)

@app.route("/abuseDetection", methods=["POST", "GET"])
def abuseDetection():
    total_tweets = 0
    valid_tweets = 0
    abuse_tweets = 0
    nonAbusive = 0
    abusive = 0
    val = [x for x in request.form.values()]
    if len(val) != 0:
        keyWord = val[0]
        noOfTweets = int(val[1])
        # print(keyWord)
        # print(noOfTweets)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        # keyword = input("Enter keyword or hashtag to search: ")
        # no_of_tweets = int(input("Enter how many tweets to analyze: "))
        tweets = tweepy.Cursor(api.search, q=keyWord).items(noOfTweets)
        tweet_list = []
        for tweet in tweets:
            tweet_list.append(tweet.text)
        tweet_list = pd.DataFrame(tweet_list)
        tweet_list["text"] = tweet_list[0].apply(cleantweet)
        X_final = abuse_vec.transform(tweet_list["text"])
        tweet_list["labels"] = abuse_model.predict(X_final)
        total_tweets = len(tweet_list)
        valid_tweets = len(tweet_list[(tweet_list["labels"] == 0)])
        abuse_tweets = len(tweet_list[(tweet_list["labels"] == 1)])
        # Clculated result
        nonAbusive = round(((valid_tweets * 100)/total_tweets), 1)
        abusive = round(((abuse_tweets * 100)/total_tweets), 1)
    return render_template("abuseDetection.html", abusive=abusive, nonAbusive=nonAbusive, total_tweets=total_tweets, val=val)

@app.route("/individualTweetCheck", methods=["POST", "GET"])
def individualTweetCheck():
    sentiment = ""
    ans = -1
    ans2 = -1
    val = [x for x in request.form.values()]
    if len(val) != 0:
        print(val[0])
        x = [val[0]]
        test = pd.DataFrame(x)
        y = posneg_vec.transform(test[0])
        ans = posneg_model.predict(y)
        print(ans)
        test2 = abuse_vec.transform(test[0])
        ans2 = abuse_model.predict(test2)
        if(ans == 4):
            sentiment = "Positive"
        elif(ans == 0):
            sentiment = "Negative"
        elif(ans == 2):
            sentiment = "Neutral"
        else:
            sentiment = "Please submit your text to show result"
    return render_template("individualTweetCheck.html", sentiment=sentiment, ans=ans, ans2=ans2, val=val)

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()