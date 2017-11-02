''' tweet out city factoids '''
import settings
from TwitterAPI import TwitterAPI

api = TwitterAPI(settings.API_KEY,
                 settings.API_SECRET,
                 settings.ACCESS_TOKEN,
                 settings.ACCESS_SECRET)

status = 'test'
resp = api.request('statuses/update', {'status': status})
if resp.status_code == 200:
    print('tweet successful')
else:
    print('twitter request returned with status code %d: %s',
          resp.status_code,
          resp.text)
