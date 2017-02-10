#!/usr/bin/python2

# TODO: Remove notes no longer linked to any UID
# TODO: Import to specific decks

import cards as mod_cards

import os
import csv
import sys

sys.path.append('/usr/share/anki')
import anki
import anki.importing

def get_uuids_in_deck(collection, deck_name):
    got_uuids = set()
    note_ids = collection.findNotes('deck:"' + deck_name + '"')
    for note_id in note_ids:
        note = collection.getNote(note_id)
        if note.model()['id'] != model['id']:
            continue
        uuid, topic, front, back, add_reverse, origin_file, git_revision = note.fields
        got_uuids.add((origin_file, uuid))
    print 'Already got UIDs:', got_uuids
    return got_uuids

def main():
    collection_path = '/home/prvak/dropbox/anki/User 1/collection.anki2'
    cwd = os.getcwd()
    collection = anki.Collection(collection_path)
    os.chdir(cwd)


    model = collection.models.byName("Basic (and reversed card) - synchronized with anki-decks")

    my_notes = mod_cards.load_all_notes()

    got_uuids = set(note.uuid for note in my_notes)

    note_ids = collection.findNotes('mid:' + model['id'])
    existing_uids = set()
    for note_id in note_ids:
        n = collection.getNote(note_id)
        if n['anki-decks-uid'] not in got_uuids:
            print(n['anki-decks-uid'])
            print(n.fields)

    collection.close()

if __name__ == '__main__':
    main()
