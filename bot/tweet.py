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
        text = text + ''.join(l['IPA'] for l in syllable)
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

    options = [animal, get_slogan, translation, weather_today,
               restaurant_review]
    text = random.choice(options)(city, city_data)
    text += '\n' + city_url
    tweet_data = {'status': text}
    return tweet_data


def get_slogan(city, city_data):
    ''' city's slogan '''
    slogan = city_data['slogan'][0].upper() + city_data['slogan'][1:]
    return 'The city of %s: %s' % (city, slogan)


def animal(city, city_data):
    ''' a native species '''
    return 'The city of %s is home to a rare species known as %s: %s' % \
            (city,
             get_latin(city_data['wildlife']['name']),
             city_data['wildlife']['description'].split('.')[0])


def translation(_, city_data):
    ''' the word for hello is ___ '''
    word = random.choice([
        'helloNN',
        'goodbyeNN',
        'thanksNN',
        'sorryNN',
    ])
    return 'To say "%s" in the %s language, say "%s" (%s)' % (
        city_data['dictionary'][word]['translation'],
        get_latin(city_data['language']['name']),
        get_latin(city_data['dictionary'][word]),
        get_ipa(city_data['dictionary'][word])
    )


def weather_today(city, city_data):
    ''' today's weather '''
    platitude = random.choice([
        'Today is a beautiful day in %s.',
        'It\'s a beautiful day in %s.',
    ])
    weather = city_data['weather']['forecast'][0]
    sky = weather['precipitation'] or 'clear skies'
    return u'%s Expect %s and a high of %d\u00BAC' % (
        platitude % city,
        sky,
        float(int(weather['high'] * 10)) / 10)


def restaurant_review(_, city_data):
    ''' we love this local restaurant '''
    return 'Don\'t miss %s, our favorite spot for %s-style cuisine' \
       % (get_latin(city_data['restaurant']['name'], capitalize=True),
          get_latin(city_data['country'], capitalize=True))


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
