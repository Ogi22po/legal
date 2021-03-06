# -*- coding: utf-8 -*-
#
# knr/utils.py
#
# Copyright (C) 2011-19 Tomáš Pecina <tomas@pecina.cz>
#
# This file is part of legal.pecina.cz, a web-based toolbox for lawyers.
#
# This application is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This application is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from datetime import timedelta
from json import loads
from urllib.parse import quote, unquote

from django.template import Context, Template

from legal.settings import MAPKEY
from legal.common.utils import getpreset, famt, getcache


def getvat():

    return getpreset('VAT')


def findloc(addr):

    if not addr:
        return None
    addr = quote(unquote(addr).encode('utf-8'))
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&language=cs&sensor=false&key={}'.format(addr, MAPKEY)
    res = getcache(url, timedelta(weeks=1))[0]
    if not res:
        return None
    res = loads(res)
    if res['status'] != 'OK':
        return None
    res = res['results'][0]
    loc = res['geometry']['location']
    return res['formatted_address'], round(loc['lat'], 7), round(loc['lng'], 7)


def finddist(from_lat, from_lon, to_lat, to_lon):

    url = (
        'https://maps.googleapis.com/maps/api/distancematrix/json?origins={:f},{:f}&destinations={:f},{:f}'
        '&mode=driving&units=metric&language=cs&sensor=false&key={}'.format(from_lat, from_lon, to_lat, to_lon, MAPKEY))
    res = getcache(url, timedelta(weeks=1))[0]
    if not res:
        return None, None
    res = loads(res)
    if res['status'] != 'OK':
        return None, None
    res = res['rows'][0]['elements'][0]
    if res['status'] != 'OK':
        return None, None
    return res['distance']['value'], res['duration']['value']


def convi(arg):

    return famt(int(arg))


def convf(arg, num):

    tpl = Template('{{{{ var|floatformat:"{:d}" }}}}'.format(num))
    con = Context({'var': arg})
    return tpl.render(con)
