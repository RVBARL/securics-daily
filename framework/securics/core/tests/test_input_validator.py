# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

from unittest import TestCase

from securics.core.InputValidator import InputValidator
import operator


class TestInputValidator(TestCase):

    def test_check_name(self):
        result = InputValidator().check_name('test')
        self.assertEqual(result, True)

        result = InputValidator().check_name('test', '')
        self.assertEqual(result, False)

        result = InputValidator().check_name('?')
        self.assertEqual(result, False)

    def test_check_length(self):
        result = InputValidator().check_length('test')
        self.assertEqual(result, True)

        result = InputValidator().check_length('test', 3)
        self.assertEqual(result, False)

        result = InputValidator().check_length('test', 4, operator.eq)
        self.assertEqual(result, True)

    def test_group(self):
        result = InputValidator().group('test')
        self.assertEqual(result, True)

        result = InputValidator().group(['test1', 'test2'])
        self.assertEqual(result, True)

        result = InputValidator().group('TesT')
        self.assertEqual(result, True)

        result = InputValidator().group(['teSt1', '.test2', '..Test3', '.....'])
        self.assertEqual(result, True)

        result = InputValidator().group(['.'])
        self.assertEqual(result, False)

        result = InputValidator().group(['..'])
        self.assertEqual(result, False)
