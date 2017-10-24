#!/bin/bash
#VERSION:- 1.1
# Please don't touch this script
#phase:- Under Testing
#Purpose:- To automate installation of salt master on customer`s environment according to CRI.
#==================
#AUTHOR:- Suman Deb 
#=================

# DONT RUN THE SCRIPT ON A WORKING ALREADY RUNNING SALT MASTER.
# THIS SCRIPT WILL OVERWRIDE THE EXISTING VALUES. SO RUN AT YOUR OWN RISK

LOGFILE=/var/log/salt_install.log

# Getting the varaibles from param.conf file located inside the project directory

. ./params.conf
#git_host=gitlab-server
#git_hostip="10.236.194.207"
#cloud_pillar_url="http://10.236.220.135:8080/provisioning/services/provisioningservice/clouddata/listAll"
#cmdb_url="http://10.236.220.130:5056/api/v1/viewentities"
#key_path="/srv/salt/files/keys"
#pmp_host="10.236.220.206"
#pmp_hostname="sit-gwcon.cloud360.com"
#pmp_port="443"
#pmp_token="BAC402E0-F5D4-43D5-93ED-76D763600C7A"
#pmp_account="aws"
#pmp_resource="Provider"
#pmp_scheme="https"
#gitfs_remotes="git@gitlab-server:root/code.git"

#check_os_info ()
#{
if [ -f /etc/debian_version ];then
  OS="Debian"
  VER=$(cat /etc/debian_version)
  REL=$(lsb_release -a | grep Release | awk -F " " '{print $2}')
  echo "This OS comes under $OS family"
  echo "The version is ${VER}"
  echo "The OS release is ${REL}"
elif [ -f /etc/redhat-release ];then
  OS="RedHat"
  VER=$(cat /etc/redhat-release)
#  REL=$(cat /etc/*release | cut -d" " -f3 | cut -d "." -f1)
  REL=$(lsb_release -rs | cut -f1 -d .)
  if [ -z "$REL" ];then
  REL=$(rpm -qa \*-release | grep -Ei "oracle|redhat|centos" | cut -d"-" -f3)
  fi
  echo "This OS comes under $OS family"
  echo "The version is ${VER}"
  echo "The OS release is ${REL}"
else
  echo "This OS is not suppored by this script"
fi
#}




check_internet_access ()
{
echo "Checking Internet Connectivity."
if rpm -qa | grep wget;then
wget -q --spider http://google.com
 if [ $? -eq 0 ]; then
    echo "Online"
 else
    echo "Offline"
    echo "Sorry!! Internet connection is required in order to access Salt Offcial repo"
    echo "Script Terminated"
    exit 1
 fi
else
echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "Online"
  else
    echo "Offline"
    echo "Sorry!! Internet connection is required in order to access Salt Offcial repo"
    echo "Script Terminated"
    exit 1
 fi
fi
}




#Configuring Salt Official Repo
configure_salt_repo ()
{
echo "Configuring Salt Official Repo."
if [ "$OS" = "Debian" ];then
  case $REL in
	14.04)
                echo "This is $OS and 14.04"	
		wget -O - https://repo.saltstack.com/apt/ubuntu/16.04/amd64/latest/SALTSTACK-GPG-KEY.pub | sudo apt-key add - >> $LOGFILE 2>&1
		touch /etc/apt/sources.list.d/saltstack.list
		echo "deb http://repo.saltstack.com/apt/ubuntu/16.04/amd64/latest xenial main" >> /etc/apt/sources.list.d/saltstack.list         
		if [ $? -eq 0 ]; then
    		echo "Success."
 		else
    		echo "Failed!."
		fi;;
	16.04)
	        echo "This is $OS and 16.04"
		wget -O - https://repo.saltstack.com/apt/ubuntu/14.04/amd64/latest/SALTSTACK-GPG-KEY.pub | sudo apt-key add - >> $LOGFILE 2>&1
		touch /etc/apt/sources.list.d/saltstack.list
                echo "deb http://repo.saltstack.com/apt/ubuntu/14.04/amd64/latest trusty main" >> /etc/apt/sources.list.d/saltstack.list
		if [ $? -eq 0 ]; then
                echo "Success."
                else
                echo "Failed!."
                fi;;
	12.04)
	        echo "This is $OS and 12.04"
		echo "Warning!! This has reached EOL."
		wget -O - https://repo.saltstack.com/apt/ubuntu/12.04/amd64/latest/SALTSTACK-GPG-KEY.pub | sudo apt-key add -
		touch /etc/apt/sources.list.d/saltstack.list
		echo "deb http://repo.saltstack.com/apt/ubuntu/12.04/amd64/latest precise main" >> /etc/apt/sources.list.d/saltstack.list
		if [ $? -eq 0 ]; then
                echo "Success."
                else
                echo "Failed!"
		fi;;
	    *)
		echo "Version Not supported"
		exit
		;;
   esac
