# -*- coding: utf-8 -*-
#
# uds/cron.py
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

from datetime import date, datetime, timedelta
from os import makedirs
from os.path import join
from re import compile, split

from bs4 import BeautifulSoup
from textract import process
from django.contrib.auth.models import User

from legal.settings import BASE_DIR, TEST, TEST_TEMP_DIR
from legal.common.glob import ODP, LOCAL_URL
from legal.common.utils import get, sleep, LOGGER, between, adddoc
from legal.sur.models import Party
from legal.uds.glob import TYPES
from legal.uds.models import Publisher, Agenda, Document, DocumentIndex, File, Retrieved


APP = __package__.rpartition('.')[2]

ROOT_URL = 'https://infodeska.justice.cz/'
PUBLISHERS_URL = '{}subjekty.aspx?typ={{}}'.format(ROOT_URL)
LIST_URL = '{}subjekt.aspx?subjkod={{:d}}'.format(ROOT_URL)
DETAIL_URL = '{}vyveseni.aspx?vyveseniid={{:d}}'.format(ROOT_URL)
FILE_URL = '{}soubor.aspx?souborid={{:d}}'.format(ROOT_URL)
DOCUMENT_URL = LOCAL_URL + '/uds/list?id={:d}'
REPO_PREF = TEST_TEMP_DIR if TEST else join(BASE_DIR, 'repo', 'uds')

UPDATE_INTERVAL = timedelta(hours=6)


def cron_publishers():

    def proc_publisher(tag, typ, high=False, subsidiary_region=False, subsidiary_county=False, reports=None):
        pubid = int(tag['href'].rpartition('=')[2])
        name = (
            tag.text.replace('  ', ' ')
            .replace('KS ', 'Krajský soud ')
            .replace('MS ', 'Městský soud ')
            .replace('OS Praha ', 'Obvodní soud Praha ')
            .replace('OS ', 'Okresní soud ')
            .replace('KSZ ', 'Krajské státní zastupitelství ')
            .replace('MSZ ', 'Městské státní zastupitelství ')
            .replace('OSZ Praha ', 'Obvodní státní zastupitelství Praha ')
            .replace('OSZ ', 'Okresní státní zastupitelství ')
        )
        return Publisher.objects.update_or_create(
            name=name,
            defaults={
                'type': typ,
                'pubid': pubid,
                'high': high,
                'subsidiary_region': subsidiary_region,
                'subsidiary_county': subsidiary_county,
                'reports': reports,
                'updated': datetime.now() - UPDATE_INTERVAL})[0]


    def proc_publishers(soup, typ, high=False):
        if high:
            for tag in soup.find_all('a'):
                proc_publisher(tag, typ, high=True)
        else:
            rep = proc_publisher(soup.select('dt a')[0], typ)
            for tag in soup.find_all('dd'):
                cls = tag.get('class', [])
                subsidiary_region = 'pobockakraj' in cls
                subsidiary_county = 'pobockaokres' in cls
                proc_publisher(
                    tag.find('a'),
                    typ,
                    subsidiary_region=subsidiary_region,
                    subsidiary_county=subsidiary_county,
                    reports=rep)

    for typ in TYPES:
        try:
            res = get(PUBLISHERS_URL.format(typ))
            soup = BeautifulSoup(res.text, 'html.parser')
            high = soup.find('div', 'bezlokality')
            lower = soup.find('div', 'slokalitou')
            proc_publishers(high, typ, high=True)
            for reg in lower.find_all('dl'):
                proc_publishers(reg, typ, high=False)
        except:
            pass

    LOGGER.info('Publishers imported')


SPLIT_NUM_RE = compile(r'\D+')
SPLIT_STR_RE = compile(r'[\W\d]+')


def split_numbers(string):

    return list(map(int, filter(bool, split(SPLIT_NUM_RE, string))))


def split_strings(string):

    return list(filter(bool, split(SPLIT_STR_RE, string)))


