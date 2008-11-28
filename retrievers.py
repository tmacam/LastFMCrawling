#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Retrievers for LastFM resources."""

__version__ = "0.4.lastfm-" + "$Revision$".split()[1]
__date__ = "2008-11-17"
__author__ = "Tiago Alves Macambira & Rafael Sachetto"
__copyright__ = "Copyright (c) 2006-2008 Tiago Alves Macambira"
__license__ = "X11"


import re
import datetime
import urllib2
import httplib
import logging
import cPickle
import zlib
from socket import gethostname
from DistributedCrawler.client.BeautifulSoup import BeautifulSoup, \
        BeautifulStoneSoup
from common import FINDUSERS_VALID_GENDERS, FINDUSERS_SEPARATOR, \
        FINDUSERS_PAGE_COUNT, FINDUSERS_URL_TEMPLATE


# FIXME add logging information through retrievers


######################################################################
# CONSTANTS
######################################################################


APIKEY = "f4ddd94913e516288a1ede7fa75f9bd5"

MONTHS_TO_NUM = {'Jan':1, 'Fev':2, 'Mar':3, 'Abr':4, 'Mai':5, 'Jun':6, 'Jul':7, 'Ago':8, 'Set':9, 'Out':10, 'Nov':11, 'Dez':12}


######################################################################
# AUX. CLASSES
######################################################################


def takeComma(name):
    if name.endswith(","):
        return name[:-1]
    else:
        return name

class InvalidPage(Exception):
    """Used by ObstinatedRetriever to notify that a given page has not
    passed (some) sanity test.
    """
    pass


class ObstinatedRetriever(object):
    """A simple downloader that "Never give up, never surrender[s]".

    Download a page and validate it's content's. If any of those fail, tries
    again for MAX_RETRIES.

    Descendents SHOULD re-implement validate().
    """
    # FIXME Should Deal with retries, validation, compression
    #       and appearing as valid client. 
    # FIXME  We should refactor this into or onto ArticleRetriver

    MAX_RETRIES = 5

    def validate(self, data):
        """Verifies if a download page has the right content.
        
        Args:
            data: download content, as a string. No assumption is made
                about the nature of such content such as whether it is HTML or
                binary data.

        Returns:
            None

        Raises:
            Raises InvalidPage if the content is not valid.
        """
        pass

    def get_url(self, url):
        """Retrieves the content of the URL url IFF it is valid.
        
        At least MAX_RETRIES are done if the download or if the content
        of the page is found not to be valid.

        Returns:
            The content of the URL as a string.

        Raises:
            Can raise InvalidPage and any exception raised by
            urllib2.urlopen().
        """
        retries = 0
        while True:
            try:
                retries += 1
                request = urllib2.urlopen(url)
                logging.debug("get_url : %s", url)
                page = request.read()
                self.validate(page)
                return page
            except (InvalidPage, urllib2.URLError, urllib2.HTTPError,
                    ValueError, httplib.HTTPException):
                logging.info("Error getting url, retring.")
                if retries > self.MAX_RETRIES:
                    raise


######################################################################
# LASTFM-SPECIFIC RETRIEVERS
######################################################################

class PageNotFound(Exception):
    """LastFM returned with 404. This may mean user expelled, not found etc"""

class FindUsersRetriver(ObstinatedRetriever):
    "Retrieves users from LastFM's User Search page."

    def validate(self, page):
        "Check if this search result has any user at all."
        soup = BeautifulSoup(page)
        try:
            users_vcards = soup.find("ul", "usersMedium").findAll("div","vcard")
            users = [vcard.a['href'].split('/')[-1] for vcard in users_vcards]
            if not users:
                raise InvalidPage()
        except:
            raise InvalidPage()

    def get_users_from_search_page(self, sex, page):
        "Returns a list whith the users found in a search page."
        page_url = FINDUSERS_URL_TEMPLATE % (sex, page)
        data = self.get_url(page_url)
        soup = BeautifulSoup(data)
        # Each user has a vcard whose first and only Anchor tag is a
        # link for the user profile in LastFM, in the form
        # http://www.lastfm.com.br/user/USERNAME. All we want is the USERNAME
        # part of such links.
        users_vcards = soup.find("ul", "usersMedium").findAll("div","vcard")
        users = [vcard.a['href'].split('/')[-1] for vcard in users_vcards]
        return users

    def get_users_from_pages(self, sex, start_page):
        """Get the list of users from a range search pages.
        
        Get the users from FINDUSERS_PAGE_COUNT user search pages,
        starting at start_page.

        Returns:
            a set with the users found.
        """
        found_users = set()
        for page in range(start_page, start_page + FINDUSERS_PAGE_COUNT):
            for user in self.get_users_from_search_page(sex, page):
                found_users.add(user.strip())
        return found_users

