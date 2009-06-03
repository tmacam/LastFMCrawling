#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for retrievers for LastFM resources."""

__version__ = "0.4.lastfm-" + "$Revision$".split()[1]
__date__ = "2008-11-17"
__author__ = "Tiago Alves Macambira & Rafael Sachetto"
__copyright__ = "Copyright (c) 2006-2008 Tiago Alves Macambira"
__license__ = "X11"

import datetime
import time
import unittest
from retrievers import UserInfoRetriever, GroupRetrievers, ObstinatedRetriever,\
TracksRetriever, LibrarySnapshotsRetriever, get_protobuffered_profile,\
lastfm_pb2


######################################################################
# Helper Classes
######################################################################


class FakeRetrievers(ObstinatedRetriever):
    """A class that behave like a ObstinatedRetriever but that only returns
    a pre-defined input.
    """
    def __init__(self, data):
        """Constructor.
        
        Args:
            data: Data to be returned by get_url.
        """
        self.fake_data = data

    def get_url(self, *args, **kargs):
        """Mocked or faked get_url."""
        self.validate(self.fake_data)
        return self.fake_data


# TIP: Method resolution w/ multiple inheritance is from left, to right


class FakeGroupRetrievers(FakeRetrievers, GroupRetrievers):
    pass


class FakeUserInfoRetriever(FakeRetrievers, UserInfoRetriever):
    pass

class FakeTracksRetrievers(FakeRetrievers, TracksRetriever):
    pass


class FakeLibrarySnapshotRetrievers(FakeRetrievers, LibrarySnapshotsRetriever):
    pass


######################################################################
# Test Cases
######################################################################


