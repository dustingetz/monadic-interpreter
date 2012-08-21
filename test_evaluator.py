import unittest

from evaluator import eval
from parser import parse
from repl import Repl
from interp_m import *


def keydiff(dict1, dict2):
    return set(dict1).difference(set(dict2))


class TestEvaluator(unittest.TestCase):

    def setUp(self):
        # multiple forms in a single test share mutable global env
        self.r = Repl()

    def checkForm(self, form, expected):
        ival = self.r.evalForm(form)
        self.assertTrue(getVal(ival) == expected)

    def checkForms(self, tests):
        checkForm = self.checkForm
        map(lambda t: checkForm(t[0], t[1]), tests)


    def test_identity(self):
        tests = [
            ("(+ 2 2)", 4)
            ,("(+ (* 2 100) (* 1 10))", 210)
            ,("(if (> 6 5) (+ 1 1) (+ 2 2))", 2)
            ,("(if (< 6 5) (+ 1 1) (+ 2 2))", 4)
            ,("(quote (testing 1 (2.0) -3.14e159))", ['testing', 1, [2.0], -3.14e159])
            ]
        self.checkForms(tests)

    def test_error(self):
        self.checkForm("(assert 1 2)", None)

    def test_env(self):
        tests = [
            ("(define x 3)", None), ("x", 3), ("(+ x x)", 6)
            ,("(begin (define x 1) (set! x (+ x 1)) (+ x 1))", 3)
            ,("((lambda (x) (+ x x)) 5)", 10)
            ,("(define twice (lambda (x) (* 2 x)))", None), ("(twice 5)", 10)
            ,("(define compose (lambda (f g) (lambda (x) (f (g x)))))", None)
            ,("((compose list twice) 5)", [10])
            ,("(define repeat (lambda (f) (compose f f)))", None)
            ,("((repeat twice) 5)", 20)
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

        self.checkForms(tests)

    def test_regression_1(self):
        "this blows the stack. don't know why."
        self.r.evalForm("(define twice (lambda (x) (* 2 x)))")
        self.r.evalForm("(define compose (lambda (f g) (lambda (x) (f (g x)))))")
        self.r.evalForm("(define repeat (lambda (f) (compose f f)))")
        try:
            self.r.evalForm("((repeat (repeat twice)) 5)")
        except RuntimeError, why:
            self.fail(why)

    def test_stack_frames(self):
        envA = self.r.env
        ival = self.r.evalForm("((lambda (a1) (* 2 a1)) 5)")
        envB = self.r.env
        self.assertEqual(keydiff(envB, envA), set([]), "stack not unwound")

    def test_define(self):
        envA = self.r.env
        self.r.evalForm("(define f (lambda (a1) (* 2 a1)))")
        self.r.evalForm("(define x 3)")
        self.r.evalForm("(define y (+ 1 x))")
        envB = self.r.env
        self.assertEqual(keydiff(envB, envA), set(['f', 'x', 'y']))

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestEvaluator))

if __name__=="__main__":
    unittest.main(exit=False)
