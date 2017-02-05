#!/usr/bin/python2

# TODO: Remove notes no longer linked to any UID
# TODO: Import to specific decks

import cards

import os
import csv
import sys
sys.path.append('/usr/share/anki')

import anki
import anki.importing

N_FIELDS = 7

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

    my_notes = cards.load_all_notes()

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
                if card.did != deck_id:
                    card.did = deck_id
                    card.flush()
            print note.uuid, cards

    collection.save()
    collection.close()

if __name__ == '__main__':
    main()
