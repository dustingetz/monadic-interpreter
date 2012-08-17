from parser import Symbol

from pymonads.error import error_m, err



interp_m = error_m # cont_t state_t error_t identity_m

ok = interp_m.unit
err = err #needs to be lifted if the monad stack changes
bind = interp_m.bind
fmap = interp_m.fmap
seq = interp_m.seq
mmap = interp_m.map




class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms,args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        assert (var in self) or self.outer, "unbound var: %s"%var
        return self if var in self else self.outer.find(var)




isa = isinstance

def eval(x, env):
    "Evaluate an expression in an environment."
    if isa(x, Symbol):             # variable reference
        assert env
        return ok(env.find(x)[x])

    elif not isa(x, list):         # constant literal
        return ok(x)

    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return ok(exp)

    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        def _doif(val):
            return (conseq if val else alt)
        mbranch = fmap(_doif, eval(test, env))
        return bind(mbranch, lambda branch: eval(branch, env))

    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x
        def _doset(val):
            #assert env.find(var) -- this is a RuntimeError
            assert env
            env.find(var)[var] = val
            return None
        return fmap(_doset, eval(exp, env))

    elif x[0] == 'define':         # (define var exp)
        (_, var, exp) = x
        def _dodefine(val):
            env[var] = val
            return None
        return fmap(_dodefine, eval(exp, env))

    elif x[0] == 'lambda':         # (lambda (var*) exp)
        (_, vars, exp) = x
        return ok(lambda *args: eval(exp, Env(vars, args, env)))

    elif x[0] == 'begin':          # (begin exp*)
        exprs = x[1:]

        # this code is a recursive monad comprehension, it composes the plumbing
        # such that errors short circuit etc, but discards the passed in value
        # and just evaluates the next expression. the return value is monadic -
        # the last expression evaluated.
        #
        # version if there wasn't a monad:
        #
        #   for exp in x[1:]:
        #     val = eval(exp, env)
        #   return val
        #
        def _dobegin(exp, exprs): # -> mv
            mfirst = eval(exp, env)
            if not exprs: return mfirst
            return bind(mfirst, lambda _: _dobegin(exprs[0], exprs[1:]))
        return _dobegin(exprs[0], exprs[1:])

    else:                          # (proc exp*)
        mvs = map(lambda exp: eval(exp, env), x)
        mproc, margs = mvs.pop(0), mvs
        args = seq(margs)
        return bind(mproc, lambda proc: proc(*args))
