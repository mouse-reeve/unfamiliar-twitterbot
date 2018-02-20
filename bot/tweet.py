''' post a tweet from the queued file '''
from datetime import datetime
import settings
import json
import random
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


def get_ipa(word, capitalize=False):
    ''' formatting foreign words '''
    text = ''
    word = word.__dict__ if not isinstance(word, dict) else word
    for syllable in word['lemma']:
        text = text + ''.join(l['ipa'] for l in syllable)
    text = re.sub('/', '', text)

    if capitalize:
        return text[0].upper() + text[1:]
    return text


def get_tweet():
    ''' create tweet content '''

    seed = datetime.now().time().strftime('%H%M%S%f')
    city_url = 'https://unfamiliar.city/city/%s' % seed
    response = urlopen(Request('%s/datafile' % city_url))

    city_data = json.loads(response.read().decode('utf-8'))
    city = get_latin(city_data['city_name'], capitalize=True)

    options = [animal, slogan]
    text = random.choice(options)(city, city_data)
    text += '\n' + city_url
    tweet_data = {'status': text}
    return tweet_data

def slogan(city, city_data):
    ''' city's slogan '''
    return 'The city of %s: %s' % (city, city_data['slogan'])

def animal(city, city_data):
    ''' a native species '''
    return 'The city of %s is home to a rare species known as %s: %s' % \
            (city,
             get_latin(city_data['wildlife']['name']),
             city_data['wildlife']['description'].split('.')[0])

def translation(_, city_data):
    ''' the word for hello is ___ '''
    return 'In the %s language, "hello" is "%s" (%s)' % (
        get_latin(city_data['language']['name']),
        get_latin(city_data['dictionary']['helloNN']),
        get_ipa(city_data['dictionary']['helloNN'])
    )


# posting logic
try:
    API = TwitterAPI(settings.TWITTER_API_KEY,
                     settings.TWITTER_API_SECRET,
                     settings.TWITTER_ACCESS_TOKEN,
                     settings.TWITTER_ACCESS_SECRET)
except Exception as e:
    print(e)
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
