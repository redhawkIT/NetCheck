#
#           Net Check | Python 3
#               by Ryan Keller
#
#   A proactive monitoring system made in order to view store uptime with the
#   intention of delivering IT and vendor services to stores experiencing outages.
#
################################################################################
#
#   Functions:
#       1) Net Check
#           Manually check the status of a store and detect outages.
#       2) Range Monitor
#           Checks stores within specific ranges; scan an entire enterprise
#       3) List Monitor
#           Collect a .csv list of store data and scan for outages
#
#   Data File Format: .csv (basic excell/spreadsheet)
#       Store               Country         Register Count
#       Integer, 5 long     US or CA        Integer, no limit
#
#   Example data set:
#       10304               US              2
#       267                 CA              6   
#
################################################################################
#                                      Operation Modes
################################################################################

### Software mode
DEBUG = False       #Will print pings and processes to terminal
EXTERNAL = True     #Pings placeholder addresses with 66% good responses
EXTERNAL_ADDRESSES = ['8.8.8.8', '8.8.4.4', 'BAD ADDRESS']


### Ping Configuration
TIMEOUT = '500'     #Miliseconds
PACKET_NUMBER = '1' #Attempts to reach a device
PACKET_SIZE = '2'   #Size of packets, Windows default is 32



################################################################################
#                                      Import Segment
################################################################################

import os
import subprocess
if EXTERNAL == True:
    import random   #For randomly generated IP octets

    

################################################################################
#                                      Main Function
################################################################################

def main():
    programIntro()
    while True:
        print ('='*80)
        print ('\t1) Net Check')
        print ('\t2) Range Monitor')
        print ('\t3) List Monitor')
        print ('\t4) Quit')
        print ('='*80)
        
        routine = intInput()
        if routine == 1:
            netCheck()
        elif routine == 2:
            rangeMonitor()
        elif routine == 3:
            listMonitor()
        elif routine == 4:
            exit()
    
    
    
################################################################################
#                                      Primary Functions
################################################################################

def programIntro():
    print ('=' * 80)
    print ('\t\tEnvoy Scanner')
    print ('\t\t\tby Ryan Keller')
    print ('-' * 80)
    print ('A proactive monitoring system for retail environments')
    print ('This detects "Hardware Hard Down" stores - where the network is OK')
    print ('...but all registers have crashed and thus cannot ring customers.')
    if DEBUG == True:
        print ('-' * 80)
        print ('Debug Mode Pre-testing:')
        if EXTERNAL == True:
            print ('Testing Network - Pinging random IP addresses x3')
            print ('\tResponse: ' + str(ping('')))
            print ('\tResponse: ' + str(ping('')))
            print ('\tResponse: ' + str(ping('')))
        else:
            print ('Testing Network - Pinging Google DNS Server at 8.8.8.8')
            print ('\tResponse: ' + str(ping('8.8.8.8')))
        print ('-' * 80)
    
    
#######################################
#   Net Check
#######################################

#Pings a single individual store
def netCheck():
    print ('='*80)
    print ('\tNet Check \t-\tStore "0" to exit')
    print ('='*80)
    
    while True:
        store = intInput()
        if store == 0: #Exit sentinel
            print ('='*80)
            print ('Returning to menu')
            break
        else:
            s = Store(store)
            print ('-'*80)
            s.report()
        
    return

    
#######################################
#   Range Monitor
#######################################

#Pings a range of store numbers
def rangeMonitor():
    print ('='*80)
    print ('\tRange Monitor\t-\tSpecify "0" to exit')
        
    while True:
        print ('='*80)
        print ('Lower Range:')
        low = intInput()
        print ('Upper Range:')
        up = intInput() + 1
        print ('='*80)
        
        if low == 0 or up == 0: #Exit sentinel
            print ('Returning to menu')
            break
        elif low >= up:
            print ('Error: upper range not greater than low range')
        else:
            s = 0
            print ('-'*80)
            for i in range(low, up):
                s = Store(i)
                s.report()
            print ('='*80)
            print ('Range Monitor complete, returning to menu')
            break
        
    return
    
    
#######################################
#   List Monitor
#######################################

