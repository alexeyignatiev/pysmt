#
# This file is part of pySMT.
#
#   Copyright 2014 Andrea Micheli and Marco Gario
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
from six import StringIO

from pysmt.typing import PartialType, Type, ArrayType
from pysmt.typing import INT, BOOL
from pysmt.test import TestCase, main
from pysmt.smtlib.parser import SmtLibParser
from pysmt.shortcuts import FreshSymbol, EqualsOrIff, Select, TRUE, FALSE
from pysmt.exceptions import PysmtValueError, PysmtTypeError


SMTLIB_SRC="""\
(define-sort Set (T) (Array T Bool))
(define-sort I () Int)

(declare-const s1 (Set I))
(declare-const a I)
(declare-const b Int)

(assert (= (select s1 a) true))
(assert (= (select s1 b) false))
(check-sat)
"""

class TestSorts(TestCase):

    # def test_smtlib_sort(self):
    #     parser = SmtLibParser()
    #     buf = StringIO(SMTLIB_SRC)
    #     script = parser.get_script(buf)
    #     pass


    def test_fake_arrays(self):
        FakeArrayType = Type("FakeArray", 2)
        with self.assertRaises(PysmtValueError):
            FreshSymbol(FakeArrayType)
        FakeArrayII = FakeArrayType(INT, INT)
        self.assertEqual(str(FakeArrayII), "FakeArray(Int, Int)")
        self.assertEqual(FakeArrayII.as_smtlib(False), "(FakeArray Int Int)")
        s = FreshSymbol(FakeArrayII)
        self.assertIsNotNone(s)

    def test_simple_sorts(self):
        # (define-sort I () Int)
        # (define-sort Set (T) (Array T Bool))
        I = INT
        SET = PartialType("Set", lambda t1: ArrayType(t1, BOOL))
        self.assertEqual(ArrayType(INT, BOOL), SET(I))

        # (declare-const s1 (Set I))
        # (declare-const a I)
        # (declare-const b Int)
        s1 = FreshSymbol(SET(I))
        a = FreshSymbol(I)
        b = FreshSymbol(INT)

        # (= (select s1 a) true)
        # (= (select s1 b) false)
        f1 = EqualsOrIff(Select(s1, a), TRUE())
        f2 = EqualsOrIff(Select(s1, b), FALSE())
        self.assertIsNotNone(f1)
        self.assertIsNotNone(f2)

        # Cannot instantiate a PartialType directly:
        with self.assertRaises(PysmtValueError):
            FreshSymbol(SET)

        # (declare-sort A 0)
        # Uninterpreted sort
        A = Type("A", 0)
        B = Type("B")

        c1 = FreshSymbol(A)
        c2 = FreshSymbol(A)
        c3 = FreshSymbol(Type("A"))
        c4 = FreshSymbol(B)
        EqualsOrIff(c1, c2)
        EqualsOrIff(c2, c3)
        with self.assertRaises(PysmtTypeError):
            EqualsOrIff(c1, c4)

        with self.assertRaises(PysmtValueError):
            Type("A", 1)

        C = Type("C", 1)
        c5 = FreshSymbol(C(A))
        c6 = FreshSymbol(C(B))
        self.assertIsNotNone(c5)
        with self.assertRaises(PysmtTypeError):
            EqualsOrIff(c5, c6)

        # Nesting
        ty = C(C(C(C(C(A)))))
        self.assertIsNotNone(FreshSymbol(ty))

        pty = PartialType("pty", lambda S,T: S(S(S(S(S(T))))))
        self.assertEqual(pty(C,A), ty, (pty(C,A).type_id, ty.type_id))







    def test_solving_with_custom_sorts(self):
        # TODO: Move this to solving test
        # self.assertSAT(And(f1, f2))
        pass


if __name__ == '__main__':
    main()