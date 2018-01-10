''' post a tweet from the queued file '''
from datetime import datetime
from bot import settings
import json
import re
from TwitterAPI import TwitterAPI
from urllib.request import Request, urlopen

# tweet generation logic
def get_latin(word, capitalize=False):
    ''' formatting foreign words '''
    text = ''
    word = word.__dict__ if not isinstance(word, dict) else word
    for syllable in word['lemma']:
        text = text + ''.join(l['latin'] for l in syllable)
    text = re.sub('/', '', text)

    if capitalize:
        return text[0].upper() + text[1:]
    return text

def get_tweet():
    ''' create tweet content '''

    seed = datetime.now().time().strftime('%H%M%S%f')
    response = urlopen(Request('https://unfamiliar.city/%s/datafile' % seed))

    city_data = json.loads(response.read().decode('utf-8'))
    city = get_latin(city_data['city_name'], capitalize=True)
    text = 'The city of %s contains a %s' % \
            (city, response['wildlife']['description'])

    tweet_data = {'status': text}
    return tweet_data

# posting logic
try:
    API = TwitterAPI(settings.TWITTER_API_KEY,
                     settings.TWITTER_API_SECRET,
                     settings.TWITTER_ACCESS_TOKEN,
                     settings.TWITTER_ACCESS_SECRET)
except:
    API = None

data = get_tweet()

if data:
    if API:
        r = API.request('statuses/update', data)

        if r.status_code != 200:
            print(r.response)
    else:
        print('----- API unavailable -----')
        print(data)