def parse_ref(ref):

    empty = (None,) * 5

    try:
        left, slash, right = ref.partition('/')
        assert slash
        lnum = split_numbers(left)
        rnum = split_numbers(right)
        assert between(1, len(lnum), 2) and between(1, len(rnum), 3)
        senate = lnum[-2] if len(lnum) == 2 else None
        number = lnum[-1]
        year = rnum[0]
        page = rnum[1] if len(rnum) > 1 and rnum[1] else None
        if 'P A NC' in left.upper():
            register = 'P A NC'
        else:
            strings = split_strings(left)
            assert strings
            if len(strings) == 1:
                register = strings[0].upper()
            else:
                for string in strings:
                    if string[0].isupper():
                        register = string.upper()
                        break
                else:
                    return empty
        assert not senate or senate > 0
        assert register
        assert number > 0
        assert between(1990, year, date.today().year)
        assert not page or page > 0
        return senate, register, number, year, page
    except:
        return empty


def update_index(doc):

    text = [doc.desc]
    for fil in File.objects.filter(document=doc).order_by('id'):
        text.extend([fil.name, fil.text])
    text = '\n\n'.join(text)
    par = {
        'id': doc.id,
        'publisher': doc.publisher,
        'agenda': doc.agenda,
        'posted': doc.posted,
        'text': text,
    }
    if doc.senate:
        par['senate'] = doc.senate
    if doc.register:
        par['register'] = doc.register
    if doc.number:
        par['number'] = doc.number
    if doc.year:
        par['year'] = doc.year
    if doc.page:
        par['page'] = doc.page
    if DocumentIndex.objects.using('sphinx').filter(id=doc.id).exists():
        DocumentIndex.objects.using('sphinx').filter(id=doc.id).delete()
    DocumentIndex.objects.using('sphinx').create(**par)


def cron_update(*args):

    today = date.today()
    if args:
        dates = []
        for arg in args:
            string = arg.split('.')
            dates.append(datetime(*map(int, string[2::-1])))
    else:
        dates = [today + ODP]
    for dat in dates:
        flt = {'subsidiary_region': False, 'subsidiary_county': False}
        if not args:
            flt['updated__lt'] = datetime.now() - UPDATE_INTERVAL
        for publisher in Publisher.objects.filter(**flt).order_by('id'):
            try:
                sleep(1)
                res = get(LIST_URL.format(publisher.pubid))
                assert res.ok
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.find_all('tr')
                if not rows:
                    continue
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 5:
                        continue
                    links = cells[0].select('a[href]')
                    if not links:
                        continue
                    desc = ref = senate = register = number = year = page = agenda = posted = None
                    files = []
                    href = links[0].get('href')
                    if href and href.startswith('vyveseni.aspx?vyveseniid='):
                        try:
                            docid = int(href.partition('=')[2])
                        except ValueError:
                            continue
                        try:
                            posted = date(*map(int, cells[0].text.strip().split('.')[2::-1]))
                        except:
                            continue
                    else:
                        continue
                    if Document.objects.filter(publisher=publisher, posted=posted, docid=docid).exists():
                        continue
                    try:
                        desc = cells[1].text.strip()
                        ref = cells[2].text.strip()
                        senate, register, number, year, page = parse_ref(ref)
                        agenda = Agenda.objects.get_or_create(desc=cells[3].text.strip())[0]
                        anchors = cells[4].find_all('a')
                        if not anchors:
                            continue
                        for anchor in anchors:
                            if not(anchor and anchor.has_attr('href')
                                and anchor['href'].startswith('soubor.aspx?souborid=')):
                                continue
                            fileid = int(anchor['href'].partition('=')[2])
                            span = anchor.find('span', 'zkraceno')
                            filename = span['title'].strip() if span else anchor.text.strip()
                            if not filename:
                                continue
                            if filename.endswith(')'):
                                filename = filename.rpartition(' (')[0]
                            filename = filename.replace(' ', '_')
                            if fileid not in [x[0] for x in files]:
                                files.append((fileid, filename))
                        doc = Document.objects.get_or_create(
                            docid=docid,
                            publisher=publisher,
                            desc=desc,
                            ref=ref,
                            senate=senate,
                            register=register,
                            number=number,
                            year=year,
                            page=page,
                            agenda=agenda,
                            posted=posted,
                        )[0]
                        for fileid, filename in files:
                            if File.objects.filter(fileid=fileid).exists():
                                File.objects.filter(fileid=fileid).update(document=doc)
                                continue
                            infile = get(FILE_URL.format(fileid))
                            assert infile.ok
                            content = infile.content
                            dirname = join(REPO_PREF, str(fileid))
                            makedirs(dirname, exist_ok=True)
                            pathname = join(dirname, filename)
                            with open(pathname, 'wb') as outfile:
                                outfile.write(content)
                                adddoc(APP, join(str(fileid), filename), FILE_URL.format(fileid))
                            try:
                                text = process(pathname).decode()
                                ocr = len(text) < 5
                                if ocr:
                                    text = process(pathname, method='tesseract', language='ces').decode()
                            except:
                                text = ''
                                ocr = False
                            File.objects.update_or_create(
                                fileid=fileid,
                                defaults={
                                    'document': doc,
                                    'name': filename,
                                    'text': text,
                                    'ocr': ocr,
                                }
                            )
                        update_index(doc)
                        if not args or TEST:
                            sleep(.2)
                            for party in Party.objects.filter(check_uds=True):
                                if DocumentIndex.objects.filter(id=doc.id, text__search='"{}"'.format(party.party)):
                                    Retrieved.objects.update_or_create(
                                        uid_id=party.uid_id,
                                        party=party,
                                        document=doc)
                                    if party.uid.email:
                                        Party.objects.filter(id=party.id).update(notify=True)
                                    LOGGER.info(
                                        'New party "{}" detected for user "{}" ({:d})'
                                        .format(
                                            party.party,
                                            User.objects.get(pk=party.uid_id).username,
                                            party.uid_id))
                    except:
                        continue
                LOGGER.debug('Updated "{}", {:%Y-%m-%d}'.format(publisher.name, dat))
                if not args:
                    Publisher.objects.filter(id=publisher.id).update(updated=datetime.now())
            except:
                LOGGER.info('Failed to update "{}", {:%Y-%m-%d}'.format(publisher.name, dat))
        LOGGER.debug('Updated all publishers, {:%Y-%m-%d}'.format(dat))


