# -*- coding: utf-8 -*-
# this made for  python3.5.3

import sys, pycurl, json, pytz, dateutil.parser
import traceback
from io import BytesIO
from datetime import datetime, timedelta

from util.schedule import Schedule

class WeatherInfo(object):

    def __init__(self, setting, schedule, tz):
        self.PARAMS = {'latitude': setting['location']['latitude'], 'longitude': setting['location']['longitude']}
        self.update_min = setting['cache_update_freq_min']
        self.TZ = pytz.timezone(tz)
        self.TIMESHIFTS = schedule

    def sunlights(self):
        lat, lng, today = self.PARAMS['latitude'], self.PARAMS['longitude'], datetime.now().strftime('%Y-%m-%d')
        url_path = 'https://api.sunrise-sunset.org/json'
        # cannot use with as yield?
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url_path + '?lat=%s&lng=%s&formatted=0&date=%s'%(lat, lng, today))
        b = BytesIO()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)
        curl.setopt(pycurl.VERBOSE, True)
        try:
            curl.perform()
            self.fetched_time = datetime.now()
            self._sunlights = json.loads(b.getvalue())
        except:
            traceback.print_exc()
        finally:
            curl.close()

    def _convByTZ(self, utcstr):
        return dateutil.parser.parse(utcstr).astimezone(self.TZ)

    def _recallAPI(self, f):
        if (not hasattr(self, 'fetched_time')) or \
            (hasattr(self, 'fetched_time') and \
            datetime.now() > (self.fetched_time + timedelta(minutes=self.update_min))): f()

    def _parse_schedule_items(self, item_name):
        """ calculate time for item_name from schedule settings """
        item = self.TIMESHIFTS[item_name]
        time = self._parse_trigger_time(item['schedule'])
        operations = item['operations']
        return Schedule(item_name, time, operations)


    def _parse_trigger_time(self, schedule):
        time, rel = schedule['time'].split('.'), schedule['relative_time_sec']
        if len(time) == 2:
            if time[1] == 'end': idx = 1
            elif time[1] == 'begin': idx = 0
            else:
                print('TIMESHIFTS.schedule.time settings incorrect. (begin, end) @%s'%(item_name))
                exit(1)
            try:
                start_time = eval('self._%s'%time[0])[idx]
            except:
                traceback.print_exc()
                print('Couldnt eval @ [self._%s]'%time[0])
                exit(1)
        elif len(time) == 1:
            try:
                start_time = eval('self._%s'%time[0])
            except Exception as e:
                traceback.print_exc()
                print('Couldnt eval @ [self._%s]'%(time[0]))
                exit(1)
        else:
            traceback.print_exc()
            print('TIMESHIFTS.schedule.time settings incorrect. @%s'%(item_name))
            exit(1)
        return start_time + timedelta(seconds=rel)


    # see also. ledlight.yml.TIMESHFTS
    # sunrise-sunset.org
    # TODO: sunrise-sunset.org timings of data update
    @property
    def _sunrise(self): # consider other services fortunely
        self._recallAPI(self.sunlights)
        return self._convByTZ(self._sunlights['results']['sunrise'])

    @property
    def _sunset(self):
        self._recallAPI(self.sunlights)
        return self._convByTZ(self._sunlights['results']['sunset'])

    @property
    def _solar_noon(self):
        self._recallAPI(self.sunlights)
        return self._convByTZ(self._sunlights['results']['solar_noon'])

    @property
    def _civil_tw(self):
        self._recallAPI(self.sunlights)
        return (self._convByTZ(self._sunlights['results']['civil_twilight_begin']),
                self._convByTZ(self._sunlights['results']['civil_twilight_end']))

    @property
    def _nautical_tw(self):
        self._recallAPI(self.sunlights)
        return (self._convByTZ(self._sunlights['results']['nautical_twilight_begin']),
                self._convByTZ(self._sunlights['results']['nautical_twilight_end']))

    @property
    def _astronomical_tw(self):
        self._recallAPI(self.sunlights)
        return (self._convByTZ(self._sunlights['results']['astronomical_twilight_begin']),
                self._convByTZ(self._sunlights['results']['astronomical_twilight_end']))

    # utility
    @property
    def timeshift_today(self):
        names = self.TIMESHIFTS.keys()
        # NOTE: cannot eval self in comprehension?
        # calltime = lambda x: eval('self.%s'%x)
        # return { x: calltime(x) for x in names }
        ret = {}
        for x in names: ret[x] = eval('self.%s'%x)
        return ret

    # the repo calculated properties
    @property
    def midnight(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)

    @property
    def astronomical_twilight(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)

    @property
    def nautical_twilight(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)

    @property
    def civil_twilight(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)

    @property
    def sunrise(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)

    @property
    def solar_noon(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)

    @property
    def evening(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)

    @property
    def sunset(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)

    @property
    def twilight(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)

    @property
    def moon(self):
        return self._parse_schedule_items(sys._getframe().f_code.co_name)
