"""
    >>> from django.contrib.auth.models import User
    >>> jane = User.objects.create_user('jane', 'jane@example.com', 'toto')
    
    >>> from oauth_provider.models import Resource, Consumer
    >>> resource = Resource(name='api', url='/oauth/photo/')
    >>> resource.save()
    >>> CONSUMER_KEY = 'dpf43f3p2l4k3l03'
    >>> CONSUMER_SECRET = 'kd94hf93k423kf44'
    >>> consumer = Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET, 
    ...                     name='api.client.example', user=jane)
    >>> consumer.save()
    
    
    >>> import time
    >>> parameters = {
    ...     'oauth_consumer_key': CONSUMER_KEY,
    ...     'oauth_signature_method': 'PLAINTEXT',
    ...     'oauth_signature': '%s&' % CONSUMER_SECRET,
    ...     'oauth_timestamp': str(int(time.time())),
    ...     'oauth_nonce': 'requestnonce',
    ...     'oauth_version': '1.0',
    ...     'oauth_callback': 'http://printer.example.com/request_token_ready',
    ...     'scope': 'api', # custom argument to specify Protected Resource
    ... }
    >>> response = c.get("/oauth/request_token/", parameters)
    
    >>> from oauth_provider.models import Token
    >>> token = list(Token.objects.all())[-1]
    
    >>> parameters = {
    ...     'oauth_token': token.key,
    ... }
    >>> response = c.get("/oauth/authorize/", parameters)
    >>> response.status_code
    302
    
    
    >>> c.login(username='jane', password='toto')
    True
    >>> token.is_approved
    0
    >>> response = c.get("/oauth/authorize/", parameters)
    >>> response.status_code
    200
    
    >>> parameters['authorize_access'] = 1
    >>> response = c.post("/oauth/authorize/", parameters)
    >>> response.status_code
    302
    >>> token = Token.objects.get(key=token.key)
    >>> token.is_approved
    1
    
    
    >>> parameters = {
    ...     'oauth_consumer_key': CONSUMER_KEY,
    ...     'oauth_token': access_token.key,
    ...     'oauth_signature_method': 'HMAC-SHA1',
    ...     'oauth_timestamp': str(int(time.time())),
    ...     'oauth_nonce': 'accessresourcenonce',
    ...     'oauth_version': '1.0',
    ...     'format': 'json',
    ... }
    
    
    >>> import oauth2 as oauth
    >>> oauth_request = oauth.Request.from_token_and_callback(access_token,
    ...     http_url='http://testserver/oauth/photo/', parameters=parameters)
    >>> signature_method = oauth.SignatureMethod_HMAC_SHA1()
    >>> signature = signature_method.sign(oauth_request, consumer, access_token)
    
    
    >>> parameters['oauth_signature'] = signature
    >>> response = c.get("/api/v1/courseinstance/", parameters)
    >>> response.status_code
    200
    
    
"""