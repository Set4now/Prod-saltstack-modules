# 2017.08.11 09:17:19 UTC
#Embedded file name: /usr/lib/python2.7/dist-packages/salt/modules/renderv1.py
from sqlalchemy import *
from jinja2 import Template
import json
import ast
import inspect
import salt
import salt.utils.cridbconnect
import pdb
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class ConnectionError(Exception):
   pass

class APIError(Exception):
   pass

class TemplateNotFound(Exception):
   pass

class PermissionDenied(Exception):
   pass


def __connection(ci_id, query = None, template = None, dbname = None, pillar = None):
    #ci_details = salt.utils.cridbconnect.get_ci(ci_id)
    if template != None:
      query = salt.utils.cridbconnect.read_template(template, pillar)
      if query == False:
#        msg="'Error: Template does not exist!!'"
#        sys.exit(json.dumps(msg))
        sys.tracebacklimit = 0
        raise TemplateNotFound("Template does not exist")
    ci_details = salt.utils.cridbconnect.get_ci(ci_id)
    if ci_details == False:
#       msg="Error: Unable To Fetch Entity Data. Either API URL is Down or Invalid CI!!"
#       sys.exit(json.dumps(msg))
       sys.tracebacklimit = 0
       raise APIError("Unable To Fetch Entity Data. Either API URL is Down or Invalid CI!! ")
    db_url = salt.utils.cridbconnect.get_dburl(ci_details['dbtype'].lower(), ci_details['user'],ci_details['password'], ci_details['host'], ci_details['port'], dbname)
    if db_url == False:
       #msg="Error: Unsupported DataBase"
       #sys.exit(json.dumps(msg))
      sys.tracebacklimit = 0
      raise Exception("Unsupported DataBase")
    engine = create_engine(db_url, pool_recycle=3600)
    try:
      connection = engine.connect()
    except Exception as e:
#      msg="Error: Unable to connect to Database. Message: {}".format(e.message) 
#      sys.exit(json.dumps(msg))
      sys.tracebacklimit = 0
      raise ConnectionError("Unable to connect to Database:- {}".format(e.message))
    return (query, db_url, engine, ci_details, connection)
  


def run_query(ci_id, query = None, template = None, dbname = None, pillar = None):
   query, db_url, engine, ci_details, connection =  __connection(ci_id=ci_id, query = query, template = template, dbname = dbname, pillar = pillar)
   try:
        results = engine.execute(query)
        if results.returns_rows:
            output = []
            for result in results:
                output.append(dict(result))
            try:
              return json.dumps(output, indent=3)
            except:
              return output
        else:
            if results.rowcount == 0:
                return 'Rows Effected: {}'.format(results.rowcount)
            return 'Success, {} row updated'.format(results.rowcount)
   except Exception as e:
         return "Invalid Query" + "\n" + "Error: " + json.dumps(e.message) + "\n" + "Actual Formated Query:" + query



def db_exists(ci_id, workdb, dbname=None):
    query, db_url, engine, ci_details, connection =  __connection(ci_id=ci_id, query = None, template = None, dbname = dbname, pillar = None)
    if ci_details['dbtype'].lower() == "mysql":
      query="show databases"
    if ci_details['dbtype'].lower() == "postgres":
      query="SELECT datname FROM pg_database"
    if ci_details['dbtype'].lower() == "sql server":
      query="SELECT name, state_desc FROM sys.databases"
    res = engine.execute(query)
    existing_databases = []
    for db in res:
        existing_databases.append(db[0])

    if workdb not in existing_databases:
        return 'DataBase not Found'
    else:
        return 'Database exists'


def db_create(ci_id, workdb, dbname=None):
    query, db_url, engine, ci_details, connection =  __connection(ci_id=ci_id, query = None, template = None, dbname = dbname, pillar = None)
    if ci_details['dbtype'].lower() == "mysql":
      query="create database {}".format(workdb)
    if ci_details['dbtype'].lower() == "postgres":
      query="create database {}".format(workdb)
    try:
      if ci_details['dbtype'].lower() == "postgres":
        conn = connection.execute("commit")
        results= connection.execute(query)
      else:
        results = engine.execute(query)
      if results.rowcount == 0:
        return 'Rows Effected: {}'.format(results.rowcount)
      return 'Success, {} row updated'.format(results.rowcount) + "\n" + "The DataBase has been successfully created."
    except Exception as e:
      return "Invalid Query" + "\n" + "Error: " + json.dumps(e.message)


