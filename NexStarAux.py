import serial
import struct
import random
import datetime
from collections import defaultdict


class NexStarInputString:
    ''' This class simulates the AUX connection to the telescope to test the NexStarAux class
        it's extremely crude
    '''
    def __init__(self, init_string, dump=True):
        self.value = init_string
        self.dump = dump
        
    def flushInput(self):
        pass
    
    def read(self,count=1):
        if len(self.value) == 0: raise serial.SerialTimeoutException
        count = random.randint(1,count)
        temp_remain = self.value[count:]
        temp_return = self.value[:count]
        self.value = temp_remain
        return temp_return
    
    def write(self,str):
        print(srr)

class NexStarInputFile:
    ''' This class allows one to use a stored file as a source for off-line processing
    '''
    def __init__(self, filename):
        self.buf = open(filename,'rb')
        self.dump = False
        
    def flushInput(self):
        pass
    
    def read(self,count=1):
        value = self.buf.read(count)
        if len(value) == 0: raise serial.SerialTimeoutException
        return value
    
    def write(self,str):
        print(srr)

class NexStarInputNone:
    ''' This class allows one to instantiate a NexStarAux class without any input srouce
    '''
    def __init__(self):
        self.dump = False

    def flushInput(self):
        pass
    def read(self,count=1):
        pass    
    def write(self,str):
        pass


