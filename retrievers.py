#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Retrievers for LastFM resources."""

__version__ = "0.4.lastfm"
__date__ = "2008-11-17"
__author__ = "Tiago Alves Macambira & Rafael Sachetto"
__copyright__ = "Copyright (c) 2006-2008 Tiago Alves Macambira"
__license__ = "X11"


import datetime
import urllib2
import httplib
import logging
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

    def get_users_from_search_page(self, gender, page):
        "Returns a list whith the users found in a search page."
        page_url = FINDUSERS_URL_TEMPLATE % (gender, page)
        data = self.get_url(page_url)
        soup = BeautifulSoup(data)
        # Each user has a vcard whose first and only Anchor tag is a
        # link for the user profile in LastFM, in the form
        # http://www.lastfm.com.br/user/USERNAME. All we want is the USERNAME
        # part of such links.
        users_vcards = soup.find("ul", "usersMedium").findAll("div","vcard")
        users = [vcard.a['href'].split('/')[-1] for vcard in users_vcards]
        return users

    def get_users_from_pages(self, gender, start_page):
        """Get the list of users from a range search pages.
        
        Get the users from FINDUSERS_PAGE_COUNT user search pages,
        starting at start_page.

        Returns:
            a set with the users found.
        """
        found_users = set()
        for page in range(start_page, start_page + FINDUSERS_PAGE_COUNT):
            for user in self.get_users_from_search_page(gender, page):
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
        # the usernames were extracted from the anchor tags from the
        # user search html pages -- those usernames are already
        # percent-encoded.
        while cur_page <= lastpage:
            url = self.GROUP_URL_TEMPLATE % (user, cur_page)
            data = self.get_url(url)
            soup = BeautifulSoup(data)
            groups_html = soup.findAll("div","groupContainer")
            if groups_html:
                for group in groups_html:
                    groups.append(group.find("a")['href'].split('/')[-1])
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
    
    Track listings are returned as list of (playcount, artist, track name)
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

        while cur_page <= lastpage:
            print "\tPage:", cur_page, "of", lastpage # FIXME
            url = self.GET_TRACKS_URL_TEMPLATE % (user, APIKEY, cur_page)
            xml = self.get_url(url)
            soup = BeautifulStoneSoup(xml).find("tracks")
            tracks = soup.findAll("track")

            for track in tracks:
                playcount = int(track.find("playcount").contents[0])
                track_url = track.find("url").contents[0]
                artist, _, name = track_url.split("/")[-3:]
                track_list.append((playcount, artist, name))
            # Track information can be splitted across several pages.
            # Get the number of pages.
            if cur_page == 1:
                lastpage = int(soup.attrs[-1][1])

            cur_page += 1

        return track_list


class FriendsRetriever(ObstinatedRetriever):
    """Friendship information is returned percent-encoded."""

    GET_USER_FRIENDS_TEMPLATE = 'http://ws.audioscrobbler.com/2.0/?method=user.getfriends&user=%s&api_key=%s'

    def validate(self, data):
        if not BeautifulStoneSoup(data).find("friends"):
            raise InvalidPage()

    def get_friends(self, user):
        friends_list = []

        url = self.GET_USER_FRIENDS_TEMPLATE % (user, APIKEY)
        xml = self.get_url(url)
        soup = BeautifulStoneSoup(xml)

        friends_urls = soup.findAll("url")

        for f_url in friends_urls:
            friend_name = f_url.contents[0].split("/")[-1]
            friends_list.append(friend_name)

        return friends_list


class UserInfoRetriever(ObstinatedRetriever):

    USER_URL_TEMPLATE = "http://www.lastfm.com.br/user/%s/"

    def validate(self, data):
        soup = BeautifulSoup(data)
        if not soup.find('div', 'clearit user vcard') and \
           not soup.find('div', 'clearit subscriber vcard'):
            raise InvalidPage()

    def get_user(self, username):

        url = self.USER_URL_TEMPLATE % (username)
        html = self.get_url(url)
        soup = BeautifulSoup(html)

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

        m_e = details.find('span', 'userPlays') 
        # average play count per day
        average = m_e.attrs[1][1].split()[2] 
        # User since... (user_since)
        d_m_a = m_e.find('small').contents[0]
        dia = int(d_m_a.split()[1])
        mes = int(MONTHS_TO_NUM[d_m_a.split()[2]])
        ano = int(d_m_a.split()[3])
        user_since = datetime.date(ano,mes,dia).isoformat()
        # Executions
        flips = m_e.findAll('span', 'flip')
        digits = []
        for d in flips:
            digits.append(d.contents[0])
        executions = "".join(digits)
        # Homepage
        homepage = ""
        h = details.find('a', 'url homepage')
        if h:
            homepage = h.contents[0]
        # Sex, age
        mais_detalhes = details.find("p", "userInfo adr")
        if not name and len(mais_detalhes.contents) > 1:
            aux = mais_detalhes.contents[0].split()
            if len(aux) == 2:
                idade, sexo = aux
                sexo = takeComma(sexo)
                idade = takeComma(idade)
            else:
                sexo = aux[0]
                idade = ''
        else:
            if len(mais_detalhes.contents) > 1:
                aux = mais_detalhes.contents[1].split()
                if len(aux) == 3:
                    _, idade, sexo = aux
                    sexo = takeComma(sexo)
                    idade = takeComma(idade)
                elif len(aux) == 2:
                    _, sexo = aux
                    sexo = takeComma(sexo)
                    idade = ''
            else:
                aux = mais_detalhes.contents[0].split()
                if len(aux) == 1:
                    sexo = aux[0]
                    idade = ''
                else:
                    idade, sexo = aux
                    sexo = takeComma(sexo)
                    idade = takeComma(idade)
        # Country
        pais = ''
        pais_html = mais_detalhes.find("span", "country-name")
        if pais_html:
            pais = pais_html.contents[0]

        return (username, name, idade, sexo, pais, executions, average,
                homepage, user_since )


def retrieve_full_user_profile(username):
    """Get the full user profile from a LastFM user.
    
    Returns:
        a dict contaning each of the aspects we are interested on of the user's
        profile
    """
    # We are not performing "retries" here as this is done for more
    # then enought times by each of the specialized retrievers
    info = UserInfoRetriever().get_user(user)
    groups = GroupRetrievers().get_user_groups(user)
    friends = FriendsRetriever().get_friends(user)
    tracks = TracksRetriever().get_tracks(user)

    return {"info" : info, "groups" : groups, "friends" : friends,
            "tracks" : tracks }


def get_user_encoded_profile(username):
    """Get the full user profile information serialized and compressed.

    The returned user profile dada will be in a format suitable for upload
    to the crawling server.
    """
    # FIXME parei aqui
    # FIXME parei aqui
    # FIXME parei aqui
    # FIXME parei aqui




######################################################################
# MAIN
######################################################################


if __name__ == '__main__':
    import sys
    user = sys.argv[1]
    print "User:", user

#    groups = GroupRetrievers().get_user_groups(user)
#    print "Groups (%i)\n\t" % len(groups),
#    print "\n\t".join(groups)

    tracks = TracksRetriever().get_tracks(user)
    print "Tracks (%i)\n\t" % len(tracks),
    print "\n\t".join("%i:%s:%s" % t for t in tracks)

#    friends = FriendsRetriever().get_friends(user)
#    print "Tracks (%i)\n\t" % len(friends),
#    print "\n\t".join(friends)

#    print UserInfoRetriever().get_user(user)

# vim: set ai tw=80 et sw=4 sts=4 fileencoding=utf-8 :