def cron_genindex():

    for doc in Document.objects.all():
        update_index(doc)
    LOGGER.debug('Index regenerated')


def cron_fixindex():

    num = 0
    for doc in Document.objects.all():
        if not DocumentIndex.objects.using('sphinx').filter(id=doc.id).exists():
            num += 1
            update_index(doc)
    if num:
        LOGGER.info('Index fixed, {:d} record(s) added'.format(num))
    else:
        LOGGER.debug('Index fixed, no records added')


def cron_remove_orphans():

    num = 0
    for doc in Document.objects.all():
        if not File.objects.filter(document=doc).exists():
            num += 1
            DocumentIndex.objects.using('sphinx').filter(id=doc.id).delete()
            doc.delete()
    if num:
        LOGGER.info('Removed {:d} orphan(s)'.format(num))
    else:
        LOGGER.debug('No orphans removed')


def uds_notice(uid):

    text = ''
    docs = Retrieved.objects.filter(uid=uid).order_by('id').distinct()
    if docs:
        text = 'Na úředních deskách byly nově zaznamenány tyto osoby, které sledujete:\n\n'
        for doc in docs:
            lst = [doc.party.party, doc.document.publisher.name, doc.document.desc]
            if doc.document.ref:
                lst.append('sp. zn. {}'.format(doc.document.ref))
            text += ' - {}\n'.format(', '.join(filter(bool, lst)))
            text += '   {}\n\n'.format(DOCUMENT_URL.format(doc.document.id))
        Retrieved.objects.filter(uid=uid).delete()
        LOGGER.info(
            'Non-empty notice prepared for user "{}" ({:d})'.format(User.objects.get(pk=uid).username, uid))
    Party.objects.filter(uid=uid).update(notify=False)
    return text
