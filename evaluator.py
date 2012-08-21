from parser import Symbol
from primitives import *
from interp_m import *

# naming conventions in leiu of types:
# 'mv', 'mproc', ... : monadic value in interp_m
# 'x': simple value
# 'xs', 'mvs': lists
# all eval_* functions return monadic values

def eval_symbol(x):
    return envGet(x)

def eval_literal(x):
    return ok(x)

def eval_quote(x):
    (_, exp) = x
    return ok(exp)

def eval_if(x):
    (_, test, conseq, alt) = x
    def _doif(val):
        return (conseq if val else alt)
    mbranch = fmap(_doif, eval(test))
    return bind(mbranch, lambda branch: eval(branch))

def eval_proc(exprs):
    m_xs = mmap(eval, exprs) # return type: \env -> [xs]
    def _apply(proc, args):
        return proc(*args)
    return bind(m_xs, lambda xs: _apply(xs[0], xs[1:]))

def eval_define(x):
    (_, var, exp) = x
    return bind( eval(exp), lambda val: envSet(var, val))

def eval_set(x):
    (_, var, exp) = x
    return bind( envBound(var),     lambda bound:
           bind( ok(None) if bound
                 else err("can't set unbound symbol `%s`"%var), lambda _:
           bind( eval(exp),         lambda val:
                 envSet(var, val)   )))

def eval_begin(x):
    exprs = x[1:]
    def _dobegin(exp, exprs): # -> mv
        mfirst = eval(exp)
        if not exprs: return mfirst
        return bind(mfirst, lambda _: _dobegin(exprs[0], exprs[1:]))
    return _dobegin(exprs[0], exprs[1:])

def eval_lambda(x):
    (_, vars, exp) = x
    def proc(*args):
        return bind(envSetAll(zip(vars, args)), lambda _: eval(exp))
    return ok(proc)



def eval(x):
    if isinstance(x, Symbol):
        return eval_symbol(x)
    elif not isinstance(x, list):
        return eval_literal(x)

    # these cannot be monadic special forms due to strict evaluation
    # with lazy evaluation, these can be injected into the environment
    elif x[0] == 'quote':
        return eval_quote(x)
    elif x[0] == 'if':
        return eval_if(x)
    elif x[0] == 'set!':
        return eval_set(x)
    elif x[0] == 'define':
        return eval_define(x)
    elif x[0] == 'lambda':
        return eval_lambda(x)
    elif x[0] == 'begin':
        return eval_begin(x)
    else:
        return eval_proc(x)


if __name__=="__main__":
    import unittest
    unittest.main(exit=False)