else
  case $REL in 
	7)
		echo "This is $SO 7 and installing latest repo release of saltstack"
                echo "Removing python-pycryptodomex and installing python-crypto"
		rpm -e --nodeps python2-pycryptodomex >> $LOGFILE 2>&1
		yum install python-crypto -y >> $LOGFILE 2>&1
                yum install https://repo.saltstack.com/yum/redhat/salt-repo-latest-2.el7.noarch.rpm -y >> $LOGFILE 2>&1
		yum clean expire-cache >> $LOGFILE 2>&1
                if [ $? -eq 0 ]; then
                echo "Success."
                else
                echo "Failed!"
		fi;;
	6)	
		echo "This is $SO 6 and installing latest repo release of saltstack"
		echo "Removing python-pycryptodomex and installing python-crypto"
		rpm -e --nodeps python2-pycryptodomex >> $LOGFILE 2>&1
		yum install python-crypto -y >> $LOGFILE 2>&1
		yum install https://repo.saltstack.com/yum/redhat/salt-repo-latest-2.el6.noarch.rpm -y >> $LOGFILE 2>&1
                if [ $? -eq 0 ]; then
                echo "Success."
                else
                echo "Failed!"
		yum clean expire-cache >> $LOGFILE 2>&1
		fi;;
	5)	echo "Warning!! This has reached EOL."
		echo "Removing python-pycryptodomex and installing python-crypto"
		rpm -e --nodeps python2-pycryptodomex
		yum install python-crypto -y
		echo "This is $SO 5 and installing latest repo release of saltstack"	
		wget https://repo.saltstack.com/yum/redhat/salt-repo-latest-1.el5.noarch.rpm -u
		rpm -ivh salt-repo-latest-1.el5.noarch.rpm
		;;
	*)
		echo "Version Not supported"
		exit
		;;
  esac
fi
}


configure_salt_versionbased_repo ()
{
echo "Configuring Salt Official Repo."
if [ "$OS" = "Debian" ];then
  case $REL in
        14.04)
                echo "This is $OS and 14.04"
                wget -O - https://repo.saltstack.com/apt/ubuntu/16.04/amd64/archive/$salt_version/SALTSTACK-GPG-KEY.pub | sudo apt-key add - >> $LOGFILE 2>&1
                touch /etc/apt/sources.list.d/saltstack.list
                echo "deb http://repo.saltstack.com/apt/ubuntu/16.04/amd64/archive/$salt_version xenial main" >> /etc/apt/sources.list.d/saltstack.list
                if [ $? -eq 0 ]; then
                echo "Success."
                else
                echo "Failed!."
                fi;;
        16.04)
                echo "This is $OS and 16.04"
                wget -O - https://repo.saltstack.com/apt/ubuntu/14.04/amd64/archive/$salt_version/SALTSTACK-GPG-KEY.pub | sudo apt-key add - >> $LOGFILE 2>&1
                touch /etc/apt/sources.list.d/saltstack.list
                echo "deb http://repo.saltstack.com/apt/ubuntu/14.04/amd64/archive/$salt_version trusty main" >> /etc/apt/sources.list.d/saltstack.list
                if [ $? -eq 0 ]; then
                echo "Success."
                else
                echo "Failed!."
                fi;;
        12.04)
                echo "This is $OS and 12.04"
                echo "Warning!! This has reached EOL."
                wget -O - https://repo.saltstack.com/apt/ubuntu/12.04/amd64/archive/$salt_version/SALTSTACK-GPG-KEY.pub | sudo apt-key add -
                touch /etc/apt/sources.list.d/saltstack.list
                echo "deb http://repo.saltstack.com/apt/ubuntu/12.04/amd64/archive/$salt_version precise main" >> /etc/apt/sources.list.d/saltstack.list
                if [ $? -eq 0 ]; then
                echo "Success."
                else
                echo "Failed!"
                fi;;
            *)
                echo "Version Not supported"
                exit
                ;;
   esac
