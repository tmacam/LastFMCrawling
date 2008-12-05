#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for retrievers for LastFM resources."""

__version__ = "0.4.lastfm-" + "$Revision$".split()[1]
__date__ = "2008-11-17"
__author__ = "Tiago Alves Macambira & Rafael Sachetto"
__copyright__ = "Copyright (c) 2006-2008 Tiago Alves Macambira"
__license__ = "X11"

import unittest
from retrievers import UserInfoRetriever

class UserInfoRetrieverTest(unittest.TestCase):
    PROFILE_NO_NOTHING = "retrievers_test_profile_1.data"
    PROFILE_AGE_GENDER = "retrievers_test_profile_2.data"
    PROFILE_GENDER_NO_AGE = "retrievers_test_profile_3.data"
    PROFILE_NO_GENDER_AGE = "retrievers_test_profile_4.data"
    PROFILE_NO_USER_INFO = "retrievers_test_profile_5.data"
    PROFILE_NO_EXECUTION = "retrievers_test_profile_6.data"
    PROFILE_RESETED = "retrievers_test_profile_7.data"

    def testProfileWithoutGenderAndAge(self):
        "Tests if we get information from a profile w/o Gender and Gender."
        data = open(self.PROFILE_NO_NOTHING, 'r')
        username = "kalleke"
        expected =  (username, '', '', '', '', '1073', '1', '', '2006-05-15')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)

    def testProfileWithAgeAndGender(self):
        "Tests if we get information from a profile w/ Age and Gender."
        data = open(self.PROFILE_AGE_GENDER, 'r')
        username = "tmacam"
        expected =  (username, 'Tiago Macambira', '27', 'Masculino',
                'Brasil', '9320', '15', 'www.burocrata.org', '2007-03-22')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)

    def testProfileWithtGenderButNoAge(self):
        "Tests if we get information from a profile w/ Gender but w/o Age."
        data = open(self.PROFILE_GENDER_NO_AGE, 'r')
        username = "susan"
        expected = (username, 'Susan', '', 'Feminino', '', '22', '0', '',
                    '2002-10-29')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)

    def testProfileWithAgeButNoGender(self):
        "Tests if we get information from a profile w/ Age but no Gender."
        data = open(self.PROFILE_NO_GENDER_AGE, 'r')
        username = "xadai"
        expected =  (username, 'Pedro Marques', '21', '', 'Brasil', '36639',
                '23', 'pedroxadai.blogspot.com', '2004-08-08')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)

    def testProfileWithoutUserInfo(self):
        "Tests if we get information from a profile w/o user-info"
        data = open(self.PROFILE_NO_USER_INFO, 'r')
        username = "sensimilla88"
        expected =  (username, '', '', '', '', '86', '0', '', '2006-11-28')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)

    def testResetedProfile(self):
        "Tests if we correctly handle profiles w/ reseted execution data"
        data = open(self.PROFILE_RESETED, 'r')
        username = "Fargaroth"
        expected =  (username, 'Faruk', '21', 'Masculino', 'Turquia',
                     '', '0', 'fargaroth.deviantart.com',
                     '2006-02-27', '2008-02-05')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)



if __name__ == '__main__':
    unittest.main()

# vim: set ai tw=80 et sw=4 sts=4 fileencoding=utf-8 :