class GroupRetrievers(ObstinatedRetriever):
    """Groups are returned percent-encoded."""

    GROUP_URL_TEMPLATE = 'http://www.last.fm/user/%s/groups?groupspage=%i'
    
    def validate(self, data):
        soup = BeautifulSoup(data)
        if not soup.find('div','skyWrap'):
            raise InvalidPage()

    def get_user_groups(self, user):
        cur_page = 1
        lastpage = 1
        groups = []
        log = logging.getLogger("GroupRetrievers")
        # the usernames were extracted from the anchor tags from the
        # user search html pages -- those usernames are already
        # percent-encoded.
        while cur_page <= lastpage:
            log.info("Retrieving page %i of %i", cur_page, lastpage)
            url = self.GROUP_URL_TEMPLATE % (user, cur_page)
            data = self.get_url(url)
            soup = BeautifulSoup(data)
            groups_html = soup.findAll("div","groupContainer")
            if groups_html:
                for group in groups_html:
                    group_name = group.find("a")['href'].split('/')[-1]
                    groups.append(group_name.encode("utf-8"))
                # Group information can be splited across several pages
                # Get the number of pages
                if cur_page == 1:
                    last_page_html = soup.find("a", "lastpage")
                    if last_page_html:
                        lastpage = int(last_page_html.contents[0])
                    else:
                        lastpage = 1
            cur_page += 1
        return groups


class TracksRetriever(ObstinatedRetriever):
    """Track information is returned percent-encoded.
    
    Track listings are returned as list of (artist, track name, playcount)
    tuples.
    """

    GET_TRACKS_URL_TEMPLATE = "http://ws.audioscrobbler.com/2.0/?user=%s&method=library.gettracks&api_key=%s&page=%i"

    def validate(self, data):
        if not BeautifulStoneSoup(data).find("tracks"):
            raise InvalidPage()


    def get_tracks(self, user):
        cur_page = 1
        lastpage = 1
        track_list = []
        log = logging.getLogger("TracksRetriever")

        while cur_page <= lastpage:
            log.info("Retrieving page %i of %i", cur_page, lastpage)
            url = self.GET_TRACKS_URL_TEMPLATE % (user, APIKEY, cur_page)
            xml = self.get_url(url)
            soup = BeautifulStoneSoup(xml).find("tracks")
            tracks = soup.findAll("track")

            for track in tracks:
                playcount = int(track.find("playcount").contents[0])
                # LastFM are percent encoded, no need to encode to UTF-8
                track_url = str(track.find("url").contents[0])
                artist, _, name = track_url.split("/")[-3:]
                track_list.append((artist, name, playcount))
            # Track information can be splitted across several pages.
            # Get the number of pages.
            if cur_page == 1:
                lastpage = int(soup.attrs[-1][1])

            cur_page += 1

        # Sort the list in-place -- just in case, and to help compression
        track_list.sort()

        return track_list


class FriendsRetriever(ObstinatedRetriever):
    """Friendship information is returned percent-encoded."""

    GET_USER_FRIENDS_TEMPLATE = 'http://ws.audioscrobbler.com/2.0/?method=user.getfriends&user=%s&api_key=%s'

    def validate(self, data):
        if not BeautifulStoneSoup(data).find("friends"):
            raise InvalidPage()

    def get_friends(self, user):
        friends_list = []
        log = logging.getLogger("FriendsRetriever")
        log.info("Retrieving friends list.")

        url = self.GET_USER_FRIENDS_TEMPLATE % (user, APIKEY)
        xml = self.get_url(url)
        soup = BeautifulStoneSoup(xml)

        friends_urls = soup.findAll("url")

        for f_url in friends_urls:
            friend_name = f_url.contents[0].split("/")[-1]
            friends_list.append(friend_name.encode("utf8"))

        return friends_list


