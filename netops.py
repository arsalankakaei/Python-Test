#First >>>>> pip install netmiko
#Second >>>> pip install colorama

import netmiko
from netmiko import ConnectHandler
from getpass import getpass
from colorama import Fore, Back, Style


ip_addresses=['192.168.11.11']

iosv_l2 = {
    'device_type': 'cisco_ios',
    'ip':   '',
    'username': '',
    'password': '',
    'secret': '',
}

max_port=25

# get and set username and password from user
print("Please enter your user name:")
username = input('username:')
print("Please insert your password:")
password = getpass()
iosv_l2['username']=username
iosv_l2['password']=password
iosv_l2['secret']=password


for ipadd in ip_addresses:
    iosv_l2['ip']=ipadd
    print("Checking switch >>> "+ iosv_l2['ip'])
    net_connect =ConnectHandler(**iosv_l2)
    net_connect.enable()
    
    
    l_for_security =[] # a temp list for extracting Total MAC Adresses
    ports=range(1,max_port)

    for p in ports : # Check all ports whitch are in ip_addresses from G0/1 to G0/(max_port-1)
        output =net_connect.send_command('show port-security interface G0/'+str(p))
        if("Enabled" in output): # Check if port-security is enable then decide to disable ports which are enable but have no MAC address
            l_for_security=output.splitlines(False)
            tmp=(l_for_security[7])
            l2=tmp.split(":")
            tmp2=l2[1]
            if(int(tmp2))<1: # if TOTAL MAC addresses is lower than 1
                output =net_connect.send_command('show interface G0/'+str(p)+" status")
                #print(output)
                if("disabled" in output): # if the port is disabled
                    #port-security is enable, port is disabled.
                    continue
                else:
                    if("trunk" in output):
                        #port-security is enable, port is trunk. 
                        continue
                    else:
                        # port-security is enable, port is enable but no MAC address sticked to this port.
                        # Disable this port
                        print(Fore.BLUE+"****************** Disable this port number : G0/"+str(p)+ " *******************"+Fore.WHITE)
                        disable_port_command = ["interface G0/"+str(p),"shutdown"]
                        net_connect.send_config_set(disable_port_command)
                        output =net_connect.send_command('show interface G0/'+str(p)+" status")
                        if ("disabled" in output):
                            print(Back.YELLOW+"     This port is disabled successfuly!"+Back.BLACK)
                        else:
                            print(Back.RED+"        <<<<<<Error on disabling>>>>>>>"+Back.BLACK)    

        else: # Check if port-security is disabled then advice to enable port-security for this port
            output =net_connect.send_command('show interface G0/'+str(p)+" status")
            if("disabled" in output):
                #port-security is disabled, port is disabled.
                continue
            else:
                if("trunk" in output):
                    #port-security is disabled, port is trunk.
                    continue
                else:
                    #port-security is disabled, port is enable.
                    print(Fore.RED+"****************** Enable Port Secutity : G0/"+str(p)+ " *******************"+Fore.WHITE)
   
