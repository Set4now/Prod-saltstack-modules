from easysnmp import snmp_get, snmp_set, snmp_walk
from easysnmp import *
import json
import datetime
import time


def snmp_fetch(oid, hostname, community="public", version=2):
  data=snmp_get(oid, hostname=hostname, community=community, version=version)
  format_data="{} {} {} {}".format(data.oid,data.oid_index,data.snmp_type,data.value)
  return json.dumps(format_data)


def list_interfaces(oid, hostname, community="public", version=2):
  data=snmp_walk(oid, hostname=hostname, community=community, version=version)
  output = []
  for i in data:
    temp_dict = {}
    temp_dict[i.value]=i.oid_index
    output.append(temp_dict)
  return json.dumps(output, indent=3)

def interface_status_all(hostname, community="public", version=2):
  try:
    interfaces=snmp_walk('IF-MIB::ifDescr', hostname=hostname, community=community, version=version)
    data=snmp_walk('IF-MIB::ifDescr', hostname=hostname, community=community, version=version)
    index_list = []
    final_list = []
    for i in data:
      temp_dict={}
      oid_value="IF-MIB::ifDescr.{}".format(i.oid_index)
      oid_adminstatus="IF-MIB::ifAdminStatus.{}".format(i.oid_index)
      oid_operstatus="IF-MIB::ifOperStatus.{}".format(i.oid_index)
      stat_adminstatus=snmp_get(oid_adminstatus, hostname=hostname, community=community, version=version)
      stat_operstatus=snmp_get(oid_operstatus, hostname=hostname, community=community, version=version)
      temp_dict["interface"]=i.value
      temp_dict["AdminStatus"]=stat_adminstatus.value
      if stat_operstatus.value == "1":
        status="Up"
      if stat_operstatus.value == "2":
        status="Down"
      temp_dict["OpernationStatus"]="{} {}".format(status,stat_operstatus.value)
      final_list.append(temp_dict)
    return json.dumps(final_list, indent=3)
  except EasySNMPTimeoutError as e:
    return json.dumps(e.message)
  except EasySNMPUnknownObjectIDError as e:
    return json.dumps(e.message)
  except EasySNMPNoSuchObjectError as e:
    return json.dumps(e.message)

def cpu_status(oid, hostname, community="public", version=2):
  try:
    data=snmp_get(oid, hostname=hostname, community=community, version=version)
    if data.value == "NOSUCHINSTANCE":
      return "Invalid OID provided."
    else:
      return json.dumps("The overall CPU busy percentage is {}".format(data.value))
  except EasySNMPTimeoutError as e:
    return json.dumps(e.message)
  except EasySNMPUnknownObjectIDError as e:
    return json.dumps(e.message)
  except EasySNMPNoSuchObjectError as e:
    return json.dumps(e.message)
	
	
def interface_speed(hostname, community="public", version=2):
  try:
    interfaces=snmp_walk('IF-MIB::ifDescr', hostname=hostname, community=community, version=version)
    data=snmp_walk('IF-MIB::ifDescr', hostname=hostname, community=community, version=version)
    index_list = []
    final_list = []
    for i in data:
      temp_dict={}
      oid_value="IF-MIB::ifDescr.{}".format(i.oid_index)
      oid_speed="IF-MIB::ifHighSpeed.{}".format(i.oid_index)
      supported_speed=snmp_get(oid_speed, hostname=hostname, community=community, version=version)
      actual_speed=int(supported_speed.value)/8
      temp_dict["interface"]=i.value
      temp_dict["Speed"]="Speed: {}bytes/sec".format(actual_speed)
      final_list.append(temp_dict)
    return json.dumps(final_list, indent=3)
  except EasySNMPTimeoutError as e:
    return json.dumps(e.message)
  except EasySNMPUnknownObjectIDError as e:
    return json.dumps(e.message)
  except EasySNMPNoSuchObjectError as e:
    return json.dumps(e.message)
	
	
	
def int_bandwidth_usage(hostname, interface_name=None, poll_interval=10, interface_oid=None, community="public", version=2):
  '''
    This will calculate the IN/OUT bandwidth usage for interface.
	snmp components used:- IfInOctets,IfOutOctets,IfSpeed,poll_interval
	Statndard Cisco Formula used . Below are the websites for reference
	https://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/8141-calculate-bandwidth-snmp.html
	https://support.solarwinds.com/Success_Center/Network_Performance_Monitor_(NPM)/Calculate_interface_bandwidth_utilization
  '''
    if interface_name != None and interface_oid == None:
	   try:
              data_one=snmp_walk('IF-MIB::ifDescr', hostname=hostname, community=community, version=version)
	   except EasySNMPTimeoutError as e:
	      return json.dumps(e.message)
    elif interface_oid != None and interface_name == None:
	   try:
              data_one=snmp_walk('ifName', hostname=hostname, community=community, version=version)
           except EasySNMPTimeoutError as e:
	      return json.dumps(e.message)
	output = []
    for i in data_one:
      temp_dict={}
      temp_dict["interface-name"]=i.value
      temp_dict["OID"]=i.oid_index
      output.append(temp_dict)
    if [d["OID"] for d in output if d["interface-name"] == interface_name]:
        oid=[d["OID"] for d in output if d["interface-name"] == interface_name][0]
    else:
	return json.dumps("No valid Interface or OID found.")
    #for i in data_two:
    #  if i.value == interface_name:
    #     oid=i.oid_index
    start_time=datetime.datetime.now()
    query_oid="ifInOctets.{}".format(oid)
    walk1=snmp_get(query_oid, hostname=hostname, community=community, version=version)
    start_time=datetime.datetime.now()
    wait_time=time.sleep(10)
    walk2=snmp_get(query_oid, hostname=hostname, community=community, version=version)
    end_time=datetime.datetime.now()
    diff_time=end_time-start_time
    elapsed_time=diff_time.seconds
    data_walk1=walk1.value
    data_walk2=walk2.value
	# This is roll counter reset
    if int(data_walk2) < int(data_walk1):
      date_walk2 += 4294967296
    speed_oid="ifSpeed.{}".format(oid)
    ifspeed=snmp_get(speed_oid, hostname=hostname, community=community, version=version)
    walk_diff=int(data_walk2)-int(data_walk1)
    IN_usage=(int(walk_diff)*8*100.00)/(int(elapsed_time)*int(ifspeed.value))*100
    start_time=datetime.datetime.now()
    query_oid="ifOutOctets.{}".format(oid)
    outwalk1=snmp_get(query_oid, hostname=hostname, community=community, version=version)
    wait_time=time.sleep(10)
    outwalk2=snmp_get(query_oid, hostname=hostname, community=community, version=version)
    end_time=datetime.datetime.now()
    diff_time=end_time-start_time
    elapsed_time=diff_time.seconds
    data_walk1=outwalk1.value
    data_walk2=outwalk2.value
    if int(data_walk2) < int(data_walk1):
      date_walk2 += 4294967296
    walk_diff=int(data_walk2)-int(data_walk1)
    OUT_usage=(int(walk_diff)*8*100.00)/(int(elapsed_time)*int(ifspeed.value))*100
    return "Poll Interval: {}secs \nBandwidth Inusage={}% \nBandwidth Outusage={}%".format(poll_interval,"%.2f" %IN_usage, "%.2f" %OUT_usage)
