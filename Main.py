#!/usr/bin/env python

from Model import Posts
import Util

def main():
    for Post in Posts.select().where(Posts.posttypeid == 1).limit(5):
        print(Util.stripTags(Post.body))

if __name__ == "__main__":
    main()
