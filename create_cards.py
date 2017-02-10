#!/usr/bin/python2

# TODO: Remove notes no longer linked to any UID

import cards as mod_cards

import os
import csv
import sys

sys.path.append('/usr/share/anki')
import anki

def main():
    collection_path = '/home/prvak/dropbox/anki/User 1/collection.anki2'
    cwd = os.getcwd()
    collection = anki.Collection(collection_path)
    os.chdir(cwd)


    model = collection.models.byName("Basic (and reversed card) - synchronized with anki-decks")

    my_notes = mod_cards.load_all_notes()

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

        for note in deck_notes:
            found_notes = collection.db.list(
                'select id from notes where guid = "' + note.guid + '"')

            if len(found_notes) == 0:
                print("Adding new note.")
                anki_note = anki.notes.Note(col=collection,
                                            model=model)
                anki_note.guid = note.guid
                was_new = True
            else:
                assert len(found_notes) == 1
                anki_note = anki.notes.Note(col=collection,
                                            id=found_notes[0])
                was_new = False

            anki_note['Topic'] = note.topic
            anki_note['Front'] = note.front
            anki_note['Back'] = note.back
            anki_note['Add Reverse'] = ('true' if note.include_reverse else '')
            anki_note['anki-decks-origin-file'] = note.origin_file
            anki_note['anki-decks git revision'] = note.git_revision

            if was_new:
                collection.addNote(anki_note)
            else:
                anki_note.flush()

            cards = collection.findCards('nid:%d' % anki_note.id)
            for card_id in cards:
                card = collection.getCard(card_id)
                if card.did != deck_id:
                    card.did = deck_id
                    card.flush()

    collection.save()
    collection.close()

if __name__ == '__main__':
    main()