class UserInfoRetrieverTest(unittest.TestCase):
    PROFILE_NO_NOTHING = "retrievers_test_profile_1.data"
    PROFILE_AGE_GENDER = "retrievers_test_profile_2.data"
    PROFILE_GENDER_NO_AGE = "retrievers_test_profile_3.data"
    PROFILE_NO_GENDER_AGE = "retrievers_test_profile_4.data"
    PROFILE_NO_USER_INFO = "retrievers_test_profile_5.data"
    PROFILE_NO_EXECUTION = "retrievers_test_profile_6.data"
    PROFILE_RESETED = "retrievers_test_profile_7.data"
    PROFILE_EMPTYHOMEPAGE = "retrievers_test_profile_8.data"
    PROFILE_STAFFPROFILE = "retrievers_test_profile_9.data"
    PROFILE_MODERATORPROFILE =  "retrievers_test_profile_10.data"


    def testProfileWithoutGenderAndAge(self):
        "Tests if we get information from a profile w/o Gender and Gender."
        data = open(self.PROFILE_NO_NOTHING, 'r')
        username = "kalleke"
        expected =  (username, '', '', '', '', '1073', '1', '', '2006-05-15')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)

    def testProtobufferedProfileWithoutGenderAndAge(self):
        "Tests if we get information from a profile w/o Gender and Gender."
        data = open(self.PROFILE_NO_NOTHING, 'r')
        username = "kalleke"       

        userdata = UserInfoRetriever().parse_user_data(username, data)
    
        fake_data = {"info" : userdata, "groups" : (), "friends" : (), "tracks" : ()}

        serialized = get_protobuffered_profile(fake_data)

        user = lastfm_pb2.User()
        user.ParseFromString(serialized)

        self.assertEqual(user.username, username)
        self.assertEqual(user.executions, 1073)
        self.assertEqual(user.average, 1)
        self.assertEqual(user.userSince, '2006-05-15')


    def testProfileWithAgeAndGender(self):
        "Tests if we get information from a profile w/ Age and Gender."
        data = open(self.PROFILE_AGE_GENDER, 'r')
        username = "tmacam"
        expected =  (username, 'Tiago Macambira', '27', 'Masculino',
                'Brasil', '10775', '16', 'www.burocrata.org', '2007-03-22')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)

    def testProtobufferdProfileWithAgeAndGender(self):
        "Tests if we get information from a profile w/ Age and Gender."

        data = open(self.PROFILE_AGE_GENDER, 'r')
        username = "tmacam"

        userdata = UserInfoRetriever().parse_user_data(username, data)
    
        fake_data = {"info" : userdata, "groups" : (), "friends" : (), "tracks" : ()}

        serialized = get_protobuffered_profile(fake_data)

        user = lastfm_pb2.User()
        user.ParseFromString(serialized)

        self.assertEqual(user.username, username)
        self.assertEqual(user.name, 'Tiago Macambira')
        self.assertEqual(user.age, 27)
        self.assertEqual(user.gender, lastfm_pb2.User.MALE)
        self.assertEqual(user.country, 'Brasil')
        self.assertEqual(user.executions, 10775)
        self.assertEqual(user.average, 16)
        self.assertEqual(user.homepage, 'www.burocrata.org')
        self.assertEqual(user.userSince, '2007-03-22')
        self.assertFalse(user.HasField('resetedDate'))

    def testProfileWithtGenderButNoAge(self):
        "Tests if we get information from a profile w/ Gender but w/o Age."
        data = open(self.PROFILE_GENDER_NO_AGE, 'r')
        username = "susan"
        expected = (username, 'Susan', '', 'Feminino', '', '22', '0', '',
                    '2002-10-29', '2007-06-16')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)

    def testProtubufferedProfileWithtGenderButNoAge(self):
        "Tests if we get information from a profile w/ Gender but w/o Age."
        data = open(self.PROFILE_GENDER_NO_AGE, 'r')
        username = 'susan' 
        expected = (username, 'Susan', '', 'Feminino', '', '22', '0', '',
                    '2002-10-29', '2007-06-16')

        userdata = UserInfoRetriever().parse_user_data(username, data)
    
        fake_data = {"info" : userdata,
                     "groups" : (),
                     "friends" : (),
                     "tracks" : ()}

        serialized = get_protobuffered_profile(fake_data)

        user = lastfm_pb2.User()
        user.ParseFromString(serialized)

        self.assertEqual(user.username, username)
        self.assertEqual(user.name, 'Susan')
        self.assertFalse(user.HasField('country'))
        self.assertEqual(user.gender, lastfm_pb2.User.FEMALE)
        self.assertFalse(user.HasField('age'))
        self.assertEqual(user.executions, 22)
        self.assertEqual(user.average, 0)
        self.assertFalse(user.HasField('homepage'))
        self.assertEqual(user.userSince, '2002-10-29')
        self.assertEqual(user.resetedDate, '2007-06-16')


    def testProfileWithAgeButNoGender(self):
        "Tests if we get information from a profile w/ Age but no Gender."
        data = open(self.PROFILE_NO_GENDER_AGE, 'r')
        username = "xadai"
        expected =  (username, 'Pedro Marques', '22', '', 'Brasil', '38158',
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

    def testEmptyHomepage(self):
        "Tests if we correctly handle profiles w/ empty homepage"
        data = open(self.PROFILE_EMPTYHOMEPAGE, 'r')
        username = "supersupercri"
        expected =  (username, 'Cristina', '23', 'Feminino', 'Itália',
                     '140', '1', '', '2008-09-18')
        returned = UserInfoRetriever().parse_user_data(username, data)
        self.assertEqual(expected, returned)

    def testStaffProfile(self):
        "Tests if we correctly recognize valid page as valid"
        fake_data = open(self.PROFILE_STAFFPROFILE, 'r').read()
        retriever = FakeUserInfoRetriever(fake_data)
        username = "hannahdonovan"
        expected =  (username, 'Hannah Donovan', '', 'Feminino', 'Reino Unido',
                     '29583', '21', '', '2005-03-03')
        returned = retriever.get_user(username)
        self.assertEqual(expected, returned)

    def testModeratorProfile(self):
        "Tests if this page is a Moderator profile"
        fake_data = open(self.PROFILE_MODERATORPROFILE, 'r').read()
        retriever = FakeUserInfoRetriever(fake_data)
        username = "Kerensky97"
        expected =  (username, 'Joe Mama', '28', 'Masculino', 'Estados Unidos',
                     '75825', '59', '', '2005-06-30', '2005-07-24')
        returned = retriever.get_user(username)
        self.assertEqual(expected, returned)


class GroupRetrieverTest(unittest.TestCase):
    GROUP_DATA_EMPTY_GROUP = "retrievers_test_groups_1.data"

    def testEmptyGroup(self):
        "Tests if we correctly ignore 'empty' groups."
        fake_data = open(self.GROUP_DATA_EMPTY_GROUP, 'r').read()
        retriever = FakeGroupRetrievers(fake_data)
        returned = retriever.get_user_groups("FakeGroupRetrieversDontCare")
        expected = [u"New Order"]
        self.assertEqual(expected, returned)


class TracksRetrieverTest(unittest.TestCase):
    TRACK_DATA_ACCENTED = "retrievers_test_tracks_1.data"

    def testTracksWithAccentedData(self):
        "Tests if we correctly handle data outside the ASCII range."
        fake_data = open(self.TRACK_DATA_ACCENTED, 'r').read()
        retriever = FakeTracksRetrievers(fake_data)
        returned = retriever.get_tracks("FakeTracksRetrievers don't care")
        expected = (u'Adriana Calcanhotto', u'Mar\xe9', 1)
        self.assertEqual(expected, returned[0])


class LibrarySnapshotsRetrieverTest(unittest.TestCase):
    LIBRARY_DATA_1 = "retrievers_test_library_1.data"
    EMPTY_LIBRARY_DATA = "retrievers_test_library_2.data"
    LIBRARY_DATA_1_LEN_FULL = 50
    LIBRARY_DATA_1_LEN_DAY_1 = 50, time.mktime(datetime.date(2009, 05, 27).timetuple())
    LIBRARY_DATA_1_LEN_DAY_2 = 42, time.mktime(datetime.date(2009, 05, 28).timetuple())
    LIBRARY_DATA_1_LEN_DAY_END = 0, time.mktime(datetime.date(2009, 05, 30).timetuple())
    LIBRARY_DATA_1_LEN_DAY_END_PLUS_ONE = time.mktime(datetime.date(2009, 05, 31).timetuple())

    def testParseDateTimeWrongFormat(self):
        retriever = LibrarySnapshotsRetriever()
        date_time_str = "20090531 T 06:32:54 lakjdkjasdkladjZ"
        self.assertRaises(ValueError,
                LibrarySnapshotsRetriever.parse_date_time,
                retriever,
                date_time_str)

    def testParseDateTimeMissingZ(self):
        retriever = LibrarySnapshotsRetriever()
        date_time_str = "2009-05-31T06:32:54"
        self.assertRaises(AssertionError,
                LibrarySnapshotsRetriever.parse_date_time,
                retriever,
                date_time_str)

    def testParseDateTimeOKStr(self):
        retriever = LibrarySnapshotsRetriever()
        date_time_str = "2009-05-31T06:32:54Z"
        expected = (2009, 05, 31, 06, 32, 54)
        returned = retriever.parse_date_time(date_time_str)
        self.assertEqual(expected, returned)

    def testFullLibraryDownload(self):
        day_one = LibrarySnapshotsRetriever.DAY_ONE
        fake_data = open(self.LIBRARY_DATA_1, 'r').read()
        retriever = FakeLibrarySnapshotRetrievers(fake_data)
        ret_lib, ret_date = retriever.get_library('dontcare', day_one,
                today = self.LIBRARY_DATA_1_LEN_DAY_END_PLUS_ONE)
        self.assert_(self.LIBRARY_DATA_1_LEN_FULL, len(ret_lib))

        # don't return anything if "today" is the smallest date in lib.
        _, exp_date = self.LIBRARY_DATA_1_LEN_DAY_1
        ret_lib, ret_date = retriever.get_library('dontcare', exp_date,
                                                  today=exp_date)
        self.assertEqual(0, len(ret_lib))
        self.assertEqual(exp_date, ret_date)

        # Ok, suppose we had already done a download of this library
        # and that there was some musics listened just today in the collection
        exp_len, exp_date = self.LIBRARY_DATA_1_LEN_DAY_2
        end_len, end_date = self.LIBRARY_DATA_1_LEN_DAY_END
        ret_lib, ret_date = retriever.get_library('dontcare', exp_date,
                today=end_date)
        self.assertEqual(34, len(ret_lib))
        self.assertEqual(end_date, ret_date)

    def testEmptyLibraryDownload(self):
        day_one = LibrarySnapshotsRetriever.DAY_ONE
        fake_data = open(self.EMPTY_LIBRARY_DATA, 'r').read()
        retriever = FakeLibrarySnapshotRetrievers(fake_data)
        ret_lib, ret_date = retriever.get_library('dontcare', day_one)
        self.assertEqual([], ret_lib)


if __name__ == '__main__':
    unittest.main()

# vim: set ai tw=80 et sw=4 sts=4 fileencoding=utf-8 :
