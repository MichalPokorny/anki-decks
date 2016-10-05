#!/usr/bin/python2

# TODO: Remove notes no longer linked to any UID

import markdown
import yaml
import glob
import subprocess
import os
import csv
import sys
sys.path.append('/usr/share/anki')

import anki
import anki.importing

def get_git_revision():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()

class Note(object):
    def __init__(self, origin_file, uuid, include_reverse,
                 topic,
                 front, back,
                 git_revision):
        self.origin_file = origin_file
        self.uuid = uuid
        self.include_reverse = include_reverse
        self.topic = topic
        self.front = front
        self.back = back
        self.git_revision = git_revision

def load_notes_to_import():
    git_revision = get_git_revision()
    print 'git rev:', git_revision

    uuids = set()

    my_notes = []
    for path in glob.glob('notes/**/*.yaml'):
        with open(path) as yf:
            data = yaml.load(yf)

        # if 'uid_tag' in data:
        #     uid_tag = data['uid_tag'] + '/'
        # else:
        #     uid_tag = ''

        if 'topic' in data:
            topic = data['topic']
        else:
            topic = ''

        for note_row in data['notes']:
            uuid = note_row['uuid']
            origin_file = unicode(path)
            if uuid in uuids:
                raise Exception("Duplicated UID:" + str(uuid))
            uuids.add(uuid)
            print (origin_file, uuid)
            # (front) (back) (add-reverse) (origin-file) (uuid) (git-revision)
            if 'include_reverse' in note_row:
                include_reverse = note_row['include_reverse']
            else:
                include_reverse = False

            note_topic = topic
            if 'topic' in note_row:
                note_topic = note_row['topic']

            front = markdown.markdown(unicode(note_row['front']))
            back = markdown.markdown(unicode(note_row['back']))

            my_notes.append(Note(
                origin_file = origin_file,
                uuid = uuid,
                include_reverse = include_reverse,
                topic = note_topic,
                front = front,
                back = back,
                git_revision = git_revision
            ))
    return my_notes

collection_path = '/home/prvak/dropbox/anki/User 1/collection.anki2'
cwd = os.getcwd()
collection = anki.Collection(collection_path)
os.chdir(cwd)

# My Default deck
deck = collection.decks.byName("Default")
deck_id = deck['id']
#collection.decks.get(deck_id)
collection.decks.select(deck_id)

model = collection.models.byName("Basic (and reversed card) - synchronized with anki-decks")

def get_uuids_in_deck(deck_name):
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

my_notes = load_notes_to_import()
csv_file = 'import_dump.csv'
added = 0
got_uuids = get_uuids_in_deck('Default')
with open(csv_file, 'w') as f:
    for note in my_notes:
        if (note.origin_file, note.uuid) in got_uuids:
            print 'Not adding:', origin_file, uuid
            continue
        # TODO: Rewrite as in anki.importing.noteimp

        row = '\t'.join(
            [
                note.uuid,
                note.topic,
                note.front, note.back,
                 'true' if note.include_reverse else '',
                 note.origin_file, note.git_revision
            ]
        )
        print row
        f.write(row.encode('utf-8') + '\n')
        added += 1


if added > 0:
    deck['mid'] = model['id']
    collection.decks.save(deck)

    print 'Importing...'

    importer = anki.importing.TextImporter(collection, csv_file)
    importer.allowHTML = True
    importer.delimiter = '\t'
    importer.initMapping()
    importer.run()
else:
    print 'Nothing to add.'

collection.close()
