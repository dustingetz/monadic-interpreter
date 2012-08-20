from pymonads.environment import *

interp_m = env_m

ok = interp_m.unit
#err = err #needs to be lifted if the monad stack changes
bind = interp_m.bind
fmap = interp_m.fmap
seq = interp_m.seq
mmap = interp_m.map
join = interp_m.join
