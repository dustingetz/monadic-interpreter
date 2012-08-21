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



def to_string(exp):
    "Convert a Python object back into a Lisp-readable string."
    return '('+' '.join(map(to_string, exp))+')' if isinstance(exp, list) else str(exp)

def _buildDefaultEnv():
    "Add some Scheme standard procedures to an environment."
    env = {}
    env.update(vars(math)) # sin, sqrt, ...
    for sym, fn in _py_primitive_fns.iteritems():
        env[sym] = liftEnv(fn)
    for sym, fn in _special_forms.iteritems():
        env[sym] = fn
    return env


class Repl:
    _defaultEnv = _buildDefaultEnv()
    def resetEnv(self):
        self.env = self._defaultEnv.copy()

    def __init__(self):
        self.resetEnv()

    def evalForm(self, form):
        mval = eval(parse(form))
        ival = envRunIn(mval, self.env) # => ((42, {...}), None)
        self.env = getEnv(ival)
        return ival


def repl(prompt='lis.py> '):
    r = Repl()
    while True:
        ival = r.evalForm(raw_input(prompt))

        if getErr(ival): print "Error:", getErr(ival)
        else: print to_string(getVal(ival))
