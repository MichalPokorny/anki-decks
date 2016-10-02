#!/usr/bin/python2
import yaml
import os
import csv
import sys
sys.path.append('/usr/share/anki')

import anki
import anki.importing

collection_path = '/home/prvak/Anki/User 1/collection.anki2'
cwd = os.getcwd()
collection = anki.Collection(collection_path)
os.chdir(cwd)

csv_file = 'import_dump.csv'
with open(csv_file, 'wb') as f:
    with open('cards/git.yaml') as yf:
        data = yaml.load(yf)

    writer = csv.writer(f, delimiter='\t')
    for x in data:
        writer.writerow([x['front'], x['back']])


deck_id = 1475450144663
#collection.decks.get(deck_id)
collection.decks.select(deck_id)

#model = collection.models.byName("Basic")

importer = anki.importing.TextImporter(collection, csv_file)
importer.delimiter = '\t'
importer.initMapping()
importer.run()

collection.close()
