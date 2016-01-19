import tweepy, os 
  
def tweet(photo_path, text):
    secret_key_filepath = os.path.join(os.path.dirname(__file__), '_secret_key.py')

    if os.path.isfile(secret_key_filepath):
        from _secret_key import consumer_key, consumer_secret, access_token, access_token_secret
    else:
        raise ValueError('Not twitter keys')

    # OAuth process, using the keys and tokens  
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)  
    auth.set_access_token(access_token, access_token_secret)  
  
    # Creation of the actual interface, using authentication  
    api = tweepy.API(auth)    
    api.update_with_media(str(photo_path), status=str(text))
#    api.update_status(status=text)

