import scapy.all as scapy

can_fields = None
sock = None

def get_fields(bus_type):    
    global can_fields
    if bus_type == "can":
        can_fields = [field.name for field in CAN().fields_desc]
        dataframe_fields = can_fields + ['datahex','dataascii']
        return dataframe_fields

def setup_can(interface):
    global sock
    try:
        print("Bring up %s...." % (interface))
        scapy.load_contrib('cansocket')
        scapy.load_layer("can")
        #os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
        #time.sleep(0.1)
        sock = CANSocket(channel=interface, bitrate=500000)
        #Creating a native CANSocket only listen for messages with Id == 0x200:
        #socket = CANSocket(channel="vcan0", can_filters=[{'can_id': 0x200, 'can_mask': 0x7FF}])
        #Creating a native CANSocket only listen for messages with Id >= 0x200 and Id <= 0x2ff:
        #socket = CANSocket(channel="vcan0", can_filters=[{'can_id': 0x200, 'can_mask': 0x700}])
        #Creating a native CANSocket only listen for messages with Id != 0x200:
        #CANSocket(channel="vcan0", can_filters=[{'can_id': 0x200 | CAN_INV_FILTER, 'can_mask': 0x7FF}])

    except OSError:
        print("Cannot find %s interface." % (interface))
        exit()

    print('Ready')


def shutdown_can():
    global sock
    sock.close()


def decode_packet(pkt):
    message = []       
    for field in can_fields:            
        try:
            if field == 'flags':        
                message.append(pkt.fields[field].flagrepr())
            else:
                message.append(pkt.fields[field])
        except: 
            message.append(None)

    try:
        datahex = pkt.fields['data'].hex()
        message.append(datahex)
        dataascii = ""
        for i in range(0, len(datahex), 2):
            if 32 <= int(datahex[i : i + 2], 16) <= 126:
                dataascii += chr(int(datahex[i : i + 2], 16))                    
            else:
                dataascii += "."
        message.append(dataascii)

    except:
        message.append(None)
    return message


def recv_msg():
    global sock
    # time needs to be added by keeping track of a time global variable
    message = []    
    try:
        #pkt = sock.sniff(count=1)[0] # Wait until a message is received.
        pkt = scapy.sniff(count=1, opened_socket=sock, timeout=1)[0]
        message = decode_packet(pkt)        

    except KeyboardInterrupt:
        #Catch keyboard interrupt
        #os.system("sudo /sbin/ip link set can0 down")
        print('\n\rRecv Msg Keyboard interrupt')
        exit(0)
    except Exception as e:
        ## possible add EOFError for end of file
        print (e)
        pass

    return message 

def setup_canreader(filepath):
    global sock
    #scapy.load_contrib('cansocket')
    scapy.load_layer("can")
    sock = CandumpReader(filepath)


# setup_canreader("/home/kali/Documents/DEFCON/VicOne/mache/wellsee_mache.log")
# setup_canreader("/home/kali/Documents/DEFCON/VicOne/mache/candump.txt")
# get_fields("can")
# for i in range(20):
#     msg = recv_msg()
#     print (msg)