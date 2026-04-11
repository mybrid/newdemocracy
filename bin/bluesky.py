#/usr/bin/env python3
"""
Requirements:

1. Daily merge. Concatenate each days posts.
2. Plain text.  Date header & text body.
3. Date sort.


"""

import argparse
import glob
import json
import logging
import os
from pathlib import Path
import re
import sys

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class Bluesky():
    """Process Bluesky Post JSON files and compile text format."""
    
    """Posts are an list of records. Record:
  {
    "post": {
      "uri": "at://did:plc:qt52xacjyfajvyymcsy3gpz7/app.bsky.feed.post/3mitads5mxk2g",
      "cid": "bafyreibykil3oave3ej4y2br3rloqubct4bxnmx7iq2nkt2jeyz6gkdjsu",
      "author": {
        "did": "did:plc:qt52xacjyfajvyymcsy3gpz7",
        "handle": "mybrid.bsky.social",
        "displayName": "Mybrid Wonderful",
        "avatar": "https://cdn.bsky.app/img/avatar/plain/did:plc:qt52xacjyfajvyymcsy3gpz7/bafkreihs7sd5nrxfgonznnyp64iy4jmffscbfgx7xqvboxi5jivsaz3w4m",
        "associated": {
          "activitySubscription": {
            "allowSubscriptions": "followers"
          }
        },
        "labels": [],
        "createdAt": "2024-12-24T02:10:20.642Z"
      },
      "record": {
        "$type": "app.bsky.feed.post",
        "createdAt": "2026-04-06T12:12:10.415Z",
        "embed": {
          "$type": "app.bsky.embed.external",
          "external": {
            "description": "YouTube video by Belief It Or Not",
            "thumb": {
              "$type": "blob",
              "ref": {
                "$link": "bafkreiewl4avpfccfs3mnflqdbwsuosoa5hqpuvkkuht5kvbp47ynz6rhy"
              },
              "mimeType": "image/jpeg",
              "size": 794944
            },
            "title": "Purity Culture is Violence | Belief It Or Not",
            "uri": "https://www.youtube.com/watch?v=yG8V7nLySLs"
          }
        },
        "facets": [
          {
            "features": [
              {
                "$type": "app.bsky.richtext.facet#link",
                "uri": "https://www.youtube.com/watch?v=yG8V7nLySLs"
              }
            ],
            "index": {
              "byteEnd": 292,
              "byteStart": 261
            }
          }
        ],
        "langs": [
          "en"
        ],
        "text": "Nudity as original sin is a stupid, idiotic and dumb. The Bible just gets worse from there. Declaring mas****tion a sin is anti-health. It is mental abuse. Christianity is first and foremost mental abuse starting with nudity as a sin. \n\nDown with Christianity.\nwww.youtube.com/watch?v=yG8V..."
      },
      "embed": {
        "external": {
          "uri": "https://www.youtube.com/watch?v=yG8V7nLySLs",
          "title": "Purity Culture is Violence | Belief It Or Not",
          "description": "YouTube video by Belief It Or Not",
          "thumb": "https://cdn.bsky.app/img/feed_thumbnail/plain/did:plc:qt52xacjyfajvyymcsy3gpz7/bafkreiewl4avpfccfs3mnflqdbwsuosoa5hqpuvkkuht5kvbp47ynz6rhy"
        },
        "$type": "app.bsky.embed.external#view"
      },
      "bookmarkCount": 0,
      "replyCount": 0,
      "repostCount": 0,
      "likeCount": 0,
      "quoteCount": 0,
      "indexedAt": "2026-04-06T12:12:14.258Z",
      "labels": []
    }
  },
"""    
    
    MODULE_PATH = Path(__file__).parent
    BOOK_PATH = Path().cwd().absolute().parent
    BLUESKY_PATH = BOOK_PATH / "bluesky"
    BOOK_NAME = BOOK_PATH.parts[-1]
    BLUESKY_POST_FILE = BLUESKY_PATH / f"{BOOK_NAME}.bluesky_posts.txt"
    
    def __init__(self):
        self.raw_posts = [] ## test harness reuses the object as global
        self.posts = {}
        
    
    def init_args(self, argv):
        """argparse.ArgumentParser"""
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument(
            'postfile',
            help="Bluesky JSON file of posts."
        )

        self.argparser = parser
        self.args = parser.parse_args(args=argv)
        
        with Path(self.args.postfile).open("r") as post_file:
            self.raw_posts = json.load(post_file)
        return

    def post_date(self, post):
        createDate = post['post']['record']['createdAt']
        return createDate[:createDate.find('T')]
    
    def post_header(self, date):
        header = os.linesep + "-" * 40 + os.linesep
        header += date + os.linesep
        header += "-" * 40 + os.linesep  
        return header

    def post_text(self, post):
        new_text = os.linesep + post['post']['record']['text']
        new_text = new_text.replace('\n', os.linesep)
        return new_text

    def run(self, argv):
        """quick script, all one method"""
        logger.debug(f"BOOK_PATH: {self.BOOK_PATH}")
        logger.debug(f"BOOK_NAME: {self.BOOK_NAME}")
        logger.debug(f"BLUESKY_POST_FILE: {self.BLUESKY_POST_FILE}")
        self.init_args(argv)
        logger.debug(f"Processing {self.args.postfile}")
        
        post_dates = [x['post']['record']['createdAt'] for x in self.raw_posts]
        post_dates = list(set(x[:x.find('T')] for x in post_dates))
        post_dates.sort()
        logger.debug(f"Num post dates: {len(post_dates)}") 
        logger.debug(json.dumps(post_dates, indent=2))
        file_text = ""
        
        current_date = self.post_date(self.raw_posts[0])
        file_text += self.post_header(current_date)
        for post in self.raw_posts:
            post_date = self.post_date(post)
            if post_date != current_date:
                file_text += self.post_header(current_date)
                current_date = post_date
            file_text += self.post_text(post) 
            
        with self.BLUESKY_POST_FILE.open('w') as post_file:
            post_file.write(file_text)
                
        logger.debug(f"{self.BLUESKY_POST_FILE} created.")


# -----------------------------------------------------------------------------
#
#  main
# -----------------------------------------------------------------------------

def main(argv):

    bluesky = Bluesky()
    bluesky.run(argv)

# end main
# -----------------------------------------------------------------------------


if __name__ == '__main__':
    main(sys.argv[1:])

# -----------------------------------------------------------------------------
#                              EOF