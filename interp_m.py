from pymonads.error import *
from pymonads.environment import *

interp_m = Environment_t(error_m)

def liftEnv(fn): #inlining this fn seems to break python?
    return lambda *args: ok(fn(*args))



bind = interp_m.bind
fmap = interp_m.fmap
seq = interp_m.seq
mmap = interp_m.map
join = interp_m.join

ok = interp_m.unit # => ((42, {}), None)
err = lambda msg: lambda env: ((None, env), msg) # => # ((None, {}), msg)

def getVal(mv): return mv[0][0]
def getEnv(mv): return mv[0][1]
def getErr(mv): return mv[1]

def envAsk(env):
    return error_m.ok((env, env))

def envReplace(newenv):
    def _(env):
        return error_m.ok((None, newenv))
    return _

def envBound(sym):
    def _(env):
        return error_m.ok((sym in env, env))
    return _

def envSetAll(pairs):
    def _(env):
        newenv = env.copy()
        newenv.update(pairs)
        return error_m.ok((None, newenv))
    return _

def envSet(var, val): return envSetAll([(var,val)])

def envRunIn(mv, env): return mv(env)

def envLocal(mv, localEnv):
    return bind( envAsk,                 lambda curEnv: # save the env ("push")
           bind( envReplace(localEnv),   lambda _:      # restore the subenv
           bind( mv,                     lambda retval: # evaluate
           bind( envReplace(curEnv),     lambda _:      # restore the old env ("pop")
                 ok(retval)              ))))           # return

def envGet(sym):
    #return bind( envAsk, lambda env: ok(env[sym]))
    return bind( envAsk, lambda env:
                 ok(env[sym]) if sym in env
                              else err("referenced unbound symbol %s"%sym))


def test():
    r = ok(13)
    assert envRunIn(r, {}) == ((13, {}), None)
    assert getVal(envRunIn(r, {})) == 13
    assert getErr(envRunIn(r, {})) == None

    assert envAsk({}) == (({}, {}), None)
    assert envRunIn(envAsk, {}) == (({}, {}), None)
    assert envRunIn(envAsk, {'x':3}) == (({'x':3}, {'x':3}), None)

    assert envSet('x',1)({}) == ((None, {'x': 1}), None)
    assert envRunIn(envSet('x', 1), {}) == ((None, {'x': 1}), None)

    iv = envRunIn( envGet('x'), {'x':1})
    assert iv == ((1, {'x': 1}), None)
    assert getVal(iv) == 1
    assert getEnv(iv) == {'x':1}
    assert getErr(iv) == None

    r = bind(envSet('x', 1), lambda _:
        bind(envGet('x'), lambda x: ok(x)))
    iv = envRunIn(r, {})
    assert getVal(iv) == 1
    assert getErr(iv) == None
    assert getEnv(iv) == {'x':1}

    r = bind(r, lambda _: bind(envBound('x'), lambda bound: ok(bound)))
    iv = envRunIn(r, {})
    assert getVal(iv) == True

    r = bind(envSet('x',1), lambda _: ok(42))
    assert getVal(envRunIn(r, {})) == 42

    r = bind(envSet('x',1), lambda _: envGet('x'))
    iv = envRunIn(r, {})
    assert getVal(iv) == 1

if __name__=="__main__":
    test()
    print "tests passed: interp_m"
