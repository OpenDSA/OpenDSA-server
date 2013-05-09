import time
import urllib
import random
import urlparse
import oauth2 as oauth
import simplejson

CONSUMER_KEY = "asdfg123456"
CONSUMER_SECRET = "asdfg123456"

class Consumer:
    secret = CONSUMER_SECRET
    key = CONSUMER_KEY
    
class Token:
    pass

consumer = Consumer()

BASE_URL                                = "https://plus.cs.hut.fi"
REQUEST_TOKEN_URL                       = BASE_URL + "/oauth/request_token/"
AUTHORIZE_URL                           = BASE_URL + "/oauth/authorize/"
ACCESS_TOKEN_URL                        = BASE_URL + "/oauth/access_token/"
CREDENTIAL_URL                          = BASE_URL + "/account/verify_credentials.json"

def get_base_parameters():
    return {
         'oauth_consumer_key': consumer.key,
         'oauth_signature_method': 'PLAINTEXT',
         'oauth_signature': '%s&' % consumer.secret,
         'oauth_timestamp': str(int(time.time())),
         'oauth_nonce': random.random(),
         'oauth_version': '1.0',
         'oauth_callback': 'oob',
         'scope': 'api', # argument to specify Protected Resource
    }


def build_url(url, get_params=None):
    if get_params != None:
        url += ("?", "&")["?" in url] + urllib.urlencode(get_params)
    return url


def fetch_url(url, get_params=None, post_params=None):
    url = build_url(url, get_params)
    
    if post_params != None:
        return urllib.urlopen(url, urllib.urlencode(post_params)).read()
    else:
        return urllib.urlopen(url).read()

def get_request_token():
    parameters                          = get_base_parameters()
    response                            = fetch_url(REQUEST_TOKEN_URL, parameters)
    parsed                              = urlparse.parse_qs(response)

    token                               = Token()
    token.key                           = parsed["oauth_token"][0]
    token.secret                        = parsed["oauth_token_secret"][0]
    return token


def get_authorization_link(token):
    return urllib.urlopen(AUTHORIZE_URL + "?" + urllib.urlencode({"oauth_token": token.key})).geturl()


def get_access_token(request_token, verifier):
    parameters                          = get_base_parameters()
    parameters['oauth_token']           = request_token.key
    parameters['oauth_signature']       = '%s&%s' % (consumer.secret, request_token.secret)
    parameters['oauth_verifier']        = verifier
    
    response                            = fetch_url(ACCESS_TOKEN_URL, post_params=parameters)
    parsed                              = urlparse.parse_qs(response)
    token                               = Token()
    token.secret                        = parsed["oauth_token_secret"][0]
    token.key                           = parsed["oauth_token"][0]
    return token


def get_protected_resource(url, access_token):
    parameters                          = get_base_parameters()
    parameters['oauth_token']           = access_token.key
    parameters['oauth_signature_method']= 'HMAC-SHA1'
        
    oauth_request = oauth.Request.from_token_and_callback(access_token, 
                                                          http_url=url, 
                                                          parameters=parameters)
    signature_method                    = oauth.SignatureMethod_HMAC_SHA1()
    signature                           = signature_method.sign(oauth_request, consumer, access_token)
    parameters['oauth_signature']       = signature

    response                            = fetch_url(url, get_params=parameters)
    try:
        return simplejson.loads(response)
    except:
        print response
        return None

def main():

    request_token = get_request_token()

    print "Go to this url and authorize token"
    print get_authorization_link(request_token)
    verifier = raw_input("Please input verifier: ").strip()
    access_token = get_access_token(request_token, verifier)

    screen_name = get_protected_resource(CREDENTIAL_URL, access_token)["screen_name"]
    print "Hello %s! Input an URL and I'll display the contents:" % screen_name
    input = "initial"
    while True:
        base = BASE_URL + "/api/v1/"
        input = raw_input(base).strip()
        if input == "":
            break
        
        try:
            resource = get_protected_resource(base + input, access_token)
            print simplejson.dumps(resource, indent=4)
        except:
            pass

main()