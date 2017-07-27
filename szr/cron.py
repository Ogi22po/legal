# -*- coding: utf-8 -*-
#
# szr/cron.py
#
# Copyright (C) 2011-17 Tomáš Pecina <tomas@pecina.cz>
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

from datetime import datetime, timedelta
from hashlib import md5
from urllib.parse import quote
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db.models import Q
from common.utils import get, post, sleep, logger, composeref
from szr.models import Court, Proceedings
from szr.glob import supreme_court, supreme_administrative_court


list_courts = 'public/search.jsp'

list_reports = 'InfoSoud/seznamOkresnichSoudu?kraj={}'

root_url = 'http://infosoud.justice.cz/'

get_proc = 'InfoSoud/public/search.do?org={}&krajOrg={}&cisloSenatu={:d}' \
    '&druhVec={}&bcVec={:d}&rocnik={:d}&typSoudu={}&autoFill=true' \
    '&type=spzn'

nss_url = 'http://www.nssoud.cz/main0Col.aspx?cls=JudikaturaSimpleSearch' \
    '&pageSource=1&menu=187'

nss_get_proc = 'http://www.nssoud.cz/mainc.aspx?cls=InfoSoud&kau_id={:d}'

update_delay = timedelta(hours=6)


def addauxid(p):

    if (p.court_id == supreme_administrative_court) and not p.auxid:
        try:
            res = get(nss_url)
            soup = BeautifulSoup(res.text, 'html.parser')
            form = soup.find('form')
            d = {i['name']: i['value'] for i in form.find_all('input')
                if i['type'] == 'hidden' and i.has_attr('value')}
            if int(p.senate):
                ref = '{} '.format(p.senate)
            else:
                ref = ''
            ref += '{0.register} {0.number:d}/{0.year:d}'.format(p)
            d['_ctl0:ContentPlaceMasterPage:_ctl0:txtSpisovaZnackaFull'] = ref
            res = post(nss_url, d)
            soup = BeautifulSoup(res.text, 'html.parser')
            oc = soup.select('table#_ctl0_ContentPlaceMasterPage__ctl0_grwA') \
                 [0].select('img[src="/Image/infosoud.gif"]')[0]['onclick']
            p.auxid = int(oc.split('=')[-1].split("'")[0])
        except:
            pass


def isreg(c):

    s = c.pk
    return (s[:2] == 'KS') or (s == 'MSPHAAB')


def cron_courts():

    try:
        res = get(root_url + list_courts)
        soup = BeautifulSoup(res.text, 'html.parser')
        Court.objects.get_or_create(id=supreme_court, name='Nejvyšší soud')
        Court.objects.get_or_create(
            id=supreme_administrative_court,
            name='Nejvyšší správní soud')
        upper = soup.find(id='kraj').find_all('option')[1:]
        lower = soup.find(id='soudy').find_all('option')[1:]
        for court in upper + lower:
            Court.objects.get_or_create(
                id=court['value'],
                name=court.string.encode('utf-8'))
    except:  # pragma: no cover
        logger.warning('Error importing courts')
    Court.objects.all().update(reports=None)
    for c in Court.objects.all():
        if isreg(c):
            try:
                sleep(1)
                res = get(root_url + list_reports.format(c.pk))
                soup = BeautifulSoup(res.text, 'xml')
                for r in soup.find_all('okresniSoud'):
                    Court.objects.filter(pk=r.id.string).update(reports=c)
            except:  # pragma: no cover
                logger.warning(
                    'Error setting hierarchy for {}'.format(c.id))
    logger.info('Courts imported')


def p2s(p):

    return '{}, {}'.format(
        p.court_id,
        composeref(p.senate, p.register, p.number, p.year))


