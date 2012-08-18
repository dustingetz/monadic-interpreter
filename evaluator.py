from parser import Symbol
from primitives import *

from pymonads.error import error_m, err



interp_m = error_m # cont_t state_t error_t identity_m

ok = interp_m.unit
err = err #needs to be lifted if the monad stack changes
bind = interp_m.bind
fmap = interp_m.fmap
seq = interp_m.seq
mmap = interp_m.map



# here be le monads!

def lift(fn): #lift is a misnomer, its not a real monadic lift. what is it?
    "inlining this fn seems to break python?"
    return lambda *args: ok(fn(*args))

# all eval_* functions are monadic - return mvs

def eval_symbol(x):
    # immutable environment
    assert x in py_primitive_fns, "unknown symbol %s"%x
    return ok(lift(py_primitive_fns[x]))

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

def eval_set(x):
    assert False, "unimplemented: set"
    (_, var, exp) = x
    def _doset(val):
        assert env
        env.find(var)[var] = val
        return None
    return fmap(_doset, eval(exp))

def eval_define(x):
    assert False, "unimplemented: define"
    (_, var, exp) = x
    def _dodefine(val):
        env[var] = val
        return None
    return fmap(_dodefine, eval(exp))

def eval_lambda(x):
    (_, vars, exp) = x
    return err("unimplemented: lambda")
    #return ok(lambda *args: eval(exp, Env(vars, args, env)))


def eval_begin(x):
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
        mfirst = eval(exp)
        if not exprs: return mfirst
        return bind(mfirst, lambda _: _dobegin(exprs[0], exprs[1:]))
    return _dobegin(exprs[0], exprs[1:])

def eval_proc(x):
    mvs = map(eval, x)
    mproc, margs = mvs.pop(0), mvs
    args = seq(margs)
    print mproc, args
    return bind(mproc, lambda proc: proc(*args))





def eval(x):

    if isinstance(x, Symbol):
        return eval_symbol(x)

    elif not isinstance(x, list):
        return eval_literal(x)

    elif x[0] == 'quote':
        return eval_quote(x)

    elif x[0] == 'if':             # (if test conseq alt)
        return eval_if(x)

#    elif x[0] == 'set!':           # (set! var exp)
#        return eval_set(x)

#    elif x[0] == 'define':         # (define var exp)
#        return eval_define(x)

#    elif x[0] == 'lambda':         # (lambda (var*) exp)
#        return eval_lambda(x)

    elif x[0] == 'begin':          # (begin exp*)
        return eval_begin(x)

    else:                          # (proc exp*)
        return eval_proc(x)







def test():

    tests = [
        #("(quote (testing 1 (2.0) -3.14e159))", ok(['testing', 1, [2.0], -3.14e159])),
        ("(+ 2 2)", ok(4)),
        ("(+ (* 2 100) (* 1 10))", ok(210)),
        ("(if (> 6 5) (+ 1 1) (+ 2 2))", ok(2)),
        ("(if (< 6 5) (+ 1 1) (+ 2 2))", ok(4)),
        # ("(define x 3)", ok(None)), ("x", ok(3)), ("(+ x x)", ok(6)),
        # ("(begin (define x 1) (set! x (+ x 1)) (+ x 1))", ok(3)),
        # ("((lambda (x) (+ x x)) 5)", ok(10)),
        # ("(define twice (lambda (x) (* 2 x)))", ok(None)), ("(twice 5)", ok(10)),
        # ("(define compose (lambda (f g) (lambda (x) (f (g x)))))", ok(None)),
        # ("((compose list twice) 5)", ok([10])),
        # ("(define repeat (lambda (f) (compose f f)))", ok(None)),
        # ("((repeat twice) 5)", ok(20)), ("((repeat (repeat twice)) 5)", ok(80)),
        # ("(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))", ok(None)),
        # ("(fact 3)", ok(6)),
        # ("(fact 50)", ok(30414093201713378043612608166064768844377641568960512000000000000)),
        # ("(define abs (lambda (n) ((if (> n 0) + -) 0 n)))", ok(None)),
        # ("(list (abs -3) (abs 0) (abs 3))", ok([3, 0, 3])),
        # ("""(define combine (lambda (f)
        # (lambda (x y)
        #   (if (null? x) (quote ())
        #       (f (list (car x) (car y))
        #          ((combine f) (cdr x) (cdr y)))))))""", ok(None)),
        # ("(define zip (combine cons))", ok(None)),
        # ("(zip (list 1 2 3 4) (list 5 6 7 8))", ok([[1, 5], [2, 6], [3, 7], [4, 8]])),
        # ("""(define riff-shuffle (lambda (deck) (begin
        # (define take (lambda (n seq) (if (<= n 0) (quote ()) (cons (car seq) (take (- n 1) (cdr seq))))))
        # (define drop (lambda (n seq) (if (<= n 0) seq (drop (- n 1) (cdr seq)))))
        # (define mid (lambda (seq) (/ (length seq) 2)))
        # ((combine append) (take (mid deck) deck) (drop (mid deck) deck)))))""", ok(None)),
        # ("(riff-shuffle (list 1 2 3 4 5 6 7 8))", ok([1, 5, 2, 6, 3, 7, 4, 8])),
        # ("((repeat riff-shuffle) (list 1 2 3 4 5 6 7 8))",  ok([1, 3, 5, 7, 2, 4, 6, 8])),
        # ("(riff-shuffle (riff-shuffle (riff-shuffle (list 1 2 3 4 5 6 7 8))))", ok([1,2,3,4,5,6,7,8]))
        # ,("(assert 1 2)", ok(None))
        # ,("(assert 0 2)", err(2))
        ]


    from parser import parse
    #global_env = add_globals(Env())

    fails = 0
    for (x, expected) in tests:
        result = eval(parse(x))
        succeeded = (result == expected)
        if not succeeded:
            fails += 1
            print x, '=>', to_string(result[0])
            print '\tFAIL!!!  Expected', expected

    print '%s %d out of %d tests fail.' % ('*'*45, fails, len(tests))


if __name__ == '__main__':
    test()
