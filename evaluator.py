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


def test(env):

    tests = [
        # identity
        ("(+ 2 2)", 4)
        ,("(+ (* 2 100) (* 1 10))", 210)
        ,("(if (> 6 5) (+ 1 1) (+ 2 2))", 2)
        ,("(if (< 6 5) (+ 1 1) (+ 2 2))", 4)
        ,("(quote (testing 1 (2.0) -3.14e159))", ['testing', 1, [2.0], -3.14e159])

        # error
        ,("(assert 1 2)", None)

        # environment
        ,("(define x 3)", None), ("x", 3), ("(+ x x)", 6)
        ,("(begin (define x 1) (set! x (+ x 1)) (+ x 1))", 3)
        ,("((lambda (x) (+ x x)) 5)", 10)
        ,("(define twice (lambda (x) (* 2 x)))", None), ("(twice 5)", 10)
        ,("(define compose (lambda (f g) (lambda (x) (f (g x)))))", None)
        ,("((compose list twice) 5)", [10])
        ,("(define repeat (lambda (f) (compose f f)))", None)
        ,("((repeat twice) 5)", 20)
        #,("((repeat (repeat twice)) 5)", 80)
        ,("(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))", None)
        ,("(fact 3)", 6)
        ,("(fact 50)", 30414093201713378043612608166064768844377641568960512000000000000)
        ,("(define abs (lambda (n) ((if (> n 0) + -) 0 n)))", None)
        ,("(list (abs -3) (abs 0) (abs 3))", [3, 0, 3])
        ,("""(define combine (lambda (f)
        (lambda (x y)
          (if (null? x) (quote ())
              (f (list (car x) (car y))
                 ((combine f) (cdr x) (cdr y)))))))""", None)
        ,("(define zip (combine cons))", None)
        ,("(zip (list 1 2 3 4) (list 5 6 7 8))", [[1, 5], [2, 6], [3, 7], [4, 8]])
        ,("""(define riff-shuffle (lambda (deck) (begin
        (define take (lambda (n seq) (if (<= n 0) (quote ()) (cons (car seq) (take (- n 1) (cdr seq))))))
        (define drop (lambda (n seq) (if (<= n 0) seq (drop (- n 1) (cdr seq)))))
        (define mid (lambda (seq) (/ (length seq) 2)))
        ((combine append) (take (mid deck) deck) (drop (mid deck) deck)))))""", None)
        ,("(riff-shuffle (list 1 2 3 4 5 6 7 8))", [1, 5, 2, 6, 3, 7, 4, 8])
        ,("((repeat riff-shuffle) (list 1 2 3 4 5 6 7 8))",  [1, 3, 5, 7, 2, 4, 6, 8])
        ,("(riff-shuffle (riff-shuffle (riff-shuffle (list 1 2 3 4 5 6 7 8))))", [1,2,3,4,5,6,7,8])
        ]


    from parser import parse
    from repl import to_string


    fails = 0
    for (x, expected) in tests:
        mval = eval(parse(x))
        ival = envRunIn(mval, env) # => ((42, {...}), None)

        val = getVal(ival)
        env = getEnv(ival) # tests share an environment
        succeeded = (val == expected)

        if not succeeded:
            fails += 1
            print x, '=>', to_string(val), getErr(ival)
            print '\tFAIL!!!  Expected', expected

    print '%s %d out of %d tests fail.' % ('*'*45, fails, len(tests))
    return env


if __name__ == '__main__':
    from repl import repl

    env = add_globals({})

    env = test(env)
    repl(env)
