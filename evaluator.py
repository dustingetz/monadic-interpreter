from parser import Symbol
from primitives import *
from interp_m import *

# naming conventions in leiu of types:
# 'mv', 'mproc', ... : monadic value in interp_m
# 'x': simple value
# 'xs', 'mvs': lists
# all eval_* functions return monadic values

def eval_symbol(x):
    # immutable environment
    assert x in global_env, "unknown symbol %s"%x
    return ok(global_env[x])

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
    #print m_xs, m_xs({})

    def _apply(proc, args):
        return proc(*args)
    return bind(m_xs, lambda xs: _apply(xs[0], xs[1:]))


def eval(x):
    if isinstance(x, Symbol):
        return eval_symbol(x)
    elif not isinstance(x, list):
        return eval_literal(x)
    elif x[0] == 'quote':
        return eval_quote(x)
    elif x[0] == 'if':             # (if test conseq alt)
        return eval_if(x)
    else:                          # (proc exp*)
        return eval_proc(x)


def test():

    tests = [
        ("(+ 2 2)", 4)
        ,("(+ (* 2 100) (* 1 10))", 210)
        ,("(if (> 6 5) (+ 1 1) (+ 2 2))", 2)
        ,("(if (< 6 5) (+ 1 1) (+ 2 2))", 4)

        ,("(quote (testing 1 (2.0) -3.14e159))", ['testing', 1, [2.0], -3.14e159])

        #,("(assert 1 2)", None)
        #,("(assert 0 2)", err(2))

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
        ]


    from parser import parse
    from repl import to_string

    fails = 0
    for (x, expected) in tests:
        mresult = eval(parse(x))
        val = mresult(global_env)[0] # apply the env and get the result
        succeeded = (val == expected)
        if not succeeded:
            fails += 1
            print x, '=>', to_string(val)
            print '\tFAIL!!!  Expected', expected

    print '%s %d out of %d tests fail.' % ('*'*45, fails, len(tests))


if __name__ == '__main__':
    test()
