from __future__ import division
import math, operator as op

from evaluator import *
from interp_m import *
from parser import *

_py_primitive_fns = {
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
    'list?': lambda x:isinstance(x,list),
    'null?':lambda x:x==[],
    'symbol?':lambda x: isinstance(x, Symbol)
}

# special forms are monadic functions
_special_forms = {
    'assert': lambda p, errmsg: ok(None) if p else err(errmsg)
    ,'dumpenv': lambda: envAsk
}



def add_globals(env):
    "Add some Scheme standard procedures to an environment."
    env.update(vars(math)) # sin, sqrt, ...
    for sym, fn in _py_primitive_fns.iteritems():
        env[sym] = liftEnv(fn)
    for sym, fn in _special_forms.iteritems():
        env[sym] = fn
    return env

def to_string(exp):
    "Convert a Python object back into a Lisp-readable string."
    return '('+' '.join(map(to_string, exp))+')' if isinstance(exp, list) else str(exp)

def repl(env, prompt='lis.py> '):
    while True:
        mval = eval(parse(raw_input(prompt)))
        ival = mval(env) # => ((42, {}), None)

        if getErr(ival): print "Error:", getErr(ival)
        else: print to_string(getVal(ival))

        env = getEnv(ival)
