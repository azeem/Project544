#!/usr/bin/env python

from Model import Posts

def main():
    for Post in Posts.select().where(Posts.posttypeid == 1).limit(5):
        print(Post.title)

if __name__ == "__main__":
    main()