else
  case $REL in
        7)
                echo "This is $SO 7 and installing archive repo release of saltstack"
                echo "Removing python-pycryptodomex and installing python-crypto"
                rpm -e --nodeps python2-pycryptodomex >> $LOGFILE 2>&1
		yum install python-crypto -y
                rpm --import https://repo.saltstack.com/yum/redhat/7/x86_64/archive/$salt_version/SALTSTACK-GPG-KEY.pub >> $LOGFILE 2>&1
	        touch  /etc/yum.repos.d/saltstack.repo
		echo "[saltstack-repo]" >> /etc/yum.repos.d/saltstack.repo	
		echo "name=SaltStack repo for RHEL/CentOS \$releasever" >> /etc/yum.repos.d/saltstack.repo
		echo "baseurl=https://repo.saltstack.com/yum/redhat/\$releasever/\$basearch/archive/$salt_version" >> /etc/yum.repos.d/saltstack.repo
		echo "enabled=1" >> /etc/yum.repos.d/saltstack.repo
		echo "gpgcheck=1" >> /etc/yum.repos.d/saltstack.repo
		echo "gpgkey=https://repo.saltstack.com/yum/redhat/\$releasever/\$basearch/archive/$salt_version/SALTSTACK-GPG-KEY.pub" >> /etc/yum.repos.d/saltstack.repo
                yum clean expire-cache >> $LOGFILE 2>&1
                if [ $? -eq 0 ]; then
                echo "Success."
                else
                echo "Failed!"
                fi;;
        6)
                echo "This is $SO 6 and installing archive repo release of saltstack"
                echo "Removing python-pycryptodomex and installing python-crypto"
                rpm -e --nodeps python2-pycryptodomex >> $LOGFILE 2>&1
                yum install python-crypto -y >> $LOGFILE 2>&1
                rpm --import https://repo.saltstack.com/yum/redhat/6/x86_64/archive/$salt_version/SALTSTACK-GPG-KEY.pub >> $LOGFILE 2>&1
		touch  /etc/yum.repos.d/saltstack.repo
                echo "[saltstack-repo]" >> /etc/yum.repos.d/saltstack.repo
                echo "name=SaltStack repo for RHEL/CentOS \$releasever" >> /etc/yum.repos.d/saltstack.repo
                echo "baseurl=https://repo.saltstack.com/yum/redhat/\$releasever/\$basearch/archive/$salt_version" >> /etc/yum.repos.d/saltstack.repo
                echo "enabled=1" >> /etc/yum.repos.d/saltstack.repo
                echo "gpgcheck=1" >> /etc/yum.repos.d/saltstack.repo
                echo "gpgkey=https://repo.saltstack.com/yum/redhat/\$releasever/\$basearch/archive/$salt_version/SALTSTACK-GPG-KEY.pub" >> /etc/yum.repos.d/saltstack.repo
                if [ $? -eq 0 ]; then
                echo "Success."
                else
                echo "Failed!"
                yum clean expire-cache >> $LOGFILE 2>&1
                fi;;
        5)      echo "Warning!! This has reached EOL."
              	
                echo "This is $SO 5 and installing archive repo release of saltstack"
                wget https://repo.saltstack.com/yum/redhat/5/x86_64/archive/2016.11.3/SALTSTACK-EL5-GPG-KEY.pub
 		rpm -ivh rpm --import SALTSTACK-EL5-GPG-KEY.pub 
		touch  /etc/yum.repos.d/saltstack.repo
		echo "[saltstack-repo]" >> /etc/yum.repos.d/saltstack.repo
		echo "name=SaltStack repo for RHEL/CentOS \$releasever" >> /etc/yum.repos.d/saltstack.repo
		echo "baseurl=https://repo.saltstack.com/yum/redhat/\$releasever/\$basearch/archive/2016.11.3" >> /etc/yum.repos.d/saltstack.repo
		echo "enabled=1" >> /etc/yum.repos.d/saltstack.repo
		echo "gpgcheck=1" >> /etc/yum.repos.d/saltstack.repo
		echo "gpgkey=https://repo.saltstack.com/yum/redhat/\$releasever/\$basearch/archive/2016.11.3/SALTSTACK-EL5-GPG-KEY.pub" >> /etc/yum.repos.d/saltstack.repo
                ;;
        *)
                echo "Version Not supported"
                exit
                ;;
  esac
