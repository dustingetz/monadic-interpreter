from pymonads.error import *
from pymonads.environment import *

interp_m = Environment_t(error_m)


ok = interp_m.unit # => ((42, {}), None)
err = lambda msg: lambda env: ((None, env), msg) # => # ((None, {}), msg)

bind = interp_m.bind
fmap = interp_m.fmap
seq = interp_m.seq
mmap = interp_m.map
join = interp_m.join


def getVal(mv): return mv[0][0]
def getEnv(mv): return mv[0][1]
def getErr(mv): return mv[1]
