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

csv_file = 'import_dump.csv'
added = 0
with open(csv_file, 'wb') as f:
    path = 'cards/git.yaml'

    with open(path) as yf:
        data = yaml.load(yf)

    git_revision = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
    print 'git rev:', git_revision

    writer = csv.writer(f, delimiter='\t')
    for x in data:
        origin_file, uid = unicode(path), unicode(str(x['uid']))
        print (origin_file, uid)
        if (origin_file, uid) in got_uids:
            print 'Not adding:', origin_file, uid
            continue
        # (front) (back) (add-reverse) (origin-file) (uid) (git-revision)
        if x['include_reverse']:
            include_reverse = 'true'
        else:
            include_reverse = ''

        front = markdown.markdown(x['front'])
        back = markdown.markdown(x['back'])

        writer.writerow([front, back, include_reverse,
                         origin_file, uid, git_revision])
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
