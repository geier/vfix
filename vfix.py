import logging

import vobject

from vdirsyncer.storage.dav.carddav import CarddavStorage
from vdirsyncer.storage.base import Item


BROKEN = 0
OK = 1
REPAIRED = 2


class FixDav(object):
    _davstoragetype = None

    def __init__(self, url, username='', password='', verify=True):
        self.storage = self._davstoragetype(url,
                                            username=username,
                                            password=password,
                                            verify=verify)

    def repaircollection(self):
        for path, etag in self.storage.list():

            item, etag = self.storage.get(path)
            fixed_card, status = self.repairitem(item.raw)
            if status != OK:
                self.storage.update(path, Item(fixed_card), etag)


class FixCardDav(FixDav):
    _davstoragetype = CarddavStorage

    def repairitem(self, vcard_string):
        status = OK
        try:
            # just checking if it parses
            vobject.readOne(vcard_string)
        except:
            vcard_string = repair_newlines_auto(vcard_string)
            status = REPAIRED
            # again
            vobject.readOne(vcard_string)

        vcard_string, status_n = repair_missing_fn(vcard_string)
        status = max(status, status_n)
        vcard_string, status_n = repair_uid(vcard_string)
        status = max(status, status_n)

        return vcard_string, status


def repair_uid(vcard_string):
    orig_string = vcard_string
    vcard = vobject.readOne(vcard_string)
    if 'uid' not in vcard.contents:
        vcard.add('uid')
    if not vcard.contents['uid']:
        vcard.uid.value = generate_random_uid()
        return vcard.serialize(), REPAIRED
    else:
        return orig_string, OK


def repair_missing_fn(vcard_string):
    orig_string = vcard_string
    vcard = vobject.readOne(vcard_string)
    if 'fn' not in vcard.contents:
        fname = vcard.contents['n'][0].valueRepr()
        fname = fname.strip()
        vcard.add('fn')
        vcard.fn.value = fname
        logging.debug('reconstructing FN')
        return vcard.serialize(), REPAIRED
    else:
        return orig_string, OK


def generate_random_uid():
    """generate a random uid, when random isn't broken, getting a
    random UID from a pool of roughly 10^56 should be good enough"""
    import string
    import random
    choice = string.ascii_uppercase + string.digits
    return ''.join([random.choice(choice) for _ in range(36)])


def repair_newlines_auto(vcard_string):

    vcard = vcard_string.split('\n')
    out = list()
    for line in vcard:
        if find_property(line) != -1 and line[0] not in [' ', '\t']:
            out.append(line)
        else:
            out[-1] = out[-1] + ('\\n' + line)
    return '\n'.join(out)


def find_property(string):
    colon_pos = string.find(':')
    semicolon_pos = string.find(';')

    # if there is an escaped ; or : it's probably not a property, and there
    # should be none after it (in fact this case shouldn't happen at all)
    try:
        if string[colon_pos - 1] == '\\':
            colon_pos = -1
    except IndexError:
        pass
    try:
        if string[semicolon_pos - 1] == '\\':
            semicolon_pos = -1
    except IndexError:
        pass

    if colon_pos == -1 and semicolon_pos == -1:
        return -1
    if colon_pos == -1:
        return semicolon_pos
    elif semicolon_pos == -1:
        return colon_pos
    else:
        return min(colon_pos, semicolon_pos)

if __name__ == "__main__":
    import getpass
    print('This is very experimental, please make sure you have a backup.\n'
          'URL means the URL to a CardDAV collection.\n'
          'Good Luck!')
    url = raw_input('URL: ')
    user = raw_input('Username: ')
    password = getpass.getpass('Password: ')

    fixer = FixCardDav(url=url, username=user, password=password)
    fixer.repaircollection()
    print('Your collection should be fixed now.')