fi
}





install_salt ()
{
if [ "$OS" = "Debian" ];then
	apt-get update -y >> $LOGFILE 2>&1
	apt-get install salt-master salt-minion salt-api salt-ssh salt-cloud -y >> $LOGFILE 2>&1
        if [ $? -eq 0 ];then
        echo "Salt installation completed succesfully"
	else
	echo "Failed!!.Some thing wrong with the installtion"
	fi
else
	yum install salt-master salt-minion salt-api salt-ssh salt-cloud -y >> $LOGFILE 2>&1
	if [ $? -eq 0 ];then
        echo "Salt installation completed succesfully"
        else
        echo "Failed!!.Some thing wrong with the installtion"
        fi
fi

}

start_salt_master ()
{
service salt-master start
if [ $? -eq 0 ]; then
    echo "Success."
 else
    echo "Failed!."
fi
}

stop_salt_master ()
{
service salt-master stop
if [ $? -eq 0 ]; then
    echo "Success."
 else
    echo "Failed!."
fi
}

start_salt_minion ()
{
service salt-minion start
if [ $? -eq 0 ]; then
    echo "Success."
 else
    echo "Failed!."
fi
}

stop_salt_minion ()
{
service salt-minion stop
if [ $? -eq 0 ]; then
    echo "Success."
 else
    echo "Failed!."
fi
}

start_salt_api ()
{
service salt-api start
}

stop_salt_api ()
{
service salt-api stop
}


configure_git_salt ()
{
cat << EOT >> /etc/salt/master.d/integration.conf
fileserver_backend:
  - git
  - roots
file_roots:
  base:
    - /srv/salt
pillar_roots:
  base:
    - /srv/pillar
gitfs_remotes:
  - ${gitfs_remotes}
EOT
if [ $? -eq 0 ]; then
    echo "Success."
 else
    echo "Failed!."
fi
}



install_gitpython_redhat ()
{
if [ "$OS" = "RedHat" ];then
  if ! rpm -qa | grep GitPython;then
	yum install GitPython -y >> $LOGFILE 2>&1
        configure_git_salt
  else
      configure_git_salt
  fi
elif [ "$OS" = "Debian" ];then
  if ! dpkg -l python-git;then
        apt-get install python-git -y >> $LOGFILE 2>&1
        configure_git_salt
  else
      configure_git_salt
  fi
else
 echo "$OS Is A Not Supported version"
fi
}


setup_git_fileserver ()
{
if [ ! -z "$git_host" ] && [ ! -z "$git_hostip" ];then
echo "$git_hostip $git_host" >> /etc/hosts
install_gitpython_redhat
fi
}

setup_PMP ()
{
if  [ ! -z "$pmp_host" ] &&  [ ! -z "$pmp_token" ];then
if [ ! -z "$pmp_account" ] &&  [ ! -z "$pmp_resource" ];then
cat << EOT >> /etc/salt/master.d/integration.conf
vault:  
  driver: pmp  
  pmp.host: ${pmp_host}  
  pmp.port: ${pmp_port}  
  pmp.resource: ${pmp_resource}  
  pmp.scheme: ${pmp_scheme}  
  pmp.token: ${pmp_token}
EOT
echo "$pmp_host $pmp_hostname" >> /etc/hosts
if [ $? -eq 0 ]; then
    echo "Success."
 else
    echo "Failed!."
fi
else
echo "Stopped!! Looks like you dont have all the PMP parameters to configure"
fi
fi
}

setup_cmdb_url_for_roster ()
{
if [ ! -z "$cmdb_url" ] && [ ! -z "$key_path" ];then
cat << EOT >> /etc/salt/master.d/integration.conf
config:
  cmdb_url: $cmdb_url
  key_path: $key_path
EOT
if [ $? -eq 0 ]; then
    echo "Success."
 else
    echo "Failed!."
fi
else
echo "One of the paramerters between cmdb_url and key_path is missing"
fi
}

setup_cloud_pillar ()
{
if [ ! -z "$cloud_pillar_url" ];then
cat << EOT >> /etc/salt/master.d/integration.conf
ext_pillar:
  - cloud_pillar:
      url: $cloud_pillar_url
EOT
if [ $? -eq 0 ]; then
    echo "Success."
 else
    echo "Failed!."
fi
else
echo "cloud_pillar_url parameter missing value"
fi
}