def db_remove(ci_id, workdb, dbname=None):
    query, db_url, engine, ci_details, connection =  __connection(ci_id=ci_id, query = None, template = None, dbname = dbname, pillar = None)
    if ci_details['dbtype'].lower() == "mysql":
      query="drop database {}".format(workdb)
    if ci_details['dbtype'].lower() == "postgres":
      query="drop database {}".format(workdb)
    if ci_details['dbtype'].lower() == "sql server":
      query="drop database {}".format(workdb)
    try:
      if ci_details['dbtype'].lower() == "postgres":
        conn = connection.execute("commit")
        results= connection.execute(query)
      elif ci_details['dbtype'].lower() == "sql server":
        conn = connection.execute("commit")
        results= connection.execute(query)
      else:
        results = engine.execute(query)
      if results.rowcount == 0:
        return 'Rows Effected: {}'.format(results.rowcount) + "\n" + "The DataBase has been successfully removed."
      return "Database removed"
    except Exception as e:
      return "Invalid Query" + "\n" + "Error: " + json.dumps(e.message)


def db_create_user(ci_id, user, password=None, dbname=None):
    query, db_url, engine, ci_details, connection =  __connection(ci_id=ci_id, query = None, template = None, dbname = dbname, pillar=None)
    if ci_details['dbtype'].lower() == "oracle":
      query="CREATE USER {} IDENTIFIED BY {}".format(user, password)
    if ci_details['dbtype'].lower() == "mysql":
      query="CREATE USER '{}' IDENTIFIED BY '{}'".format(user, password)
    if ci_details['dbtype'].lower() == "postgres":
      query="CREATE USER {} WITH PASSWORD '{}'".format(user, password)
    if ci_details['dbtype'].lower() == "sql server":
      query="CREATE USER {} FOR LOGIN {}".format(user, user)
    try:
      results = engine.execute(query)
      if results.rowcount == 0:
        return 'Rows Effected: {}'.format(results.rowcount) + "\n" + "The user has been succesfully created."
      return "Created."
    except Exception as e:
      return "Invalid Query" + "\n" + "Error: " + json.dumps(e.message)


def db_user_exists(ci_id, user, dbname=None):
    query, db_url, engine, ci_details, connection =  __connection(ci_id=ci_id, query = None, template = None, dbname = dbname, pillar = None)
    if ci_details['dbtype'].lower() == "mysql":
      query='SELECT User FROM mysql.user'
    if ci_details['dbtype'].lower() == "oracle":
      query='select * from all_users'
    if ci_details['dbtype'].lower() == "postgres":
      query='SELECT usename FROM pg_user'
    if ci_details['dbtype'].lower() == "sql server":
      query='SELECT * FROM sys.server_principals'
    res = engine.execute(query)
    existing_users = []
    for USER in res:
        existing_users.append(USER[0])
    if user.lower() not in (name.lower() for name in existing_users):
        return 'User not Found'
    else:
        return 'User exists'

def db_table_exists(ci_id, tablename, dbname=None):
    query, db_url, engine, ci_details, connection =  __connection(ci_id=ci_id, query = None, template = None, dbname = dbname, pillar = None)
    if ci_details['dbtype'].lower() == "mysql":
      query='show tables'
    if ci_details['dbtype'].lower() == "oracle":
      query='select tablespace_name, table_name from dba_tables'
    res = engine.execute(query)
    existing_tables = []
    for table in res:
      existing_tables.append(table[0])
    if tablename.lower() not in (tablename.lower() for tablename in existing_tables):
      return 'Table does not exists'
    else:
      return 'Table exists'


def run_read_only_query(ci_id, query = None, template = None, dbname = None, pillar = None):
   query, db_url, engine, ci_details, connection =  __connection(ci_id=ci_id, query = query, template = template, dbname = dbname, pillar = pillar)
   invalid_commands=["INSERT","UPDATE","DELETE","CREATE","ALTER","DROP","TRUNCATE","COMMENT","RENAME","MERGE","GRANT","REVOKE","COMMIT","ROLLBACK"]
   #invalid_commands=["UPDATE"]
   for i in invalid_commands:
     if query.startswith(i) or query.startswith(i.lower()):
       sys.tracebacklimit = 0
       raise PermissionDenied("Not Permitted To Run Anything Except SELECT query")
   try:
         results = engine.execute(query)
         if results.returns_rows:
           output = []
           for result in results:
             output.append(dict(result))
             try:
               return json.dumps(output, indent=3)
             except:
               return output
         else:
           if results.rowcount == 0:
              return 'Rows Effected: {}'.format(results.rowcount)
           return 'Success, {} row updated'.format(results.rowcount)
   except Exception as e:
          return "Invalid Query" + "\n" + "Error: " + json.dumps(e.message) + "\n" + "Actual Formated Query:" + query


