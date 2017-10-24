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
import os
import ast
import sys

def targets(tgt, tgt_type='glob', **kwargs):

  opts=salt.config.minion_config('/etc/salt/master.d/integration.conf')
  baseurl=opts["roster_config"]["cmdb_url"]
  token=opts["api"]["authorization.token"]
  app_url='{}?where={{%22entityid%22:%22{}%22}}'.format(baseurl, tgt)
  app_api_res=requests.get(app_url, headers={ 'Authorization': token }, verify=False ).json()
  
  temp_dict={}
  server_roster={}
  target=tgt
  my_dict={}
  minion_opts={}
  final_server_roster={}
  try:
    if bool(app_api_res['_items'][0]['attributes']) and bool(app_api_res['_items'][0]['parententityid']):
      server_tgt=app_api_res['_items'][0]['parententityid']
      if app_api_res['_items'][0]['entitytype'] == "Sub-System":
        my_dict = ast.literal_eval(app_api_res['_items'][0]['attributes'])
        if my_dict["pmpResourceName"]:
          if my_dict["pmpAccountName"]:
            resource_name=my_dict["pmpResourceName"]
            account_name=my_dict["pmpAccountName"]      
            sdb_url='sdb://vault/{}/{}?password'.format(resource_name, account_name)
            password=subprocess.check_output(['salt-run', 'sdb.get', sdb_url]).strip('\n')
            minion_opts["tomcat-manager.user"] = my_dict["serviceAccount"]
            minion_opts["tomcat-manager.passwd"] = password
#            return minion_opts.update(my_dict)
#            return dict(minion_opts.items() + my_dict.items())
        try:  
          server_url='{}?where={{%22entityid%22:%22{}%22}}'.format(baseurl, app_api_res['_items'][0]['parententityid'])
          server_api_response=requests.get(server_url, headers={ 'Authorization': token }, verify=False ).json()         
          temp_dict=ast.literal_eval(server_api_response['_items'][0]['attributes'])
          if server_api_response['_items'][0]['entitytype'] == "Server":
            if "ipaddress" in temp_dict.keys():
               server_roster["host"]=str(temp_dict["ipaddress"])
            if "serviceAccount" in temp_dict.keys():
               server_roster["user"]=str(temp_dict["serviceAccount"])
               #server_roster["user"]= "root" 
            server_roster["sudo"]="True"
            server_roster["thin_dir"]="/etc/salt"
            server_roster["tty"]="True"
            if "authType" in temp_dict.keys():
              if temp_dict["authType"] == "key":
                server_roster['priv']=key_path + temp_dict['keyName']
              elif temp_dict["authType"] == "password":
                resource_name=temp_dict["pmpResourceName"]
                account_name=temp_dict["pmpAccountName"]
                sdb_url='sdb://vault/{}/{}?password'.format(resource_name, account_name)
                password=subprocess.check_output(['salt-run', 'sdb.get', sdb_url]).strip('\n')
                server_roster['passwd']=password
          else:
            raise Exception("The Entity You Are Trying To Connect Is Not A SERVER.")
      #      server_tgt=app_api_res['_items'][0]['parententityid']
          server_roster["minion_opts"]=minion_opts
          final_server_roster[server_tgt]=server_roster
       # return server_tgt
          return final_server_roster 
        except:
          return False
  except:
     return False

#print targets("mid-1505285444180")
