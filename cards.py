import subprocess
import fnmatch
import os
import yaml
import markdown
import sys

def get_git_revision():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()

class Note(object):
    def __init__(self, origin_file,
                 include_reverse,
                 topic,
                 front, back,
                 git_revision,
                 deck,
                 guid):
        self.deck = deck
        self.origin_file = origin_file
        self.guid = guid
        self.include_reverse = include_reverse
        self.topic = topic
        self.front = front
        self.back = back
        self.git_revision = git_revision

    def to_fields(self):
        return [
            self.topic,
            self.front, self.back,
            'true' if self.include_reverse else '',
            self.origin_file,
            self.git_revision,

            #'' # TAGS  --  can add those.
        ]

def load_all_notes():
    git_revision = get_git_revision()
    print 'git rev:', git_revision

    guids = set()

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
            if not note_row:
                print(path)
                print("no note")
                sys.exit(1)
            if 'guid' not in note_row:
                print(note_row)
                print('No GUID')
                sys.exit(1)
            if 'front' not in note_row or 'back' not in note_row:
                print(note_row)
                print('Missing front or back')
                sys.exit(1)

            note_guid = note_row['guid']
            origin_file = unicode(path)
            if note_guid in guids:
                raise Exception("Duplicated UID:" + str(note_guid))
            guids.add(note_guid)
            if 'include_reverse' in note_row:
                include_reverse = note_row['include_reverse']
            else:
                include_reverse = False

            note_topic = topic
            if 'topic' in note_row:
                note_topic = note_row['topic']

            if 'front' not in note_row:
                raise Exception('No front: ' + note_guid)

            front = unicode(note_row['front'])
            back = unicode(note_row['back'])
            guid = note_row['guid']

            if ('markdown' not in note_row) or (note_row['markdown']):
                front = markdown.markdown(unicode(note_row['front']))
                back = markdown.markdown(unicode(note_row['back']))

            my_notes.append(Note(
                origin_file = origin_file,
                guid = note_guid,
                include_reverse = include_reverse,
                topic = note_topic,
                front = front,
                back = back,
                git_revision = git_revision,
                deck = deck
            ))
    return my_notes
