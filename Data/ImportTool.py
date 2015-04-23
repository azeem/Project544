#!/usr/bin/env python2
import sqlite3
import os
import xml.etree.cElementTree as etree
import logging

ANATHOMY = {
 'Badges': {
  'Id':'INTEGER PRIMARY KEY',
  'UserId':('INTEGER', 'Users(Id)'),
  'Name':'TEXT',
  'Date':'DATETIME',
 },
 'Comments': {
  'Id':'INTEGER PRIMARY KEY',
  'PostId':('INTEGER', 'Posts(Id)'),
  'Score':'INTEGER',
  'Text':'TEXT',
  'CreationDate':'DATETIME',
  'UserId':('INTEGER', 'Users(Id)'),
  'UserDisplayName': 'TEXT'
 },
 'Posts': {
  'Id':'INTEGER PRIMARY KEY', 
  'PostTypeId':'INTEGER', # 1: Question, 2: Answer
  'ParentID':('INTEGER', 'Posts(Id)'), # (only present if PostTypeId is 2)
  'AcceptedAnswerId':'INTEGER', # (only present if PostTypeId is 1)
  'CreationDate':'DATETIME',
  'Score':'INTEGER',
  'ViewCount':'INTEGER',
  'Body':'TEXT',
  'OwnerUserId':('INTEGER', 'Users(Id)'), # (present only if user has not been deleted) 
  'OwnerDisplayName':'TEXT', # (present only if user has not been deleted) 
  'LastEditorUserId':('INTEGER', 'Users(Id)'),
  'LastEditorDisplayName':'TEXT', #="Rich B" 
  'LastEditDate':'DATETIME', #="2009-03-05T22:28:34.823" 
  'LastActivityDate':'DATETIME', #="2009-03-11T12:51:01.480" 
  'CommunityOwnedDate':'DATETIME', #(present only if post is community wikied)
  'Title':'TEXT',
  'Tags':'TEXT',
  'AnswerCount':'INTEGER',
  'CommentCount':'INTEGER',
  'FavoriteCount':'INTEGER',
  'ClosedDate':'DATETIME',
 },
 'Votes': {
  'Id':'INTEGER PRIMARY KEY',
  'PostId':('INTEGER', 'Posts(Id)'),
  'UserId':('INTEGER', 'Users(Id)'),
  'VoteTypeId':'INTEGER',
           # -   1: AcceptedByOriginator
           # -   2: UpMod
           # -   3: DownMod
           # -   4: Offensive
           # -   5: Favorite
           # -   6: Close
           # -   7: Reopen
           # -   8: BountyStart
           # -   9: BountyClose
           # -  10: Deletion
           # -  11: Undeletion
           # -  12: Spam
           # -  13: InformModerator
  'CreationDate':'DATETIME',
  'BountyAmount':'INTEGER'
 },
 'Users': {
  'Id':'INTEGER PRIMARY KEY',
  'Reputation':'INTEGER',
  'CreationDate':'DATETIME',
  'DisplayName':'TEXT',
  'LastAccessDate':'DATETIME',
  'WebsiteUrl':'TEXT',
  'Location':'TEXT',
  'Age':'INTEGER',
  'AboutMe':'TEXT',
  'Views':'INTEGER',
  'UpVotes':'INTEGER',
  'DownVotes':'INTEGER',
  'EmailHash':'TEXT',
  'ProfileImageUrl': 'TEXT',
  'AccountId': 'INTEGER'
  },
}

def dump_files(file_names, anathomy, 
    dump_path='./', 
    dump_database_name = 'so-dump.db',
    create_query='CREATE TABLE IF NOT EXISTS [{table}]({fields})',
    insert_query='INSERT INTO {table} ({columns}) VALUES ({values})',
    log_filename='so-parser.log'):

 logging.basicConfig(filename=os.path.join(dump_path, log_filename),level=logging.INFO)
 db = sqlite3.connect(os.path.join(dump_path, dump_database_name))

 for file in file_names:
  print "Opening {0}.xml".format(file)
  with open(os.path.join(dump_path, file + '.xml')) as xml_file:
   tree = etree.iterparse(xml_file)
   table_name = file

   fields = ['{0} {1}'.format(name, sql_type if isinstance(sql_type, str) else sql_type[0]) for name, sql_type in anathomy[table_name].items()]
   fields += ['foreign key ({0}) references {1}'.format(name, sql_type[1]) for name, sql_type in anathomy[table_name].items() if isinstance(sql_type, tuple)]
   sql_create = create_query.format(
        table=table_name, 
        fields=", ".join(fields))
   print('Creating table {0}'.format(table_name))

   try:
    logging.info(sql_create)
    db.execute(sql_create)
   except Exception, e:
    logging.warning(e)

   for events, row in tree:
    try:
     logging.debug(row.attrib.keys())

     db.execute(insert_query.format(
        table=table_name, 
        columns=', '.join(row.attrib.keys()), 
        values=('?, ' * len(row.attrib.keys()))[:-2]),
        row.attrib.values())
     print ".",
    except Exception, e:
     logging.warning(e)
     print "x",
    finally:
     row.clear()
   print "\n"
   db.commit()
   del(tree)

if __name__ == '__main__':
 dump_files(ANATHOMY.keys(), ANATHOMY)
