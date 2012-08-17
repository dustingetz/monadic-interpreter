from __future__ import division
import math, operator as op


py_primitive_fns = {
    '+':op.add,
    '-':op.sub,
    '*':op.mul,
    '/':op.div,
    'not':op.not_,
    '>':op.gt,
    '<':op.lt,
    '>=':op.ge,
    '<=':op.le,
    '=':op.eq,
    'equal?':op.eq,
    'eq?':op.is_,
    'length':len,
    'cons':lambda x,y:[x]+y,
    'car':lambda x:x[0],
    'cdr':lambda x:x[1:],
    'append':op.add,
    'list':lambda *x:list(x),
    'list?': lambda x:isa(x,list),
    'null?':lambda x:x==[],
    'symbol?':lambda x: isa(x, Symbol)
}

special_forms = {
    'assert': lambda p, errmsg: ok(None) if p else err(errmsg)
}

def lift(fn): #lift is a misnomer, its not a real monadic lift. what is it?
    "inlining this fn seems to break python?"
    return lambda *args: ok(fn(*args))

def add_globals(env):
    "Add some Scheme standard procedures to an environment."
    env.update(vars(math)) # sin, sqrt, ...
    for sym, fn in py_primitive_fns.iteritems():
        env[sym] = lift(fn)
    for sym, fn in special_forms.iteritems():
        env[sym] = fn
    return env