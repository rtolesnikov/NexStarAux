from NexStarAux import *

# test reading from the dump file
# N = NexStarAux("",NexStarInputFile('NexStarAux.dump'))
N = NexStarAux("",NexStarInputFile('cap.bin'))
try:
    while(True):
        print(N.decode_message(N.read_message(), False))
except serial.SerialTimeoutException:
    pass
print(N.get_stats())
