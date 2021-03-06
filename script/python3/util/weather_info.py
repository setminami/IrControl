# -*- coding: utf-8 -*-
# this made for  python3.5.3

import sys, pycurl, json, pytz, dateutil.parser
import traceback, time
from io import BytesIO
from datetime import datetime, timedelta

from util.schedule import Schedule
from util import module_logger

DEBUG = False

class WeatherInfo(object):

    def __init__(self, day: datetime, setting, schedule, tz):
        self.PARAMS = {'latitude': setting['location']['latitude'], 'longitude': setting['location']['longitude']}
        self.update_min = setting['cache_update_freq_min']
        self.TZ = pytz.timezone(tz)
        self.TIMESHIFTS = schedule # TIMESHIFTS in yaml
        self._day = day
        self.logger = module_logger(__name__)

    def sunlights(self):
        lat, lng, today = self.PARAMS['latitude'], self.PARAMS['longitude'], self._day.strftime('%Y-%m-%d')
        url_path = 'https://api.sunrise-sunset.org/json'
        retries_left = 5
        # cannot use with as yield?
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url_path + '?lat=%s&lng=%s&formatted=0&date=%s'%(lat, lng, today))
        b = BytesIO()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)
        curl.setopt(pycurl.VERBOSE, DEBUG)
        while retries_left > 0:
            try:
                curl.perform()
                self._sunlights = json.loads(b.getvalue().decode('UTF-8'))
                self.logger.debug(self._sunlights)
                self.fetched_result = datetime.now() \
                    if self._sunlights['status'] == 'OK' else None # as success flag
                break
            except:
                if retries_left == 0:
                    traceback.print_exc()
                    exit(1)
                else:
                    self.logger.info('retry pycurl %d'%retries_left)
                    retries_left -= 1
                    time.sleep(2)
                    continue
        curl.close()

    def _convByTZ(self, utcstr):
        self.logger.debug('call {}({})'.format(sys._getframe().f_code.co_name, utcstr))
        self.logger.debug(self._sunlights)
        return dateutil.parser.parse(utcstr).astimezone(self.TZ)

    def _recallAPI(self, f):
        if (not hasattr(self, 'fetched_result')) or \
            (hasattr(self, 'fetched_result') and (self.fetched_result is None or \
            datetime.now() > (self.fetched_result + timedelta(minutes=self.update_min)))):
            f()
        self.logger.debug('call {} : {}'.format(sys._getframe().f_code.co_name, self._sunlights))

    def _parse_schedule_items(self, item_name):
        """ calculate time for item_name from schedule settings """
        item = self.TIMESHIFTS[item_name]
        display = item['display']
        time = self._parse_trigger_time(item['schedule'])
        operations = item['operations']
        return Schedule(item_name, display, time, operations)

    # TODO: organize logics
    def _parse_trigger_time(self, schedule):
        time, rel = schedule['time'], schedule['relative_time_sec']
        if isinstance(time, str):
            time = time.split('.') if time is not '---' else time

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
            except SyntaxError as se:
                # eval() Error property not found
                try:
                    start_time = datetime.strptime(time[0], '%Y-%m-%dT%H%M')
                except:
                    try:
                        start_time = datetime.now(self.TZ)
                    except :
                        traceback.print_exc()
                        print('Couldnt parse %s'%(time[0]))
                        exit(1)
        else:
            traceback.print_exc()
            print('TIMESHIFTS.schedule.time settings incorrect. @%s'%(item_name))
            exit(1)
        return start_time + timedelta(seconds=rel)


    @property
    def day(self): # day of the weather instance (hhmmss is no effect)
        return self._day
    @day.setter
    def day(self, date: datetime):
        self._day = date
        self.sunlights() # if update _day, also update apicall forcely.

    # see also. ledlight.yml.TIMESHFTS
    # sunrise-sunset.org
    ###########################
    ### ** named times ** ###
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
    ##############################################


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
    ######################################################################
    ###                 fixed time shift entries                       ###
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
    def sunrise_glow(self):
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
    ######################################################################
