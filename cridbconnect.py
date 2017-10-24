from sqlalchemy import *
from jinja2 import Template
import json
import ast
import os
import inspect
import salt
import salt.config
import salt.utils.cridbconnect
import pdb
import requests
import subprocess
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_dburl(dbtype, user, password, host, port, dbname = None):
  db_url = ""
  if dbtype == 'mysql':
    if dbname == None:
      db_url = '{}+mysqldb://{}:{}@{}:{}/?charset=utf8&use_unicode=0'.format(dbtype, user, password, host, port)
    else:
      db_url = '{}+mysqldb://{}:{}@{}:{}/{}?charset=utf8&use_unicode=0'.format(dbtype, user, password, host, port, dbname)
  elif dbtype == 'sql server':
    if dbname == None:
      db_url = '{}+pymssql://{}:{}@{}:{}'.format("mssql", user, password, host, port)
    else:
      db_url = '{}+pymssql://{}:{}@{}:{}/{}'.format("mssql", user, password, host, port, dbname)
  elif dbtype == 'oracle':
    if dbname == None:
#      sys.exit(json.dumps('Fatal Error: A valid dbname paramater required for the program to connect to an ORACLE DATABASE.'))
      raise Exception("A valid dbname paramater required for the program to connect to an ORACLE DATABASE.")
    else:
      db_url = '{}+cx_oracle://{}:{}@{}:{}/{}'.format(dbtype, user, password, host, port, dbname)
  elif dbtype in ["postgresql", "postgres"]:
    if dbname == None:
      raise Exception("A valid dbname paramater required for the program to connect to PostgreSQL DATABASE.")
    else:
      db_url = '{}+psycopg2://{}:{}@{}:{}/{}'.format(dbtype, user, password, host, port, dbname)
  else:
    return False
  return db_url



def get_ci(ci_id):
  result = {}
  opts=salt.config.minion_config('/etc/salt/master.d/integration.conf')
  baseurl=opts["roster_config"]["cmdb_url"]
  token=opts["api"]["authorization.token"]
  url='{}?where={{%22entityid%22:%22{}%22}}'.format(baseurl, ci_id)
  #url='http://10.236.220.121:5000/api/v1/viewentities?where={{%22entityid%22:%22{}%22}}'.format(ci_id)
  try:
    cloud = requests.get(url, headers={ 'Authorization': token }, verify=False ).json()
    #cloud=requests.get(url).json()
    my_dict={}
    result={}
    if bool(cloud['_items'][0]['attributes']):
      if cloud['_items'][0]['entitytype'] == "Sub-System" and cloud['_items'][0]['entitysubtype'] == "Database":
        my_dict = ast.literal_eval(cloud['_items'][0]['attributes'])
        resource_name=my_dict["pmpResourceName"]
        account_name=my_dict["pmpAccountName"]
        sdb_url='sdb://vault/{}/{}?password'.format(resource_name, account_name)
        password=subprocess.check_output(['salt-run', 'sdb.get', sdb_url]).strip('\n')
        result['host'] = my_dict['host']
        result['user'] = my_dict['serviceAccount']
        result['password'] = password
        result['port'] = my_dict['port']
        result['dbtype'] = cloud['_items'][0]['technology']
        return result
      elif cloud['_items'][0]['entitytype'] == "PAAS" and cloud['_items'][0]['entitysubtype'] == "DatabaseServices":
        my_dict = ast.literal_eval(cloud['_items'][0]['attributes'])
        resource_name=my_dict["pmpResourceName"]
        account_name=my_dict["pmpAccountName"]
        sdb_url='sdb://vault/{}/{}?password'.format(resource_name, account_name)
        password=subprocess.check_output(['salt-run', 'sdb.get', sdb_url]).strip('\n')
        result['host'] = my_dict['host']
        result['user'] = my_dict['serviceAccount']
        result['password'] = password
        result['port'] = my_dict['port']
        result['dbtype'] = cloud['_items'][0]['technology']
        return result
      else:
        return False
    else:
      return False
  except:
    return False

#print get_ci("dat-1505211219510")

def read_template(template, pillar = None):
  opts=salt.config.minion_config('/etc/salt/master.d/integration.conf')
  template_path = opts["db_templates"]["path"]
  if os.path.exists(template_path + template + ".jinja"):
    with open(template_path + template + ".jinja") as template_data:
      data = template_data.read()
      if pillar != None:
        render_jinja = Template(data)
        query = render_jinja.render(pillar)
      else:
        query = data
  else:
    return False
  return query
