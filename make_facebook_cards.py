#!/usr/bin/python3


"""
A simple example script to get all posts on a user's timeline.
Originally created by Mitchell Stewart.
<https://gist.github.com/mylsb/10294040>
"""
import shutil
import urllib
import facebook
import requests


def some_action(post):
    """ Here you might want to do something with each post. E.g. grab the
    post's message (post['message']) or the post's picture (post['picture']).
    In this implementation we just print the post's created time.
    """
    print(post['created_time'])


# You'll need an access token here to do anything.  You can get a temporary one
# here: https://developers.facebook.com/tools/explorer/
access_token = 'EAACEdEose0cBAEuPgEfzKansiJuC9GK1nYhRdyPUCsMTgDCgHzC9448VmKENPCo3NtT7OT1RTzcWdZCGGLemDZCXFVZAidWT9RYCab0KeFGBmEDZCBZCeOXmt4GyHaam4g5C4b4RvnUTR04TiDFEPse3vDvqKLK1I3mNOZCsTsDDPAFPmBk2epwsmhRtUnOREZD'

# Look at Bill Gates's profile for this example by using his Facebook id.
# user = 'BillGates'
# user = 'prvak'
user = '1641657189'

graph = facebook.GraphAPI(access_token)
#profile = graph.get_object(user)
user = graph.get_object("me")
#print(profile)
#print(profile.friends)
friends = graph.get_connections(user['id'], 'friends')
print(friends)

while True:
    print(friends)
    #for i, friend in enumerate(friends['data']):
    #    id = friend['id']
    #    print(i, len(friends['data']), graph.get_object(id))

    #    #testfile = urllib.URLopener()
    #    #testfile.retrieve("http://graph.facebook.com/v2.8/" + id + "/picture?width=500", friend['name'] + ".jpg")
    #    url = "http://graph.facebook.com/v2.8/" + id + "/picture?width=500"
    #    path = friend['name'] + ".jpg"
    #    r = requests.get(url, stream=True)
    #    with open(path, "wb") as f:
    #        shutil.copyfileobj(r.raw, f)

    print(friends['paging'])
    print()
    print()

    try:
        friends = requests.get(friends['paging']['next']).json()
        #friends = requests.get(friends['paging']['cursors']['after']).json()
    except KeyError:
        # When there are no more pages (['paging']['next']), break from the
        # loop and end the script.
        break

# # posts = graph.get_connections(profile['id'], 'posts')
# 
# # Wrap this block in a while loop so we can keep paginating requests until
# # finished.
# while True:
#     try:
#         # Perform some action on each post in the collection we receive from
#         # Facebook.
#         [some_action(post=post) for post in posts['data']]
#         # Attempt to make a request to the next page of data, if it exists.
#         posts = requests.get(posts['paging']['next']).json()
#     except KeyError:
#         # When there are no more pages (['paging']['next']), break from the
#         # loop and end the script.
#         break

