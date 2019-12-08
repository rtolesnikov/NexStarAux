from NexStarAux import *

# test reading from the dump file
N = NexStarAux("",NexStarInputFile('NexStarAux.dump'))
try:
    while(True):
        print(N.decode_message(N.read_message()))
except serial.SerialTimeoutException:
    pass
print(N.get_stats())
