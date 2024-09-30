import scapy.all as scapy

ip_fields, tcp_fields, udp_fields = None, None, None         # global variable for fields
prefix = "IPPROTO_"
table = {num:name[len(prefix):] 
        for name,num in vars(scapy.socket).items()
            if name.startswith(prefix)}  

def get_interfaces():
    list = scapy.get_if_list() 
    print (list)
    print ( type(list[0]) )

    for interface in list:
        print (interface)
        try:
            pkt = scapy.sniff(iface=interface, timeout=5, filter="tcp")
            print ( pkt )
        except:
            print ("Error opening interface.")

def get_fields(bus_type):    
    global ip_fields
    global tcp_fields
    global udp_fields
    if bus_type == "eth":
        ip_fields = [field.name for field in scapy.IP().fields_desc]
        tcp_fields = [field.name for field in scapy.TCP().fields_desc]
        udp_fields = [field.name for field in scapy.UDP().fields_desc]
        dataframe_fields = ip_fields + ['time'] + tcp_fields + udp_fields + ['payload','payload_raw']
        return dataframe_fields

def recv_msg():
    # time needs to be added by keeping track of a time global variable
    message = []
    try:
        pkt = scapy.sniff(count=1)[0] # Wait until a message is received.
        ethernet_frame = pkt
        ip_pkt = ethernet_frame.payload

        for field in ip_fields:            
            try:
                if field == 'options':
                    message.append(len(ip_pkt.fields[field]))
                elif field == 'proto':
                    message.append( table[ip_pkt.fields[field]] )
                else:
                    message.append(ip_pkt.fields[field])
            except: 
                message.append(None)

                    
        message.append(pkt.time)

        layer_type = type(ip_pkt.payload)
        print (layer_type)

        for field in tcp_fields:
            try:
                if field == 'options':
                    message.append(len(pkt[layer_type].fields[field]))
                else:
                    message.append(pkt[layer_type].fields[field])
            except:
                message.append(None)

        for field in udp_fields:
            try:
                if field == 'options':
                    message.append(len(pkt[layer_type].fields[field]))
                else:
                    message.append(pkt[layer_type].fields[field])
            except:
                message.append(None)

        message.append(len(pkt[layer_type].payload))
        message.append(pkt[layer_type].payload.original)        

    
    except KeyboardInterrupt:
        #Catch keyboard interrupt
        #os.system("sudo /sbin/ip link set can0 down")
        print('\n\rRecv Msg Keyboard interrupt')
        exit(0)
    except:
        pass

    return message        


#print ( get_fields("eth") )
#recv_msg()
# scapy.load_layer("can")
# can_fields = [field.name for field in CAN().fields_desc] 
# print (can_fields)