#!/usr/bin/python2

# TODO: Remove notes no longer linked to any UID
# TODO: Import to specific decks

import uuid
import fnmatch
import markdown
import yaml
import subprocess
import os
import csv
import sys
sys.path.append('/usr/share/anki')

import anki
import anki.importing

def get_git_revision():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()

N_FIELDS = 7

class Note(object):
    def __init__(self, origin_file, uuid, include_reverse,
                 topic,
                 front, back,
                 git_revision,
                 deck):
        self.deck = deck
        self.origin_file = origin_file
        self.uuid = uuid
        self.include_reverse = include_reverse
        self.topic = topic
        self.front = front
        self.back = back
        self.git_revision = git_revision

    def to_fields(self):
        return [
            self.uuid,
            self.topic,
            self.front, self.back,
            'true' if self.include_reverse else '',
            self.origin_file,
            self.git_revision,

            #'' # TAGS  --  can add those.
        ]


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


def load_all_notes():
    git_revision = get_git_revision()
    print 'git rev:', git_revision

    uuids = set()

    my_notes = []

    yaml_files = []
    # TODO: follow symlinks
    for root, dirnames, filenames in os.walk('notes'):
        for filename in fnmatch.filter(filenames, '*.yaml'):
            yaml_files.append(os.path.join(root, filename))

    for path in yaml_files:
        print(path)
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

        deck = data['deck']

        for note_row in data['notes']:
            note_uuid = note_row['uuid']
            try:
                uuid.UUID(note_uuid)
            except ValueError:
                print "Bad UUID", note_uuid, "in", path
                raise
            origin_file = unicode(path)
            if note_uuid in uuids:
                raise Exception("Duplicated UID:" + str(note_uuid))
            uuids.add(note_uuid)
            # print (origin_file, note_uuid)
            # (front) (back) (add-reverse) (origin-file) (note_uuid) (git-revision)
            if 'include_reverse' in note_row:
                include_reverse = note_row['include_reverse']
            else:
                include_reverse = False

            note_topic = topic
            if 'topic' in note_row:
                note_topic = note_row['topic']

            if 'front' not in note_row:
                raise Exception('No front: ' + note_uuid)

            front = markdown.markdown(unicode(note_row['front']))
            back = markdown.markdown(unicode(note_row['back']))

            my_notes.append(Note(
                origin_file = origin_file,
                uuid = note_uuid,
                include_reverse = include_reverse,
                topic = note_topic,
                front = front,
                back = back,
                git_revision = git_revision,
                deck = deck
            ))
    return my_notes

class MyTextImporter(anki.importing.TextImporter):
    pass
    #def noteFromFields(self, fields):
    #    note = super(MyTextImporter, self).noteFromFields(fields)
    #    # TODO: add some tags, too?

    #    #assert len(fields) == N_FIELDS + 1
    #    # [fields...] [comma,divided,tags]
    #    #note.fields = fields[:N_FIELDS]
    #    # note.tags = self.tagsToAdd # [] # TODO
    #    #print(note.fields)
    #    return note

def main():
    collection_path = '/home/prvak/dropbox/anki/User 1/collection.anki2'
    cwd = os.getcwd()
    collection = anki.Collection(collection_path)
    os.chdir(cwd)


    model = collection.models.byName("Basic (and reversed card) - synchronized with anki-decks")

    my_notes = load_all_notes()

    notes_by_deck = {}
    for note in my_notes:
        deck = note.deck
        if deck not in notes_by_deck:
            notes_by_deck[deck] = []
        notes_by_deck[deck].append(note)

    for deck_name, deck_notes in notes_by_deck.iteritems():
        print "Importing into", deck_name

        # Finds or creates deck.
        deck_id = collection.decks.id(deck_name)
        collection.decks.select(deck_id)

        deck = collection.decks.get(deck_id)
        deck['mid'] = model['id']
        collection.decks.save(deck)

        csv_file = 'import_dump.csv'
        imported = 0
        # got_uuids = get_uuids_in_deck(collection, 'Default')
        with open(csv_file, 'wb') as f:
            writer = csv.writer(f, delimiter='\t')
            for note in deck_notes:
                # If the UUID matches, then importing updates the note.

                # NOTE: To skip updating:
                # if (note.origin_file, note.uuid) in got_uuids:
                #     print 'Not adding:', origin_file, uuid
                #     continue

                # TODO: Rewrite as in anki.importing.noteimp

                writer.writerow(map(lambda s: s.encode('utf-8'),
                                    note.to_fields()))
                imported += 1

        if imported > 0:
            print 'Importing...'

            importer = MyTextImporter(collection, csv_file)
            importer.allowHTML = True
            importer.delimiter = '\t'
            importer.initMapping()
            importer.run()
        else:
            print 'Nothing to add.'

        for note in deck_notes:
            cards = collection.findCards('anki-decks-uid:"' + note.uuid + '"')
            for card_id in cards:
                card = collection.getCard(card_id)
                card.did = deck_id
                card.flush()
            print(note.uuid, cards)

    collection.save()
    collection.close()

if __name__ == '__main__':
    main()
