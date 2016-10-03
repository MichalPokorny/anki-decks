#!/usr/bin/python2
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

class Note(object):
    def __init__(self, origin_file, uid, include_reverse, front, back,
                 git_revision):
        self.origin_file = origin_file
        self.uid = uid
        self.include_reverse = include_reverse
        self.front = front
        self.back = back
        self.git_revision = git_revision

def load_notes_to_import():
    git_revision = get_git_revision()
    print 'git rev:', git_revision

    uids = set()

    my_notes = []
    for path in ['cards/git.yaml', 'cards/cards.yaml',
                 'cards/ruby_ops.yaml', 'cards/terms.yaml',
                 'cards/vim.yaml']:
        with open(path) as yf:
            data = yaml.load(yf)

        for note_row in data:
            origin_file, uid = unicode(path), unicode(str(note_row['uid']))
            if uid in uids:
                raise Exception("Duplicated UID:" + str(uid))
            uids.add(uid)
            print (origin_file, uid)
            # (front) (back) (add-reverse) (origin-file) (uid) (git-revision)
            if 'include_reverse' in note_row:
                include_reverse = note_row['include_reverse']
            else:
                include_reverse = False

            front = markdown.markdown(unicode(note_row['front']))
            back = markdown.markdown(unicode(note_row['back']))

            my_notes.append(Note(
                origin_file = origin_file,
                uid = uid,
                include_reverse = include_reverse,
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

# model = collection.models.byName("Basic (and reversed card) - synchronized with anki-decks")
model = collection.models.byName("Basic (and reversed card) - synchronized with anki-decks")

got_uids = set()

note_ids = collection.findNotes("deck:Default")
for note_id in note_ids:
    note = collection.getNote(note_id)
    if note.model()['id'] != model['id']:
        continue

    front, back, add_reverse, origin_file, uid, git_revision = note.fields
    got_uids.add((origin_file, uid))

print 'Already got UIDs:', got_uids

my_notes = load_notes_to_import()
csv_file = 'import_dump.csv'
added = 0
with open(csv_file, 'w') as f:
    for note in my_notes:
        if (note.origin_file, note.uid) in got_uids:
            print 'Not adding:', origin_file, uid
            continue
        # (front) (back) (add-reverse) (origin-file) (uid) (git-revision)

        # TODO: Rewrite as in anki.importing.noteimp

        row = '\t'.join(
            [note.front, note.back,
             'true' if note.include_reverse else '',
             note.origin_file, note.uid, note.git_revision]
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