class NexStarAux:
    DEV_IDS = {
        'DEV_MAIN' :   0x01,
        'DEV_HC'   :   0x04,
        'DEV_RA'   :   0x10,
        'DEV_AZM'  :   0x10,
        'DEV_DEC'  :   0x11,
        'DEV_ALT'  :   0x11,
        'DEV_GPS'  :   0xb0,
        'DEV_RTC'  :   0xb2,
    }
    
    # Motor Controller Message IDs
    MC_IDS = {
    #   NAME                        ID    Tx Rx
        'MC_GET_POSITION'        : (0x01, 0, 3),
        'MC_GOTO_FAST'           : (0x02, 3, 0),
        'MC_SET_POSITION'        : (0x04, 3, 0),
        'MC_SET_POS_GUIDERATE'   : (0x06, 2, 0),
        'MC_SET_POS_GUIDERATE_H' : (0x06, 3, 0),
        'MC_SET_NEG_GUIDERATE'   : (0x07, 2, 0),
        'MC_SET_NEG_GUIDERATE_H' : (0x07, 3, 0),
        'MC_LEVEL_START'         : (0x0b, 0, 0),
        'MC_PEC_RECORD_START'    : (0x0c, 0, 0),
        'MC_PEC_PLAYBACK'        : (0x0d, 1, 0),
        'MC_SET_POS_BACKLASH'    : (0x10, 1, 0),
        'MC_SET_NEG_BACKLASH'    : (0x11, 1, 0),
        'MC_LEVEL_DONE'          : (0x12, 0, 1),
        'MC_SLEW_DONE'           : (0x13, 0, 1),
        'MC_PEC_RECORD_DONE'     : (0x15, 0, 1),
        'MC_PEC_RECORD_STOP'     : (0x16, 0, 0),
        'MC_GOTO_SLOW'           : (0x17, 2, 0),
        'MC_GOTO_SLOW_H'         : (0x17, 3, 0),
        'MC_AT_INDEX'            : (0x18, 0, 1),
        'MC_SEEK_INDEX'          : (0x19, 0, 0),
        'MC_MOVE_POS'            : (0x24, 1, 0),
        'MC_MOVE_NEG'            : (0x25, 1, 0),
        'MC_MOVE_PULSE'          : (0x26, 0, 0),
        'MC_GET_PULSE_STATUS'    : (0x27, 0, 0),
        'MC_ENABLE_CORDWRAP'     : (0x38, 0, 0),
        'MC_DISABLE_CORDWRAP'    : (0x39, 0, 0),
        'MC_SET_CORDWRAP_POS'    : (0x3a, 3, 0),
        'MC_POLL_CORDWRAP'       : (0x3b, 0, 1),
        'MC_GET_CORDWRAP_POS'    : (0x3c, 0, 3),
        'MC_GET_POS_BACKLASH'    : (0x40, 0, 1),
        'MC_GET_NEG_BACKLASH'    : (0x41, 0, 1),
        'MC_SET_AUTOGUIDE_RATE'  : (0x46, 1, 0),
        'MC_GET_AUTOGUIDE_RATE'  : (0x47, 0, 1),
        'MC_PROGRAM_ENTER'       : (0x81, 0, 1),
        'MC_PROGRAM_INIT'        : (0x82, 0, 1),
        'MC_PROGRAM_DATA'        : (0x83, 0, 0),
        'MC_PROGRAM_END'         : (0x84, 0, 1),
        'MC_GET_APPROACH'        : (0xfc, 0, 1),
        'MC_SET_APPROACH'        : (0xfd, 1, 0),
        'MC_GET_VER'             : (0xfe, 0, 2),
    }
    
    # GPS Receiver Message IDs
    GPS_IDS = {
    #   NAME                    ID    Tx Rx
        'GPS_GET_LAT'        : (0x01, 0, 3),
        'GPS_GET_LONG'       : (0x02, 0, 3),
        'GPS_GET_DATE'       : (0x03, 0, 2),
        'GPS_GET_YEAR'       : (0x04, 0, 2),
        'GPS_GET_SAT_INFO'   : (0x07, 0, 2),
        'GPS_GET_RCVR_STATUS': (0x08, 0, 2),
        'GPS_GET_TIME'       : (0x33, 0, 3),
        'GPS_TIME_VALID'     : (0x36, 0, 1),
        'GPS_LINKED'         : (0x37, 0, 1),
        'GPS_GET_HW_VER'     : (0x55, 0, 1),
        'GPS_GET_COMPASS'    : (0xA0, 0, 1),
        'GPS_GET_VER'        : (0xFE, 0, 2),
    }
    
    GUIDE_IDS = {
        'GUIDERATE_SIDEREAL' : 0xffff,
        'GUIDERATE_SOLAR'    : 0xfffe,
        'GUIDERATE_LUNAR'    : 0xfffd,
    }
    
    PREAMBLE = 0x3b
    
    
    def __init__(self, port, inputSource = None):
        ''' if useSerial is True, use the real serial port given by port variable
            otherwise, use the fake class NexStarTest that has the same interface as serial but is designed for unit test
        '''
        # Create reverse message name -> id mapping for easy lookup
        self.REV_MC_IDS = {}
        for msg_name in self.MC_IDS.keys():
            self.REV_MC_IDS[self.MC_IDS[msg_name][0]] = msg_name
        
        self.REV_GPS_IDS = {}
        for msg_name in self.GPS_IDS.keys():
            self.REV_GPS_IDS[self.GPS_IDS[msg_name][0]] = msg_name

        # Create reverse device name -> id mapping for easy lookup
        self.REV_DEV_IDS = {}
        self.MC_SET = []
        self.GPS_SET = []
        
        for dev_name in self.DEV_IDS.keys():
            # Prefer equatorial device names since there is no way to tell which config the scope is in
            if dev_name not in ('DEV_AZM', 'DEV_ALT'):
                self.REV_DEV_IDS[self.DEV_IDS[dev_name]] = dev_name
            if dev_name in ('DEV_RA', 'DEV_DEC', 'DEV_AZM', 'DEV_ALT'):
                self.MC_SET.append(self.DEV_IDS[dev_name])
            elif dev_name == 'DEV_GPS':
                self.GPS_SET.append(self.DEV_IDS[dev_name])
        
        # create the structure to hold the statistics
        # it will allow automatic acces to stats[src][dst] without having to create them first
        self.stats = defaultdict(lambda: defaultdict(int))

        # initialze the incoming data stream
        self.in_message = bytes()
        if inputSource == None:
            self.serial = serial.Serial(port, 19200, timeout=1.0)
            self.serial.flushInput()
        else:
            # if the input given, use the given class instance
            # it should be intialized outside of this call
            self.serial = inputSource
    
        # Setup dump file reading from read serial port or if requested by the reader class
        if inputSource == None or self.serial.dump:
            self.dumpfile = open('NexStarAux.dump','ab')
        else:
            self.dumpfile = None
        
    def get_CRC(self, data):
        '''Return message CRC. Assumes that data is a byte array of the entire message, including the preable but excluding the CRC byte
        '''
        temp = 0
        for i_byte in data[1:]:
            temp += i_byte
            # print('%x'%i_byte)
        # Python doesn't do two's complement arithmetic, so need to work with packing numbers to get 2's complement
        # print('Sum: %x'%temp)
        tt = struct.pack('>i',-temp)
        # print('Packed: %x'%(tt[-1]&0xff))
        return tt[-1]&0xff
         
    def check_CRC(self, data):
        assert self.get_CRC(data[:-1]) == data[-1]
    
    def alive(self):
        print("Alive")
    
    def encode_message(self, src, dst, msg_id, data=bytes()):
        if dst in ('DEV_RA', 'DEV_DEC', 'DEV_AZM', 'DEV_ALT') or \
           src in ('DEV_RA', 'DEV_DEC', 'DEV_AZM', 'DEV_ALT'):
            (id,tx,rx) = self.MC_IDS[msg_id]
        elif dst == 'DEV_GPS' or src == 'DEV_GPS':
            (id,tx,rx) = self.GPS_IDS[msg_id]
        else:
            raise ValueError("Unknown device ID, src/dst: 0x%x/0x%x"%(src,dst))
        
        # assert tx == len(data)  # Ensure that we got the right size data for the given message
        data_packed =  bytes([self.PREAMBLE, len(data)+3, self.DEV_IDS[src], self.DEV_IDS[dst], id]) + data
        # Add CRC byte
        CRC = self.get_CRC(data_packed)
        return data_packed+bytes([CRC])
    
    def validate_message(self,data, strict = True):
        assert len(data) > 0             # Reject empty messages, they will cause run-time errors later, instead of assertion errors
        assert data[0] == self.PREAMBLE  # Ensure that preable is first
        # print("Passed preamble")
        self.check_CRC(data)             # Ensure correct CRC
        # print("Passed CRC")
        assert data[1]+3 == len(data)    # Ensure the message is the right length
        # print("Checking strict: %d"% strict)
        if strict:
            assert data[2] in self.REV_DEV_IDS.keys() # Ensure source is a valid device ID
            assert data[3] in self.REV_DEV_IDS.keys() # Ensure dest is a valid device ID
            if data[2] in self.MC_SET or data[3] in self.MC_SET:
                assert data[4] in self.REV_MC_IDS.keys() # Message id is correct
            elif data[2] in self.GPS_SET or data[3] in self.GPS_SET:
                assert data[4] in self.REV_GPS_IDS.keys() # Message id is correct
            else:
                raise AssertionError("Unknown device ID, src/dst: 0x%x/0x%x"%(data[2],data[3]))

    def get_dev_tag(self, dev_id):
        try:
            dev_tag = self.REV_DEV_IDS[dev_id]
        except KeyError:
            dev_tag = hex(dev_id)
        return dev_tag
    
    def record_stats(self,src_id, dest_id):
        self.stats[src_id][dest_id] += 1
        
    def get_stats(self):
        dst_set = set()
        for src in self.stats.keys():
            dst_set |= set(self.stats[src].keys())
        buf = ' '*10 + '  F R O M:\n'
        buf += '  TO:   ' + ''.join(['%8s'%self.get_dev_tag(x) for x in sorted(self.stats.keys())]) + '\n'
        for dest in sorted(dst_set):
            buf += '%8s'%self.get_dev_tag(dest)
            for src in sorted(self.stats.keys()):
                buf += '%8d'%self.stats[src][dest]
            buf += '\n'
        return(buf)
    
    
    def decode_message(self, data, strict=True):
        self.validate_message(data, strict)
        payload = data[5:-1]
        src_id = data[2]
        dst_id = data[3]
        msg_id = data[4]
        self.record_stats(src_id,dst_id)
        # Figure out which lookup to use based on the device IDs
        if src_id in self.MC_SET or dst_id in self.MC_SET:
            lookup = self.REV_MC_IDS
        elif src_id in self.GPS_SET or dst_id in self.GPS_SET:
            lookup = self.REV_GPS_IDS
        else:
            # If symbolic lookup is not possible, fake the lookupu table so that it returns the hex string of the message ID
            lookup = {}
            lookup[msg_id] = hex(msg_id)
        src_tag = self.get_dev_tag(src_id)
        dst_tag = self.get_dev_tag(dst_id)

        # If message contains decodeable telemetry, grab it
        if src_id == self.DEV_IDS['DEV_RA'] and msg_id == self.MC_IDS['MC_GET_POSITION'][0] and len(payload) == 3 :
            # this is RA position report
            (self.RA,) = struct.unpack('>I',payload + bytes([0]))
            self.RA >>= 8
            self.RA *= 360.0/(2**24)
            return "%s -> %s (%s, %f)"%(src_tag, dst_tag, lookup[msg_id], self.RA)
        if src_id == self.DEV_IDS['DEV_DEC'] and msg_id == self.MC_IDS['MC_GET_POSITION'][0] and len(payload) == 3 :
            # this is DEC position report
            (self.DEC,) = struct.unpack('>I',payload + bytes([0]))
            self.DEC >>= 8
            self.DEC *= 360.0/(2**24)
            return "%s -> %s (%s, %f)"%(src_tag, dst_tag, lookup[msg_id], self.DEC)
        if src_id == self.DEV_IDS['DEV_RA'] and msg_id == self.MC_IDS['MC_SLEW_DONE'][0] and len(payload) == 1 :
            # This is a RA SLEW DONE report
            self.RA_SLEW_DONE = payload[0] == 0xff
            return "%s -> %s (%s, %d)"%(src_tag, dst_tag, lookup[msg_id], self.RA_SLEW_DONE)
        if src_id == self.DEV_IDS['DEV_DEC'] and msg_id == self.MC_IDS['MC_SLEW_DONE'][0] and len(payload) == 1 :
            # This is a DEC SLEW DONE report
            self.DEC_SLEW_DONE = payload[0] == 0xff
            return "%s -> %s (%s, %d)"%(src_tag, dst_tag, lookup[msg_id], self.DEC_SLEW_DONE)
        if src_id == self.DEV_IDS['DEV_RA'] and msg_id == self.MC_IDS['MC_POLL_CORDWRAP'][0] and len(payload) == 1 :
            # This is a pollwrap report
            self.RA_CORDWRAP = payload[0] == 0xff
            return "%s -> %s (%s, %d)"%(src_tag, dst_tag, lookup[msg_id], self.DEC_CORDWRAP)
        if src_id == self.DEV_IDS['DEV_DEC'] and msg_id == self.MC_IDS['MC_POLL_CORDWRAP'][0] and len(payload) == 1 :
            # This is a pollwrap report
            self.DEC_CORDWRAP = payload[0] == 0xff
            return "%s -> %s (%s, %d)"%(src_tag, dst_tag, lookup[msg_id], self.DEC_CORDWRAP)
        if dst_id in  (self.DEV_IDS['DEV_RA'], self.DEV_IDS['DEV_DEC'], self.DEV_IDS['DEV_ALT'], self.DEV_IDS['DEV_AZM']) and \
           msg_id in  (self.MC_IDS['MC_GOTO_FAST'][0], self.MC_IDS['MC_GOTO_SLOW'][0]) and \
           len(payload) == 3 :
           # This is a high precision GOTO request, decode but don't set any telemtry
           (temp,) = struct.unpack('>I',payload + bytes([0]))
           temp >>= 8
           temp *= 360.0/(2**24)
           return "%s -> %s (%s, %f)"%(src_tag, dst_tag, lookup[msg_id], temp)
        if dst_id in  (self.DEV_IDS['DEV_RA'], self.DEV_IDS['DEV_DEC'], self.DEV_IDS['DEV_ALT'], self.DEV_IDS['DEV_AZM']) and \
           msg_id in  (self.MC_IDS['MC_GOTO_FAST'][0], self.MC_IDS['MC_GOTO_SLOW'][0]) and \
           len(payload) == 2 :
           # This is a low precision GOTO request, decode but don't set any telemtry
           (temp,) = struct.unpack('>H',payload)
           temp *= 360.0/(2**24)
           return "%s -> %s (%s, %f)"%(src_tag, dst_tag, lookup[msg_id], temp)

        # Now use the selected lookup based on the payload size
        # Specific decodeable messages had been intercepted by now, so this decode is for generic messages
        if len(payload) > 0:
                try:
                    return "%s -> %s (%s, %s)"%(src_tag, dst_tag, lookup[msg_id], '0x'+payload.hex())
                except:
                    return "%s -> %s (%s, %s)"%(src_tag, dst_tag, hex(msg_id), '0x'+payload.hex())
        else:
            try:
                return "%s -> %s (%s)"%(src_tag, dst_tag, lookup[msg_id])
            except KeyError:
                return "%s -> %s (%s)"%(src_tag, dst_tag, hex(msg_id))

    def read(self,size=1):
        'Wrapped read()  so that we can dump anything that has been read'
        temp = self.serial.read(size)
        if self.dumpfile is not None:
            self.dumpfile.write(temp)
        return temp
        
    def read_message(self, strict = False):
        ''' Reads bytes from a serial port (self.serial) WITHOUT ALIGNMENT assumptions
            Finds a valid message based on the expeced format, even if the first byte read is at a random position in the data stream
            Returns a valid message as a byte() array
        '''
        while (True):
            # print('Testing:', self.in_message)
            if len(self.in_message) == 0:
                self.in_message  = self.read(1)
            elif len(self.in_message) == 1:
                if self.in_message[0] == self.PREAMBLE:
                    # got preable, try reading number of words
                    # note that preable is the same as MC_POLL_CORDWRAP, and in general is not unique so does not mean too much
                    self.in_message += self.read(1)
                else:
                    # if a single-byte message is not a preable, there is nothing we can do, discard and read the next byte
                    self.in_message = self.read(1)
            elif len(self.in_message) == 2:
                # Have two bytes, see if any good
                if self.in_message[0] == self.PREAMBLE and self.in_message[1] <= 8:
                    # PREABLE and mesasge length are reasonable, read as many bytes as message length dictates, plus CRC byte
                    # but keep in mind that the serial port may return fewer bytes than requested
                    self.in_message += self.read(self.in_message[1]+1)
                else:
                    # something is off with the two-byte message, remove the first byte and try again
                    self.in_message = self.in_message[1:]
            else:
                if self.in_message[0] == self.PREAMBLE and self.in_message[1] <= 8:
                    if len(self.in_message) < self.in_message[1]+3:
                        # The message is shorter than it should be
                        # it could be that the serial port produced less data than requested; request bytes needed to make a full message
                        self.in_message += self.read(self.in_message[1]+3 - len(self.in_message))
                    else:
                        # this message has a chance, but it could be that we got a start of another message as well, so try to find the shortest valid message
                        test_msg = self.in_message[:self.in_message[1]+3]
                        # print('Almost: ', test_msg)
                        try:
                            # print(self.decode_message(test_msg))
                            self.validate_message(test_msg, strict)
                            # This is a good message. Remove it from current queue and return
                            self.in_message = self.in_message[self.in_message[1]+3:]
                            # print('Remaining: ', self.in_message)
                            return test_msg
                        except AssertionError:
                            # Not a valid message;  remove the first byte and try again
                            print ("Rejected: ", self.in_message.hex())
                            self.in_message = self.in_message[1:]
                else:
                    # Long message, but wrong, remove the first byte and try again
                    self.in_message = self.in_message[1:]

    def encode_GPS_GET_LONG(self, deg=-(118.0+29.0/60)):
        return self.encode_message('DEV_GPS','DEV_HC','GPS_GET_LONG', \
                               struct.pack(">i",round(2**24*float(deg)/360.0))[1:])
    def encode_GPS_GET_LAT(self, deg=(34.0+13.0/60)):
        return self.encode_message('DEV_GPS','DEV_HC','GPS_GET_LAT', \
                               struct.pack(">i",round(2**24*float(deg)/360.0))[1:])

    def encode_GPS_GET_TIME(self,d =datetime.datetime.utcnow().timetuple()[3:6]):
        '''Encode current UTC time'''
        return self.encode_message('DEV_GPS','DEV_HC','GPS_GET_TIME', \
                                   bytes(d))

    def encode_GPS_GET_DATE(self, d =datetime.datetime.utcnow().timetuple()[1:3]):
        '''Encode current UTC date'''
        return self.encode_message('DEV_GPS','DEV_HC','GPS_GET_DATE', \
                                   bytes(d))
    
    def encode_GPS_GET_YEAR(self, d=datetime.datetime.utcnow().timetuple()[0]):
        '''Encode current UTC year'''
        return self.encode_message('DEV_GPS','DEV_HC','GPS_GET_YEAR', \
                struct.pack(">i",d)[2:])
        
    def encode_GPS_GET_HW_VER(self):
        return self.encode_message('DEV_GPS','DEV_HC','GPS_GET_HW_VER',b'\xab')

    def encode_GPS_GET_VER(self):
        return self.encode_message('DEV_GPS','DEV_HC','GPS_GET_VER',b'\x01\x00')
        
    @staticmethod
    def wrap_angle(angle):
        while angle < 0:   angle += 360.0
        while angle > 360: angle -= 360.0
        return float(angle)
    
    def encode_MC_SLEW(self, axis, pos, fast_slew = True):
        if axis not in ('DEV_RA', 'DEV_DEC', 'DEV_ALT', 'DEV_AZM'):
            raise ValueError("Invalid axis: %s"%axis)
        
        if fast_slew:
            msg_tag = 'MC_GOTO_FAST'
        else:
            msg_tag = 'MC_GOTO_SLOW_H'
        
        pos_enc = struct.pack(">I",round(2**24*float(self.wrap_angle(pos))/360.0))[1:]
        return self.encode_message('DEV_HC', axis, msg_tag,pos_enc)
        
        