def updateproc(p):

    notnew = bool(p.updated)
    p.updated = datetime.now()
    p.save()
    court = p.court_id
    try:
        if court == supreme_administrative_court:
            addauxid(p)
            if not p.auxid:
                return
            url = nss_get_proc.format(p.auxid)
            res = get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            table = soup.find('table', 'frm')
        else:
            if court == supreme_court:
                court_type = 'ns'
            else:
                court_type = 'os'
            url = root_url + get_proc.format(
                court,
                (p.court.reports.id if p.court.reports else p.court.id),
                p.senate,
                quote(p.register.upper()),
                p.number,
                p.year,
                court_type)
            res = get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            table = soup.find('tr', 'AAAA')
        assert table
    except:  # pragma: no cover
        logger.warning(
            'Failed to check proceedings "{0.desc}" ({1}) for user '
            '"{2}" ({0.uid_id:d})'
                .format(
                    p,
                    p2s(p),
                    User.objects.get(pk=p.uid_id).username))
        return False
    hash = md5(str(table).encode()).hexdigest()
    if court != supreme_administrative_court:
        changed = None
        try:
            t = table.find_next_sibling().find_next_sibling().table \
                .tr.td.find_next_sibling().text.split()
            if len(t) == 4:
                changed = datetime(*map(int, list(reversed(t[0].split('.')))
                    + t[1].split(':')))
        except:  # pragma: no cover
            logger.warning(
                'Failed to check proceedings "{0.desc}" ({1}) for user '
                '"{2}" ({0.uid_id:d})'
                    .format(
                        p,
                        p2s(p),
                        User.objects.get(pk=p.uid_id).username))
        if (changed != p.changed) or (hash != p.hash):
            p.notify |= notnew
            if changed:
                p.changed = changed
                logger.info(
                    'Change detected in proceedings "{0.desc}" ({1}) '
                    'for user "{2}" ({0.uid_id:d})'.format(
                        p,
                        p2s(p),
                        User.objects.get(pk=p.uid_id).username))
    elif hash != p.hash:
        p.notify |= notnew
        if notnew:
            p.changed = p.updated
            if p.changed:
                logger.info(
                    'Change detected in proceedings "{0.desc}" ({1}) '
                    'for user "{2}" ({0.uid_id:d})'.format(
                        p,
                        p2s(p),
                        User.objects.get(pk=p.uid_id).username))
    p.hash = hash
    logger.debug(
        'Proceedings "{0.desc}" ({1}) updated for user '
        '"{2}" ({0.uid_id:d})'.format(
            p,
            p2s(p),
            User.objects.get(pk=p.uid_id).username))
    return True


def cron_update():

    p = Proceedings.objects.filter(Q(updated__lte=datetime.now()-update_delay)
        | Q(updated__isnull=True))
    if p:
        p = p.earliest('updated')
        if updateproc(p):
            p.save()


def szr_notice(uid):

    text = ''
    pp = Proceedings.objects.filter(uid=uid, notify=True) \
            .order_by('desc', 'id')
    if pp:
        text = 'V těchto soudních řízeních, která sledujete, ' \
            'došlo ke změně:\n\n'
        for p in pp:
            if p.desc:
                desc = ' ({})'.format(p.desc)
            else:
                desc = ''
            text += ' - {0.court}, sp. zn. {0.senate:d} {0.register} ' \
                '{0.number:d}/{0.year:d}{1}\n'.format(p, desc)
            if p.court_id != supreme_administrative_court:
                if p.court_id == supreme_court:
                    court_type = 'ns'
                else:
                    court_type = 'os'
                text += '   {}\n\n'.format(root_url + get_proc.format(
                    p.court.id,
                    (p.court.reports.id if p.court.reports else p.court.id),
                    p.senate,
                    quote(p.register.upper()),
                    p.number,
                    p.year,
                    court_type))
            elif p.auxid:
                text += '   {}\n\n'.format(nss_get_proc.format(p.auxid))
            p.notify = False
            p.save()
        logger.info(
            'Non-empty notice prepared for user "{}" ({:d})'
                .format(User.objects.get(pk=uid).username, uid))
    return text
