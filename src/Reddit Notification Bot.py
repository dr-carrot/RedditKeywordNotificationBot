import praw
import time
import sys
import os
import requests

# The keywords or phrases that the bot looks for.
# Just follow the same format as below. Add or remove words/phrases as necessary.
# Keywords and phrases are NOT case sensitive. However it will match them literally, so make sure you spell them correctly.
#KEYWORDS = ['keyword1', 'keyword2', 'keyphrases also work', 'etc...']

# You can have 1 subreddit or multiple. If you have multiple, separate them with + symbols like I have done in the example.
# Also, you do not need to include the "/r/" part, just the name of the subreddit as shown in the example.
# The subreddit can also just be "all" if you want it to search through every subreddit in existence. (Might get spammy if you have a common or a lot of keywords).

# Main program. Don't mess with anything below here unless you know what you're doing.

def send_to_reddit(submission):
    try:
        reddit.redditor(notifySettings['user']).message(notifySettings['subject'], notifySettings['body'] + submission.shortlink)
        print('Sent new reddit message') # This line is for testing purposes. If you don't want it, you can completely remove this line.
    except Exception as e:
        print(e)
        time.sleep(60)

def send_to_discord(submission):
    try:
        payload = {}
        requests.post(notifySettings.webhook, data = payload)
        print('Sent new discord message') # This line is for testing purposes. If you don't want it, you can completely remove this line.
    except Exception as e:
        print(e)
        time.sleep(8)

def send_message(submission):
    if notifyType.lower() == 'reddit':
        send_to_reddit(submission)
    elif notifyType.lower() == 'discord':
        send_to_discord(submission)

def connect_to_reddit(user, passwd, clientId, clientSecret, userAgent):
    reddit = praw.Reddit(
    username = user,
    password = passwd,
    client_id = clientId,
    client_secret = clientSecret,
    user_agent = userAgent)
    return reddit

        
def find_submissions():
    try:
        while True:
            for submission in reddit.subreddit(subreddits).stream.submissions():
                for keyword in keywords:
                    if keyword.lower() in submission.title.lower() and submission.created_utc > start_time:
                        send_message(submission)
                        break
    except Exception as e:
        print(e)
        time.sleep(60)

def setupProperties():
    #TODO: should be able to read subreddits and keywords out of a file
    assert('BOT_KEYWORDS' in os.environ)
    assert('BOT_SUBREDDITS' in os.environ)
    assert('BOT_NOTIFY_METHOD' in os.environ)
    assert('BOT_USERNAME' in os.environ)
    assert('BOT_PASSWORD' in os.environ)
    assert('BOT_CLIENT_ID' in os.environ)
    assert('BOT_CLIENT_SECRET' in os.environ)

    keywords = os.environ['BOT_KEYWORDS'].split(',')
    subreddits = os.environ['BOT_SUBREDDITS']
    botUser = os.environ['BOT_USERNAME']
    botPass = os.environ['BOT_PASSWORD']
    botClientId = os.environ['BOT_CLIENT_ID']
    botClientSecret = os.environ['BOT_CLIENT_SECRET']
    userAgent = os.environ.get('BOT_USER_AGENT', 'Message Notification Bot, by /u/John_Yuki, dockerized by /u/drCarrotson')

    notifyType = os.environ['BOT_NOTIFY_METHOD']

    notifySettings = {}

    if notifyType.lower() == 'discord':
        assert('BOT_DISCORD_WEBHOOK' in os.environ)
        notifySettings = {'webhook': os.environ['BOT_DISCORD_WEBHOOK']}
    elif notifyType.lower() == 'reddit':
        assert('BOT_REDDIT_USER' in os.environ)
        assert('BOT_REDDIT_MSG_SUBJECT' in os.environ)
        assert('BOT_REDDIT_MSG_BODY' in os.environ)
        notifySettings = {
            'user': os.environ['BOT_REDDIT_USER'],
            'subject': os.environ['BOT_REDDIT_MSG_SUBJECT'],
            'body': os.environ['BOT_REDDIT_MSG_BODY']
        }
    else:
        assert(False)

    return keywords, subreddits, notifyType, botUser, botPass, botClientId, botClientSecret, userAgent, notifySettings


if __name__ == '__main__':
    (keywords, subreddits, notifyType, botUser, botPass, botClientId, botClientSecret, userAgent, notifySettings) = setupProperties()
    start_time = time.time()
    reddit = connect_to_reddit(botUser, botPass, botClientId, botClientSecret, userAgent)
    find_submissions()