if __name__ == '__main__':
    print("Hello")
    N = NexStarAux('null', NexStarInputNone())
    
    # Delete the old dump file so it doesn't grow every time the test is run-time
    import os
    if os.path.exists('NexStarAux.dump'):
        os.remove('NexStarAux.dump')
    
    assert N.get_CRC(b'\x3b\x03\x04\x10\xfe') == 0xEB
    assert N.get_CRC(b'\x3b\x05\x10\x04\xfe\x04\x03') == 0xE2
    N.check_CRC(b'\x3b\x03\x04\x10\xfe\xeb')
    try:
        N.check_CRC(b'\x3b\x05\x10\x04\xfe\xeb')
        raise ValueError("This needs to fail")
    except AssertionError:
        # print("expected error")
        pass
    N.check_CRC(b'\x3b\x05\x10\x04\xfe\x04\x03\xe2')
    assert N.encode_message   ('DEV_HC','DEV_AZM','MC_GET_VER',bytes()) == b'\x3b\x03\x04\x10\xfe\xeb'
    assert N.encode_message   ('DEV_HC','DEV_AZM','MC_GET_VER') == b'\x3b\x03\x04\x10\xfe\xeb'
    assert N.decode_message(b'\x3b\x03\x04\x10\xfe\xeb') == 'DEV_HC -> DEV_RA (MC_GET_VER)'
    
    N = NexStarAux("", NexStarInputString(b'\x3b\x03\x04\x10\xfe\xeb'))
    assert N.read_message() == b'\x3b\x03\x04\x10\xfe\xeb'
    
    # N = NexStarAux(b'\x00\x3b\x03\x04\x10\xfe\xeb', False)
    N = NexStarAux("", NexStarInputString(b'\x00\x3b\x03\x04\x10\xfe\xeb'))
    assert N.read_message() == b'\x3b\x03\x04\x10\xfe\xeb'

    N = NexStarAux("", NexStarInputString(b'\x00\x3b\x03\x04\x10\xfe\xeb\x3b\x00'))
    assert N.read_message() == b'\x3b\x03\x04\x10\xfe\xeb'

    N = NexStarAux("", NexStarInputString(b'\x00\x3b\x03\x04\x10\xfe\xeb\x3b\x03\x04\x10\xfe\xeb'))
    assert N.read_message() == b'\x3b\x03\x04\x10\xfe\xeb'
    assert N.read_message() == b'\x3b\x03\x04\x10\xfe\xeb'

    N = NexStarAux("", NexStarInputString(b'\x3b\x3b\x03\x04\x10\xfe\xeb\x00\x3b\x03\x04\x10\xfe\xeb'))
    assert N.read_message() == b'\x3b\x03\x04\x10\xfe\xeb'
    assert N.read_message() == b'\x3b\x03\x04\x10\xfe\xeb'

    try:
        N = NexStarAux("", NexStarInputString(b'\x00\x3b\x03\x04\x10\xfe\xeb\x00\x3b\x03\x04\x10\xfe'))
        assert N.read_message() == b'\x3b\x03\x04\x10\xfe\xeb'
        assert N.read_message() == b'\x3b\x03\x04\x10\xfe\xeb'
        raise ValueError( "This should fail: not enough data for second message")
    except serial.SerialTimeoutException:
        # print("Expected error")
        pass

    t = N.encode_message   ('DEV_HC','DEV_AZM','MC_GOTO_FAST', b'123')
    print(N.decode_message(t))
    assert N.decode_message(t) == "DEV_HC -> DEV_RA (MC_GOTO_FAST, 69.182003)"
    N = NexStarAux("", NexStarInputString(t))
    assert N.read_message() == b';\x06\x04\x10\x02123N'

    t = N.encode_message   ('DEV_HC','DEV_AZM','MC_MOVE_POS', b'0')
    N.decode_message(t) == "DEV_HC -> DEV_AZM (MC_MOVE_POS, b'0')"
    N = NexStarAux("", NexStarInputString(t))
    assert N.read_message() == b';\x04\x04\x10$0\x94'
    
    t = []
    t.append(N.encode_message   ('DEV_HC','DEV_AZM','MC_GOTO_FAST', b'123'))
    t.append(N.encode_message   ('DEV_HC','DEV_AZM','MC_GOTO_FAST', b'456'))
    t.append(N.encode_message   ('DEV_HC','DEV_AZM','MC_GOTO_FAST', b'789'))
    N = NexStarAux("", NexStarInputString(b'hd'+ t[0]+b'wer' + t[1]+t[2]))
    try:
        while (True):
            print(N.decode_message(N.read_message()))
    except serial.SerialTimeoutException:
        pass
    
    t = N.encode_message('DEV_HC','DEV_GPS','GPS_GET_TIME')
    assert t == b';\x03\x04\xb03\x16'
    assert N.decode_message(t) == "DEV_HC -> DEV_GPS (GPS_GET_TIME)"

    # Test handling of unknown devices
    t = b';\x03\x14\xb03\x06'
    assert N.decode_message(t, False) == "0x14 -> DEV_GPS (GPS_GET_TIME)"

    t = b';\x03\x14\xb83\xfe'
    assert N.decode_message(t, False) == "0x14 -> 0xb8 (0x33)"


    t = N.encode_message('DEV_GPS','DEV_HC','GPS_GET_TIME', bytes([17,43,22]))
    assert t == b';\x06\xb0\x043\x11+\x16\xc1'
    assert N.decode_message(t) == "DEV_GPS -> DEV_HC (GPS_GET_TIME, 0x112b16)"

    t = N.encode_message('DEV_GPS','DEV_HC','GPS_GET_DATE', bytes([1,16]))
    assert N.decode_message(t) == "DEV_GPS -> DEV_HC (GPS_GET_DATE, 0x0110)"

    t = -(75.0+54.0/60 + 16.35/3600)
    tt = N.encode_GPS_GET_LONG(t)
    assert N.decode_message(tt) == "DEV_GPS -> DEV_HC (GPS_GET_LONG, 0xca0600)"

    t = +(45.0+20.0/60 + 30.17/3600)
    tt = N.encode_GPS_GET_LAT(t)
    assert N.decode_message(tt) == "DEV_GPS -> DEV_HC (GPS_GET_LAT, 0x203e35)"
    
    tt = N.encode_GPS_GET_YEAR()
    print(N.decode_message(tt))
    tt = N.encode_GPS_GET_YEAR(2003)
    assert N.decode_message(tt) == "DEV_GPS -> DEV_HC (GPS_GET_YEAR, 0x07d3)"
    
    tt = N.encode_GPS_GET_DATE()
    print(N.decode_message(tt))
    tt = N.encode_GPS_GET_DATE((1,16))
    assert N.decode_message(tt) == "DEV_GPS -> DEV_HC (GPS_GET_DATE, 0x0110)"
    tt = N.encode_GPS_GET_TIME()
    print(N.decode_message(tt))
    tt = N.encode_GPS_GET_TIME((17,43,22))
    assert N.decode_message(tt) == "DEV_GPS -> DEV_HC (GPS_GET_TIME, 0x112b16)"
    tt = N.encode_GPS_GET_HW_VER()
    assert N.decode_message(tt) == "DEV_GPS -> DEV_HC (GPS_GET_HW_VER, 0xab)"
    tt = N.encode_GPS_GET_VER()
    assert N.decode_message(tt) == "DEV_GPS -> DEV_HC (GPS_GET_VER, 0x0100)"
    
    # Test goto encoding
    tt = N.encode_MC_SLEW('DEV_RA',1.5)
    assert N.decode_message(tt) == "DEV_HC -> DEV_RA (MC_GOTO_FAST, 1.499999)"
    tt = N.encode_MC_SLEW('DEV_DEC',1.5)
    assert N.decode_message(tt) == "DEV_HC -> DEV_DEC (MC_GOTO_FAST, 1.499999)"

    tt = N.encode_MC_SLEW('DEV_DEC',359.99)
    assert N.decode_message(tt) == "DEV_HC -> DEV_DEC (MC_GOTO_FAST, 359.990001)"

    # Test angle wrap
    tt = N.encode_MC_SLEW('DEV_RA',361.5)
    assert N.decode_message(tt) == "DEV_HC -> DEV_RA (MC_GOTO_FAST, 1.499999)"

    # Test angle wrap
    tt = N.encode_MC_SLEW('DEV_RA',-360+1.5)
    assert N.decode_message(tt) == "DEV_HC -> DEV_RA (MC_GOTO_FAST, 1.499999)"

    # Test slow GOTO
    tt = N.encode_MC_SLEW('DEV_RA',1.5, False)
    # print(N.decode_message(tt))
    assert N.decode_message(tt) == "DEV_HC -> DEV_RA (MC_GOTO_SLOW_H, 1.499999)"

    print(N.get_stats())
    
    
