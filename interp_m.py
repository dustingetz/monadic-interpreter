#from pymonads.error import error_m, err
from pymonads.environment import *

interp_m = env_m

ok = interp_m.unit
#err = err #needs to be lifted if the monad stack changes
bind = interp_m.bind
fmap = interp_m.fmap
seq = interp_m.seq
mmap = interp_m.map
join = interp_m.join

# bring into this namespace
env_get = env_m.get_m
env_set = env_m.set_m
env_runIn = env_m.runIn_s
env_ask = env_m.ask_m