#Parses a .csv file and pings each store in it
def listMonitor():
    print ('='*80)
    print ('\tFile Monitor \t-\tSpecify file "0" or "0.csv" to exit')
    print ('='*80)
    
    print ('File must be in the local directory and formatted as .csv')
    while True:
        file = fileName()
        try:
            if file == '0.csv':
                print ('='*80)
                print ('Returning to menu')
                break

            if '\\' not in file:
                path = os.path.dirname(os.path.abspath(__file__))
                file = (path + '\\' + file)
            
            readFile = open(file, 'r')
            print ('='*80)
            print ('File:', file)
            print ('='*80)
            
            line = readFile.readline()
            s = ''
            print ('-'*80)
            while line != '':
                line = line.rstrip('\n').replace(' ','').split(',')
                s = Store(line[0], line[1], line[2])
                s.report()
                line = readFile.readline()
            print ('='*80)
            readFile.close()

        except Exception as e:
            print ('An unexpected error occured while reading/writing files')
            print ('\t' + e)
            
    return
    

    
################################################################################
#                                      Tertiary Functions
################################################################################

#######################################
#   Pinging
#######################################

#Uses OS/system to ping, parses output to find online status
def ping(address):
    if EXTERNAL == True: # Ping google servers instead, 66% success
        address = random.choice(EXTERNAL_ADDRESSES)
    command =   ['ping', address,
                '-n', PACKET_NUMBER,
                '-w', TIMEOUT,
                '-l', PACKET_SIZE]

    try:
        status = subprocess.check_output(command,
        stderr=subprocess.STDOUT,   # Gathers standard out from system process
        universal_newlines=True)    # Returns string type, not bytes

        if DEBUG == True:
            print (status)
        
        #   Using StdOut would be acceptable, except it is not accurate -
        #   A "reachable" or 0 response just indicates a reply was received
        #   Thus "Reply... Destination Unreachable" would report as an online device
        if ('Reply' in status) and ('unreachable' not in status):
            #So we'll search StdOut as a string to ensure accurate reporting
            onlineStatus = True
        else:
            onlineStatus = False
    except:
        onlineStatus = False
        
    return onlineStatus

    
#######################################
#   Classes and Record Management
#######################################    

class Store(object):
    #"ping usrg01021304" Will ping US store 21304, Register 1
    #Data format:
    #    Store    Country    Register Count
    #    00000    US         2
    
    def __init__(self, store, country='us', rgCount=2):
        store = str(store)
        self.store = store.rjust(5, '0')
        self.country = str(country)
        self.rgCount = int(rgCount)
        self.crashedRegisters = 0
        
        # Checking gateway and back office PC
        self.dg = ping('dg' + self.store)
        self.mws = ping('mws' + self.store)
        
        # Checking all registers, accumulating count of crashed RG's
        self.register = {}
        for i in range(1, self.rgCount + 1):
            status = ping(self.country + 'rg0' + str(i) + '0' + self.store)
            if status == False:
                self.crashedRegisters += 1
            self.register[i] = status
        
        #Checking for hard down status
        self.status = False
        if self.dg == True:
            if self.crashedRegisters == self.rgCount:
                self.status = True #HARD DOWN

        
    def report(self):
        #Prints a visually palatable report of endpoint status
        print ('STORE\t|\t' + str(self.store))
        print ('* DG:\t|\t' + str(self.dg))
        for i in range(1, self.rgCount + 1):
            print ('* RG' + str(i) + ':\t|\t' + str(self.register[i]))
        print ('* MWS:\t|\t' + str(self.mws))
        print ('H.Down\t|\t' + str(self.status))
        print ('-'*80)

 
#######################################
#   Input Validation
#######################################

#Loops until an acceptable integer is input    
def intInput():
    while True:
        try:
            inputInteger = int(input(' > '))
            if inputInteger >= 0:
                break
            else:
                print ('Integer must be non-negative, retry:')
        except ValueError:
            print ('Improper selection, retry:')
    return inputInteger

    
#Loops until a valid .csv file can be specified in a string    
def fileName():

    while True:
        try:
            name = str(input(' File > '))
            if (name[-4:] != '.csv'):
                #Formats the file with the correct extension
                name = (name + '.csv')
                break
            elif (name[-4:] == '.csv'):
                break
        except:
            print ('An error occured - enter a different name:')
    return name    

    
    
################################################################################
#                                      Function Calls
################################################################################

main()



################################################################################
#                                      End Comments
################################################################################
#
#   This program was created as a personal project and, with permission, used
#   by a company I have contracted with. It contains no proprietary data and
#   is not covered by any non-disclosure agreements.
#