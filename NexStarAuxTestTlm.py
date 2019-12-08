from NexStarAux import *
import struct


N0 = NexStarAux("", NexStarInputNone())
# test telemetry snooping
t = N0.encode_message('DEV_RA','DEV_HC','MC_GET_POSITION', struct.pack('>i',round(2**24*float(1.5)/360.0))[1:])
N = NexStarAux("", NexStarInputString(t))
tt = N.decode_message(t)
print(tt)


print(N.get_stats())
