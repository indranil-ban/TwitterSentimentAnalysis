from flask import Flask,request, url_for, redirect, render_template
from werkzeug.serving import run_simple

import numpy as np
import pandas as pd
import tweepy 
import pickle

# set to True to inform that the app needs to be re-created
to_reload = False
consumer_key= '2yQ5So6NP0k8OTDuKEyE5W8bI'
consumer_secret= 'RcEUgWvKMYOgwedPJwQhwUkEWDboW40AGKDcysSqdYOsmDCBXM'
access_token= '1235877260407607296-Ata6aQEqfY1BfcK5zsD2522UwRd4e9'
access_token_secret= 'PjnogWUP87fPwnkluOpL1qAdo8SZH05GESUauZJNo0X8f'


def get_app():
    print("create app now")
    app = Flask(__name__)
    model = pickle.load(open('posneg_model.pkl', 'rb'))
    vec = pickle.load(open('posneg_vec.pkl', 'rb'))
    
    @app.route("/", methods=["POST","GET"])
    def dashboard():
        val = [x for x in request.form.values()]
        if len(val) != 0:
            keyWord=val[0]
            noOfTweets=val[1]
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
            # tweet_list["text"] = tweet_list["text"].apply(cleantweet)
            # X_final = vectorizer.transform(tweet_list2["text"])
        return render_template("index.html")

    @app.route("/abuseDetection", methods=["POST","GET"])
    def abuseDetection():
        val = [x for x in request.form.values()]
        if len(val) != 0:
            keyWord=val[0]
            noOfTweets=val[1]
            # print(keyWord)
            # print(noOfTweets)
        global to_reload
        to_reload = True
        return render_template("abuseDetection.html")
    
    @app.route("/individualTweetCheck", methods=["POST","GET"])
    def individualTweetCheck():
        val = [x for x in request.form.values()]
        if len(val) != 0:
            print(val[0])
            test = [val[0]]
            test = pd.DataFrame(test)
            test= vec.transform(test[0])
            ans=model.predict(test)
            print(ans)
        global to_reload
        to_reload = True
        return render_template("individualTweetCheck.html",sentiment="Positive")

    return app


class AppReloader(object):
    def __init__(self, create_app):
        self.create_app = create_app
        self.app = create_app()

    def get_application(self):
        global to_reload
        if to_reload:
            self.app = self.create_app()
            to_reload = False

        return self.app

    def __call__(self, environ, start_response):
        app = self.get_application()
        return app(environ, start_response)


# This application object can be used in any WSGI server
application = AppReloader(get_app)

if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)