from __future__ import division
import math, operator as op

from evaluator import *
from parser import *


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



def to_string(exp):
    "Convert a Python object back into a Lisp-readable string."
    return '('+' '.join(map(to_string, exp))+')' if isa(exp, list) else str(exp)

def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        val = eval(parse(raw_input(prompt)), global_env)
        if val is not None: print to_string(val)

def test():

    tests = [
        ("(quote (testing 1 (2.0) -3.14e159))", ok(['testing', 1, [2.0], -3.14e159])),
        ("(+ 2 2)", ok(4)),
        ("(+ (* 2 100) (* 1 10))", ok(210)),
        ("(if (> 6 5) (+ 1 1) (+ 2 2))", ok(2)),
        ("(if (< 6 5) (+ 1 1) (+ 2 2))", ok(4)),
        ("(define x 3)", ok(None)), ("x", ok(3)), ("(+ x x)", ok(6)),
        ("(begin (define x 1) (set! x (+ x 1)) (+ x 1))", ok(3)),
        ("((lambda (x) (+ x x)) 5)", ok(10)),
        ("(define twice (lambda (x) (* 2 x)))", ok(None)), ("(twice 5)", ok(10)),
        ("(define compose (lambda (f g) (lambda (x) (f (g x)))))", ok(None)),
        ("((compose list twice) 5)", ok([10])),
        ("(define repeat (lambda (f) (compose f f)))", ok(None)),
        ("((repeat twice) 5)", ok(20)), ("((repeat (repeat twice)) 5)", ok(80)),
        ("(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))", ok(None)),
        ("(fact 3)", ok(6)),
        ("(fact 50)", ok(30414093201713378043612608166064768844377641568960512000000000000)),
        ("(define abs (lambda (n) ((if (> n 0) + -) 0 n)))", ok(None)),
        ("(list (abs -3) (abs 0) (abs 3))", ok([3, 0, 3])),
        ("""(define combine (lambda (f)
        (lambda (x y)
          (if (null? x) (quote ())
              (f (list (car x) (car y))
                 ((combine f) (cdr x) (cdr y)))))))""", ok(None)),
        ("(define zip (combine cons))", ok(None)),
        ("(zip (list 1 2 3 4) (list 5 6 7 8))", ok([[1, 5], [2, 6], [3, 7], [4, 8]])),
        ("""(define riff-shuffle (lambda (deck) (begin
        (define take (lambda (n seq) (if (<= n 0) (quote ()) (cons (car seq) (take (- n 1) (cdr seq))))))
        (define drop (lambda (n seq) (if (<= n 0) seq (drop (- n 1) (cdr seq)))))
        (define mid (lambda (seq) (/ (length seq) 2)))
        ((combine append) (take (mid deck) deck) (drop (mid deck) deck)))))""", ok(None)),
        ("(riff-shuffle (list 1 2 3 4 5 6 7 8))", ok([1, 5, 2, 6, 3, 7, 4, 8])),
        ("((repeat riff-shuffle) (list 1 2 3 4 5 6 7 8))",  ok([1, 3, 5, 7, 2, 4, 6, 8])),
        ("(riff-shuffle (riff-shuffle (riff-shuffle (list 1 2 3 4 5 6 7 8))))", ok([1,2,3,4,5,6,7,8]))
        ,("(assert 1 2)", ok(None))
        ,("(assert 0 2)", err(2))
        ]


    global_env = add_globals(Env())

    fails = 0
    for (x, expected) in tests:
        result = eval(parse(x), global_env)
        succeeded = (result == expected)
        if not succeeded:
            fails += 1
            print x, '=>', to_string(result[0])
            print '\tFAIL!!!  Expected', expected

    print '%s %d out of %d tests fail.' % ('*'*45, fails, len(tests))


if __name__ == '__main__':
    test()