Installing_extra_packages ()
{
wget https://bootstrap.pypa.io/get-pip.py && \   
python get-pip.py && \    
pip install azure==2.0.0rc6 && \    
pip install pyvmomi  && \    
pip install pywinrm==0.1.1 && \    
pip install impacket && \    
pip install boto && \    
pip install botocore && \    
pip install boto3 >> $LOGFILE 2>&1
if [ $? -eq 0 ]; then
    echo "Success."
else
    echo "Failed!."
fi
}


copying_network_templates ()
{
mkdir -p  /srv/salt/Network
cp -r templates /srv/salt/Network
cp NAscript.sh /srv/salt/Network
}




copying_custom_cri_modules ()
{
echo "Copying custom modules to salt directories..."
dir=`find / -type d -name salt | grep /usr/lib/ | head -1`
#cp --preserve cricloudroster.py /usr/lib/python2.7/dist-packages/salt/roster/
cp --preserve cricloudroster.py $dir/roster/
#cp --preserve cloud_pillar.py /usr/lib/python2.7/dist-packages/salt/pillar/
cp --preserve cloud_pillar.py $dir/pillar/
#cp --preserve pmp.py /usr/lib/python2.7/dist-packages/salt/sdb/
cp --preserve pmp.py $dir/sdb/
#cp -r utils/sdbparse.py /usr/lib/python2.7/dist-packages/salt/utils/
cp -r utils/sdbparse.py $dir/utils/
#cp -r utils/pmp.py /usr/lib/python2.7/dist-packages/salt/utils/
cp -r utils/pmp.py $dir/utils/
#cp -r utils/pillar.py /usr/lib/python2.7/dist-packages/salt/utils/
cp -r utils/pillar.py $dir/utils/
cp network_pillar.py $dir/pillar/
cp router_parse.py $dir/utils/

if [ $? -eq 0 ]; then
    echo "Success."
 else
    echo "Failed!."
fi
}



usage ()
{
	echo "Usage: <scriptname> [-a <masterIP>] [d <minionID>] [Optional:- -i Ip] [Optiional:- -u username] [Optiional:- -v version]"
}

if [ $# -eq 0 ];then
echo "Please provide required arguments to the script"
usage
echo "Required parameters:- "
echo "-a: Ipadress of the salt master server"
echo "-d: Salt minion Id. Recommended as master. id: master in master config file."
echo "Optional parameters:- "
echo "-i: The interface the salt master will bind or listen to. Generally its the same ip as salt master IP"
echo "-u: Run salt as a diffrent user other than root."
exit 1
elif [ $# -lt 4 ];then
usage
echo "Required parameters:- "
echo "-a: Ipadress of the salt master server"
echo "-d: Salt minion Id. Recommended as master. id: master in master config file."
echo "Optional parameters:- "
echo "-i: The interface the salt master will bind or listen to. Generally its the same ip as salt master IP"
echo "-u: Run salt as a diffrent user other than root."
exit 1
fi



while getopts a:d:i::u::v::h arg; do
	case $arg in 
		a)
		echo "Ready to set up Salt minion to register with salt master (Ipaddress ${OPTARG})"
		ipaddr=${OPTARG}
		;;
		d)
		echo "Will configure Salt minion ID to ${OPTARG}"
		minionid=${OPTARG}
		;;
		i)
		echo "Binding Salt to Ipaddrss ${OPTARG}"
		bindip=${OPTARG}
		;;
		u)
		echo "You have decided to run salt as ${OPTARG}! Where the default is Root."
		saltuser=${OPTARG}
		;;
                v)
	  	echo "The version of salt will be ${OPTARG}"
                salt_version=${OPTARG}
		;;
		h)
		echo "Example usage of the script:- "
	 	echo "./scriptname -a 10.10.x.x -d master"
		echo "./scriptname -a 10.10.x.x -d master -i 10.10.x.x -u crisuer"
                exit 0;;
		*)
		usage
		echo "Illegal Arguments";;
	esac
done