class UserInfoRetriever(ObstinatedRetriever):
    """    
    User info is returned as a tuple (username, name, age, sex, country,
    executions, average, homepage, user_since ).

    Strings are returned percent-encoded in plain ASCII.
    """

    USER_URL_TEMPLATE = "http://www.lastfm.com.br/user/%s/"

    AGE_GENDER_RE = re.compile(r"(\d+)?\s*(M\w+|F\w+)?")

    def validate(self, data):
        soup = BeautifulSoup(data)
        if not soup.find('div', 'clearit user vcard') and \
           not soup.find('div', 'clearit subscriber vcard'):
            raise InvalidPage()

    def get_user(self, username):
        "Get the parsed user profile page."
        url = self.USER_URL_TEMPLATE % (username)
        try:
            html = self.get_url(url)
        except urllib2.HTTPError, e:
            if e.code == 404:
                page = BeautifulSoup(e.read())
                text = ""
                try:
                    text = str(page.find("div",{"id":"fourOhFour"}).h1)
                except:
                    pass
                raise PageNotFound(text)
            else:
                # Propagate original error
                raise
        return self.parse_user_data(username, html)

    

    def parse_user_data(self,username, data):
        "Parse the user profile page."
        soup = BeautifulSoup(data)

        log = logging.getLogger("UserInfoRetriever")
        log.info("BEGIN")

        details = soup.find('div', 'clearit user vcard')

        if not details:
            details = soup.find('div', 'clearit subscriber vcard')
        if not details:
            raise InvalidPage() # we should NOT get here 'cuz of validate

        # User's name
        name = ""
        try:
            name = details.find('strong', 'fn').contents[0]
        except AttributeError:
            pass

        # get html code with the average play count, user since 
        # and total executions informations
        details_html = details.find('span', 'userPlays') 

        # average play count per day
        average = details_html.attrs[1][1].split()[2] 

        # User since... (user_since)
        if details_html.find('small'):
            # Usuário já escutou alguma coisa...
            # desde dd mon YYYY
            day_month_year_text = details_html.find('small').contents[0]
        else:
            # Usuário apenas se registrou, nao postou nenhuma música
            # Registrado em: dd mon YYYY
            day_month_year_text = details_html.contents[0]
        # Get only the "dd mon YYYY"
        day_text, month_text, year_text = day_month_year_text.split()[-3:]
        day = int(day_text)
        month = int(MONTHS_TO_NUM[month_text])
        year = int(year_text)
        user_since = datetime.date(year, month, day).isoformat()

        # Executions
        flips = details_html.findAll('span', 'flip')
        digits = []
        for d in flips:
            digits.append(d.contents[0])
        executions = "".join(digits)

        # Homepage
        homepage = ""
        homepage_html = details.find('a', 'url homepage')
        if homepage_html:
            homepage = homepage_html.contents[0]

        # Get user info -- Country, Age, Gender
        country, age, gender = "", "", ""
        extra_details = details.find("p", "userInfo adr")
        if extra_details:
            # Country
            country = ''
            country_html = extra_details.find("span", "country-name")
            if country_html:
                country = country_html.contents[0]
            # Gender and age -- Remove all children tags - get only gender
            # and age text, if it exists
            # NOTICE: this modifies the page structure,
            #         should be the last step...
            for child in extra_details.findAll():
                child.extract()
            if extra_details.contents:
                # Get gender and age using regular expressions...
                gender_age_text = extra_details.contents[0]
                gender_age_text = gender_age_text.replace(",", "").strip()
                res = self.AGE_GENDER_RE.match(gender_age_text)
                age, gender = res.groups()
                if not gender:
                    gender = ""
                if not age:
                    age = ""

        # convert everything to plain strings -- every "odd" data is percent
        # encoded...
        log.info("END")
        res = (username, name, age, gender, country, executions, average,
                homepage, user_since )
        return tuple([str(i) for i in res])


def retrieve_full_user_profile(username):
    """Get the full user profile from a LastFM user.
    
    Returns:
        a dict contaning each of the aspects we are interested on of the user's
        profile
    """
    # We are not performing "retries" here as this is done for more
    # then enought times by each of the specialized retrievers
    info = UserInfoRetriever().get_user(username)
    groups = GroupRetrievers().get_user_groups(username)
    friends = FriendsRetriever().get_friends(username)
    tracks = TracksRetriever().get_tracks(username)

    return {"info" : info, "groups" : groups, "friends" : friends,
            "tracks" : tracks}


def get_user_encoded_profile(username):
    """Get the full user profile information serialized and compressed.

    The returned user profile data will be in a format suitable for upload
    to the crawling server, i.e., pickled and compressed with zlib.

    Along with the encoded profile information we return the user's friend
    list.

    Returns:
        a tuple in the format (encoded user profile, user's friend lists)
    """
    data = retrieve_full_user_profile(username)
    friends = data['friends']
    serialized = cPickle.dumps(data)
    compressed = zlib.compress(serialized, 9)

    return (compressed, friends)


######################################################################
# MAIN
######################################################################

def main(user):
    logging.basicConfig(level=logging.DEBUG, flushlevel=logging.NOTSET)
    print "User:", user

    #print retrieve_full_user_profile(user)
    get_user_encoded_profile(user)

    #print UserInfoRetriever().get_user(user)

    #groups = GroupRetrievers().get_user_groups(user)
    #print "Groups (%i)\n\t" % len(groups),
    #print "\n\t".join(groups)

    #tracks = TracksRetriever().get_tracks(user)
    #print "Tracks (%i)\n\t" % len(tracks),
    #print "\n\t".join("%i:%s:%s" % t for t in tracks)

    #friends = FriendsRetriever().get_friends(user)
    #print "Tracks (%i)\n\t" % len(friends),
    #print "\n\t".join(friends)



if __name__ == '__main__':
    import sys
    main(sys.argv[1])

# vim: set ai tw=80 et sw=4 sts=4 fileencoding=utf-8 :
