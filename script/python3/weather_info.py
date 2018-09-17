# -*- coding: utf-8 -*-
# this made for  python3.5.3

import sys, pycurl, json, pytz, dateutil.parser
from io import BytesIO
from datetime import datetime, timedelta

class WeatherInfo(object):

    def __init__(self, setting, tz):
        self.PARAMS = {'latitude': setting['location']['latitude'], 'longitude': setting['location']['longitude']}
        self.TZ = pytz.timezone(tz)

    def sunlights(self):
        lat, lng, today = self.PARAMS['latitude'], self.PARAMS['longitude'], datetime.now().strftime('%Y-%m-%d')
        url_path = 'https://api.sunrise-sunset.org/json'
        # cannot use with as yield?
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url_path + f('?lat={lat}&lng={lng}&formatted=0&date={today}'))
        b = BytesIO()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)
        curl.setopt(pycurl.VERBOSE, True)
        try:
            curl.perform()
            self.fetched_time = datetime.now()
            self._sunlights = json.loads(b.getvalue())
        except Exception as e:
            return str(e)
        finally:
            curl.close()

    def _convByTZ(self, utcstr):
        return dateutil.parser.parse(utcstr).astimezone(self.TZ)

    def _recallAPI(self, f):
        if (not hasattr(self, 'fetched_time')) or \
            (hasattr(self, 'fetched_time') and \
            datetime.now() > (self.fetched_time + timedelta(minutes=self.PARAMS['update_freq_min']))): f()

    # see also. ledlight.yml.TIMESHFTS
    # sunrise-sunset.org
    @property
    def sunrise(self): # consider other services fortunely
        self._recallAPI(self.sunlights)
        return self._convByTZ(self._sunlights['results']['sunrise'])

    @property
    def sunset(self):
        self._recallAPI(self.sunlights)
        return self._convByTZ(self._sunlights['results']['sunset'])

    @property
    def solar_noon(self):
        self._recallAPI(self.sunlights)
        return self._convByTZ(self._sunlights['results']['solar_noon'])

    @property
    def civil_tw(self):
        self._recallAPI(self.sunlights)
        return (self._convByTZ(self._sunlights['results']['civil_twilight_begin']),
                self._convByTZ(self._sunlights['results']['civil_twilight_end']))

    @property
    def nautical_tw(self):
        self._recallAPI(self.sunlights)
        return (self._convByTZ(self._sunlights['results']['nautical_twilight_begin']),
                self._convByTZ(self._sunlights['results']['nautical_twilight_end']))

    @property
    def astronomical_tw(self):
        self._recallAPI(self.sunlights)
        return (self._convByTZ(self._sunlights['results']['astronomical_twilight_begin']),
                self._convByTZ(self._sunlights['results']['astronomical_twilight_end']))

    # the repo calculated properties
    @property
    def midnight(self):
        astro_begin, astro_end = self.astronomical_tw
