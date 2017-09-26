"""This is custom module to fetch roster details from CMDB though http API
   This will take the Entity ID as target not the Entity Name.
   cli..
   salt-ssh --roster <modulename>  <Entity-ID> test.ping
   eg.
   salt-ssh --roster cricloudroster  srv-1499434862679 test.ping
"""


import urllib
import requests
import json
import subprocess
import salt
import salt.config
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import ast

def targets(tgt, tgt_type='glob', **kwargs):
  try:
    opts = salt.config.minion_config('/etc/salt/master.d/integration.conf')
    baseurl = opts["roster_config"]["cmdb_url"]
    key_path = opts["roster_config"]["key_path"]
    token = opts["api"]["authorization.token"]
    url = '{}?where={{%22entityid%22:%22{}%22}}'.format(baseurl, tgt)
    cloud = requests.get(url, headers={ 'Authorization': token }, verify=False ).json()
    final_roster = {}
    roster = {}
    #target=tgt
    my_dict={}
    my_opts={"minion_opts":{}}
    my_dict = ast.literal_eval(cloud['_items'][0]['attributes'])
    if "ipAddress" in my_dict.keys():
      final_roster["host"]=str(my_dict["ipAddress"])
    if "serviceAccount" in my_dict.keys():
      final_roster["user"]=str(my_dict["serviceAccount"])
    final_roster["sudo"]=True
    final_roster['thin_dir']="/etc/salt"
    final_roster['tty']=True
    if "authType" in my_dict.keys():
       if my_dict["authType"] == "key":
         final_roster['priv'] = key_path + my_dict['keyName']
       elif my_dict["authType"] == "password":
         resource_name=my_dict["pmpResourceName"]
         accnt_name=my_dict["pmpAccountName"]
         sdb_url='sdb://vault/{}/{}?password'.format(resource_name, accnt_name)
         password=subprocess.check_output(['salt-run', 'sdb.get', sdb_url]).strip('\n')
         final_roster["passwd"]=password
    if bool(my_opts["minion_opts"]):
      final_roster.update(my_opts)
    roster[tgt] = final_roster
    return roster
  except RuntimeError:
    return "Something Wrong with API. Try Again!!"

