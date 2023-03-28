#!/usr/bin/env python3
"""
#  Info on Rohde&Schwarz PowerSupply HMP4040                                                                                        #
#  Manual https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_manuals/user_manual/1178_6833_01/HMPSeries_UserManual_en_03.pdf #
#  Manual VISA https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/dl_application/application_notes/1sl374/1SL374_0e.pdf             #
#  TCPIP 192.168.168.246                                                                                                            #
#  IP Port 5025                                                                                                                     #
#  HTTP Port 80                                                                                                                     #
"""

import time, socket

class HMP4040(object):

    def __init__(self,IP,PORT):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((IP, PORT))
        self.socket.sendall('*IDN?\n'.encode())
        print(f"PowerSupply {self.socket.recv(4096)}")

    def setChVoltCurr(self,Channel,V,I):
        self.socket.sendall(f'INST {Channel} \n'.encode())
        self.socket.sendall(f'APPL {V},{I} \n'.encode())

    def turnChOn(self,Channel):
        self.socket.sendall(f'INST {Channel} \n'.encode())
        self.socket.sendall('OUTP:STAT 1 \n'.encode())

    def turnChOff(self,Channel):
        self.socket.sendall(f'INST {Channel} \n'.encode())
        self.socket.sendall('OUTP:STAT 0 \n'.encode())



if __name__ == "__main__":


    def checkStatus(outfile,checkString):
        ready=False
        f = open(outfile, "r")
        lines = f.readlines()
        for line in lines:
            if checkString in line:
                ready=True
                break
        f.close()
        return ready

    def getNEntry(outfile):
        NEntry=""
        f = open(outfile, "r")
        lines = f.readlines()
        NEntry=lines[-1]
        f.close()
        return NEntry

    import subprocess,sys
    import logging
    logging.basicConfig(level=logging.DEBUG)
    import time

    powSup =  HMP4040('192.168.168.246', 5025)
    powSup.setChVoltCurr("OUT2",1.25,3)
    powSup.turnChOn("OUT2")

    subprocess.Popen("mkdir -p Data", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    cmdMOSAIC250="/home/vfat3/vfat3_testing_ll/VFAT3 -cfg /home/vfat3/vfat3_testing_ll/cfg/tb_gem_250.cfg -set_default_chip 0 -chip_init -DAQ 2>&1 > Data/.outputMOSAIC250.log &"
    spMOSAIC250 = subprocess.Popen(cmdMOSAIC250, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    #out250, err250 = spMOSAIC250.communicate()

    cmdMOSAIC251="/home/vfat3/vfat3_testing_ll/VFAT3 -cfg /home/vfat3/vfat3_testing_ll/cfg/tb_gem_251.cfg -set_default_chip 0 -chip_init -DAQ 2>&1 > Data/.outputMOSAIC251.log &"
    spMOSAIC251 = subprocess.Popen(cmdMOSAIC251, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    #out251, err251 = spMOSAIC251.communicate()

    time.sleep(5)
    err=0
    while not checkStatus("Data/.outputMOSAIC250.log","Sync OK") or not checkStatus("Data/.outputMOSAIC251.log","Sync OK"):
        logging.warning("MOSAIC boards not yet ready")
        time.sleep(1)
        err+=1
        if err>20:
            logging.error("Not able to configure check Data/.outputMOSAIC250.log and Data/.outputMOSAIC251.log ")
            break
    logging.info("VFAT Sync OK")
    if checkStatus("Data/.outputMOSAIC250.log","Standard DAQ run") and checkStatus("Data/.outputMOSAIC251.log","Standard DAQ run"):
        logging.info(">>> ENABLE TRIGGER <<<")
        logging.info(">>> To check the triggered events press Return <<<")
        logging.info(">>> To stop the run write Stop <<<")
        checkIn=input()
        while not checkIn=="Stop":
            logging.info("MOSAIC250: "+getNEntry("Data/.outputMOSAIC250.log")+" MOSAIC251: "+getNEntry("Data/.outputMOSAIC251.log"))
            checkIn=input()

    cmdKillAllVFAT="killall -w VFAT3"

    powSup.turnChOff("OUT2")
