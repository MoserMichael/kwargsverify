#!/usr/bin/env python3
import os
import unittest
import sys
import kwchecker


class Test(unittest.TestCase):
    def setUp(self):
        sys.stdout.flush()
        print("\n*** testing: ", self._testMethodName, "***\n")
        sys.stdout.flush()

    def tearDown(self):
        sys.stdout.flush()

    def test_validate(self):
        def func_to_test(**kwargs):
            checker = kwchecker.KwArgsChecker(
                required={"req_email": kwchecker.email_validator()},
                opt={"opt_str": str},
            )
            checker.validate(**kwargs)

        error_text = ""
        try:
            func_to_test()
        except ValueError as error:
            error_text = str(error)

        self.assertEqual(
            error_text, "Error: required parameter req_email is not passed as parameter"
        )

        try:
            func_to_test(req_email="not-an-email")
        except ValueError as error:
            error_text = str(error)

        self.assertEqual(error_text, "Error: parameter req_email is not a valid email")

        error_text = ""
        try:
            func_to_test(req_email="blabla@gmail.com", opt_str=[1, 2, 3])
        except ValueError as error:
            error_text = str(error)

        self.assertEqual(
            error_text, "Error: parameter opt_str not of expected type <class 'str'>"
        )

        error_text = ""
        try:
            func_to_test(req_email="blabla@gmail.com", undefined_param=42)
        except ValueError as error:
            error_text = str(error)

        self.assertEqual(
            error_text, "Error: parameter name undefined_param is not defined"
        )

        error_text = ""
        try:
            func_to_test(req_email="blabla@gmail.com", opt_str="blabla")
        except ValueError as error:
            error_text = str(error)
        self.assertEqual(error_text, "")

    def test_regex(self):
        def func_to_test_regex(**kwargs):
            checker = kwchecker.KwArgsChecker(
                required={
                    "no_spaces": (
                        str,
                        kwchecker.no_regex_validator(
                            r".*\s+$", "no trailing whitespaces allowed"
                        ),
                        kwchecker.no_regex_validator(
                            r"^\s+", "no leading whitespaces allowed"
                        ),
                    ),
                }
            )
            checker.validate(**kwargs)

        func_to_test_regex(no_spaces="no-leading-and-trailing-spaces")
        
        error_text = ""
        try:
            func_to_test_regex(no_spaces="    leading tab")
        except ValueError as error:
            error_text = str(error)
        self.assertEqual(
            error_text, "Error: no leading whitespaces allowed"
        )

        error_text = ""
        try:
            func_to_test_regex(no_spaces="trailing spaces \t")
        except ValueError as error:
            error_text = str(error)
        self.assertEqual(
            error_text, "Error: no trailing whitespaces allowed"
        )


if __name__ == "__main__":
    # unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
    print("*** eof test ***")
