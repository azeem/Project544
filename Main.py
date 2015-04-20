#!/usr/bin/env python

from Model import Posts
import Util

def main():
    for post in Posts.select().where(Posts.posttypeid == 2).limit(5):
        print("Post ID: {:d}".format(post.id))
        print(Util.getNounPhrases(post.body))

if __name__ == "__main__":
    main()
    # testWiki()