setting_up_saltuser ()
{
if [ ! -z "$saltuser" ];then
	if [ "$OS" = "Debian" ];then
        if ! id $saltuser;then
	echo "Creating user"
	useradd -m -d /home/$saltuser $saltuser 
	echo "Please enter a password"
	read password
	echo "$saltuser:$password" | chpasswd >> $LOGFILE 2>&1
	echo "$saltuser created with password as $password"
        else 
        echo "User already exist"
        fi
	else
        if ! id $saltuser;then
	echo "Creating user"
	useradd $saltuser
	echo "Please enter a password"
	read password
	echo "$password" | passwd --stdin $saltuser >> $LOGFILE 2>&1
	echo "$saltuser created with password as $password"
        else
        echo "User already exist"
        fi
	fi
sed -i "s/#user: root/user: $saltuser/g" /etc/salt/master
mkdir /home/$saltuser/.ssh/ >> $LOGFILE 2>&1
chown $saltuser:$saltuser  /home/$saltuser/.ssh/ >> $LOGFILE 2>&1
chmod 700 /home/$saltuser/.ssh/ >> $LOGFILE 2>&1
cp id_rsa_gitlab /home/$saltuser/.ssh/
cat << EOT > /home/$saltuser/.ssh/config
Host gitlab-server
IdentityFile /home/$saltuser/.ssh/id_rsa_gitlab
User git
StrictHostKeyChecking no
EOT
chmod 400 /home/$saltuser/.ssh/id_rsa_gitlab >> $LOGFILE 2>&1
chown $saltuser:$saltuser /home/$saltuser/.ssh/id_rsa_gitlab >> $LOGFILE 2>&1
chown -R $saltuser /etc/salt /srv /var/cache/salt /var/log/salt >> $LOGFILE 2>&1
else
cp id_rsa_gitlab /root/.ssh/
cat << EOT > /root/.ssh/config
Host gitlab-server
IdentityFile /root/.ssh/id_rsa_gitlab
User git
StrictHostKeyChecking no
EOT
chmod 400 /root/.ssh/id_rsa_gitlab
fi

}


echo "You are ready to install salt $salt_version"

echo "Checking Internet Access"
check_internet_access 

sleep 3
if [ -z "$salt_version" ];then
configure_salt_repo 
else
configure_salt_versionbased_repo
fi
sleep 2
echo "Installing Salt.Please Wait........"
install_salt
sleep 2
echo "Installing Extra packages."
Installing_extra_packages
echo "Changing Salt master Ip in minion file."
touch /etc/salt/master.d/integration.conf
touch /etc/salt/minion.d/integration.conf
if [ -f /etc/salt/minion ];then
sed -i "s/#master: salt/master: ${ipaddr}/g" /etc/salt/minion >> $LOGFILE 2>&1
else
echo "master: ${ipaddr}" >> /etc/salt/minion.d/integration.conf
fi
echo "Changing Salt minion ID."
if [ -f /etc/salt/minion ];then
echo "id: ${minionid}" >> /etc/salt/minion 
else
echo "id: ${minionid}" >> /etc/salt/minion.d/integration.conf
fi

echo "Changing Salt Bind Ip address."
echo "interface: ${ipaddr}" >> /etc/salt/master.d/integration.conf 

echo "Changing Log level in in salt Master"
sed -i "s/#log_level: warning/log_level: error/g" /etc/salt/master.d/integration.conf  >> $LOGFILE 2>&1
echo "Setting up Git File server."
setup_git_fileserver 
echo "Setting up PMP."
setup_PMP 
echo "Setting up CMDB API for salt-ssh roster module."
setup_cmdb_url_for_roster
echo "Setting up external cloud pillar."
setup_cloud_pillar 
echo "Setting up salt user."
copying_custom_cri_modules
copying_network_templates
setting_up_saltuser 
echo "=========================================================Starting Salt Master========================================================================"
start_salt_master 
echo "=========================================================Starting Salt Minion========================================================================"
start_salt_minion 
sleep 20
echo "=====================================================Accepting itself as salt minion================================================================="
salt-key -A $minionid -y | tee -a $LOGFILE
echo "=================================================Checking Connection Between Master And Minion======================================================="
sleep 10
salt $minionid test.ping | tee -a $LOGFILE
clear
sleep 5
echo "######################################################################################################################################################"
echo "========================================Salt server has been succesfully installed and Configured!!==================================================="
echo "######################################################################################################################################################"
echo "=====================================================Thank You For Your Time=========================================================================="
