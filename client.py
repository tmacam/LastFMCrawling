#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""DistributedCrawling client for LastFM resources."""

__version__ = "0.4.lastfm"
__date__ = "2008-11-11"
__author__ = "Tiago Alves Macambira & Rafael Sachetto"
__copyright__ = "Copyright (c) 2006-2008 Tiago Alves Macambira"
__license__ = "X11"


import sys
import os
import urllib2
import time
import logging
from socket import gethostname
from DistributedCrawler.client import upload_aux
from DistributedCrawler.client import BaseClient, getUUID, log_backtrace, log_urllib2_exception
from DistributedCrawler.client.daemonize import createDaemon, reconfigStdout
from DistributedCrawler.client.BeautifulSoup import BeautifulSoup
#from digg_article_retriever import ArticleRetriever, \
#        __version__ as articleretriever_version
from common import FINDUSERS_VALID_GENDERS, FINDUSERS_SEPARATOR, \
        FINDUSERS_PAGE_COUNT, FINDUSERS_URL_TEMPLATE


articleretriever_version = "unk-aret-ver"


# TODO(macambira): perhaps python has a nice logging framework now
# TODO(macambira): perhaps python has a nice logging framework now
# TODO(macambira): perhaps python has a nice logging framework now
# TODO(macambira): perhaps python has a nice logging framework now
log = sys.stdout


######################################################################
# AUX. CLASSES
######################################################################


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
                logging.debug("get_url : %s"url)
                page = request.read()
                self.validate(page)
                return page
            except (InvalidPage, urllib2.URLError, urllib2.HTTPError,
                    ValueError):
                if retries > self.MAX_RETRIES:
                    raise


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


        


######################################################################
# Crawling Clients
######################################################################


class LastFMClient(BaseClient):
    """Client for crawling digg articles."""

    def __init__(self, client_id, base_url, store_dir=None):
        """LastFMClient Constructor."""
        # Parent class constructor
        BaseClient.__init__(self, client_id, base_url, store_dir)
        # Informing the version of our ArticleRetriver
        self.headers["client-arver"] =  articleretriever_version
        # Registering Command Handlers
        self.handlers["FINDUSERS"] = self.findusers

    def _write_to_store(self, article_id, data):
        """Write a (compressed) article to store.
        
        Article_id is turned into something filesystem safe here.
        """
        # FIXME - Must customize this function for lastfm content
        # FIXME - Must customize this function for lastfm content
        # FIXME - Must customize this function for lastfm content
        safe_id = article_id.replace('/', '_')
        safe_id += '.xml.gz'
        BaseClient._write_to_store(self, safe_id, data)

    def findusers(self, params):
        """Retrieve pages from the users search and send it to the server."""
        # Retrieve the search gender (male, female) and search page
        gender, page_num = params[0], int(params[1:])
        assert gender in FINDUSERS_VALID_GENDERS
        # Download search result pages
        logging.info("FINDUSERS %s BEGIN", params)
        retriever = FindUsersRetriver()
        found_users = retriever.get_users_from_pages(gender, page_num)
        logging.info("FINDUSERS %s GOT FINDUSERS DATA", params)
        # Setup form and headers
        #    Although we used "upload" code, this is a plain POST
        upload_headers = dict(self.headers)
        form_data = {'page-id' : params,
                     'page-users'  : FINDUSERS_SEPARATOR.join(found_users),
                     'page-users-count'  : str(len(found_users)),
                     'client-id'    : self.id}
        # Upload the article
        upload_url = self.base_url + '/findusers/' + params
        response = upload_aux.upload_form(upload_url, form_data, upload_headers)
        logging.info("FINDUSERS %s END", params)
        # Ok. Command, handled. Now what?
        # Do what the server told us to.
        # Command MUST be SLEEP. We will sleep for at least self.MIN_SLEEP
        command = response.read()
        self._handleCommand(command, do_sleep=True)



#TODO(macambira): move main out of this module or refactor it into a set of small helper functions


def main(base_url, store_dir):
    """Setup enviroment and run client."""
    global log

    # FIXME Remove global log, use logging package
    # FIXME Merge as much of this code as possible with __main__

    hostname = gethostname()

    id_filename = store_dir + "/" + hostname + '.id'
    log_filename = store_dir + "/" + hostname + '.log'
    out_filename = store_dir + "/" + hostname + '.out' # FIXME DEPRECATED!!!!

    # Setup logging, client id
    client_id = getUUID(id_filename)
    logging.basicConfig(filename=log_filename,
                        level=logging.INFO,
                        flushlevel=logging.NOTSET)
    # FIXME DEPRECATED Redirecting log from output to file
    log = open(out_filename, 'a', 0)

    cli = LastFMClient(client_id, base_url=base_url, store_dir=store_dir)
    sys.stderr.write("\nStarting Client...\n")
    log.write("STARTED %s \n" % time.asctime())
    logging.info("STARTED %s", time.asctime())

    cli.run()


if __name__ == '__main__':
    #BASE_URL = 'http://www.speed.dcc.ufmg.br/lastfm'
    BASE_URL = 'http://localhost:8700'
    STORE_DIR = os.getcwd()  # "." loses its meaning as soon as we deamonize
    LOG_FILENAME = STORE_DIR + "/lastfmclient.log"
    STDOUT_REDIR_FILENAME = STORE_DIR + "/daemon.out"

    # Dettach the current proceess from the terminal and became 
    # a daemon
    print "Becoming a daemon"
    #res = createDaemon()
    # We closed all stdio and redirected them for /dev/null
    # Just in case we need them back, let's reconfigure stdout and stderr
    #reconfigStdout(STDOUT_REDIR_FILENAME)
    log = sys.stdout # we closed the old file descriptor, get the new one.
    print "Became a daemon"
    
    try:
        main(BASE_URL, STORE_DIR)
    except urllib2.HTTPError, e:
        logging.exception("Exception caught in __main__.")
        #log_urllib2_exception(e) # FIXME - use logging facility
        raise
    except:
        #log_backtrace()
        raise
 
# vim: set ai tw=80 et sw=4 sts=4 fileencoding=utf-8 :
