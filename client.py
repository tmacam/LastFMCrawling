#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""DistributedCrawling client for LastFM resources."""

__version__ = "0.4.lastfm"
__date__ = "2008-11-11"
__author__ = "Tiago Alves Macambira & Rafael Sachetto"
__copyright__ = "Copyright (c) 2006-2008 Tiago Alves Macambira"
__license__ = "X11"

from optparse import OptionParser
import os
import urllib2
import time
import logging
from socket import gethostname
from DistributedCrawler.client import upload_aux
from DistributedCrawler.client import BaseClient, getUUID, log_backtrace, log_urllib2_exception
from DistributedCrawler.client.daemonize import createDaemon, reconfigStdout
#from digg_article_retriever import ArticleRetriever, \
#        __version__ as articleretriever_version
from common import FINDUSERS_VALID_GENDERS, FINDUSERS_SEPARATOR 
from retrievers import FindUsersRetriver, get_user_encoded_profile, \
    retrieve_encoded_user_library_snapshot, LibrarySnapshotsRetriever, \
    PageNotFound, __version__ as articleretriever_version


######################################################################
# Crawling Clients
######################################################################


class LastFMClient(BaseClient):
    """Client for crawling digg articles."""

    MIN_SLEEP = 120

    def __init__(self, client_id, base_url, store_dir=None):
        """LastFMClient Constructor."""
        # Parent class constructor
        BaseClient.__init__(self, client_id, base_url, store_dir)
        # Informing the version of our ArticleRetriver
        self.headers["client-arver"] =  articleretriever_version
        # Registering Command Handlers
        self.handlers["FINDUSERS"] = self.findusers
        self.handlers["GETPROFILE"] = self.getprofile
        self.handlers["GETLIBRARY"] = self.getlibrary

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

    def getprofile(self, params):
        """Retrieve user profile and send it to the server."""
        log = logging.getLogger("GETPROFILE")
        # The only parameter we get is the user name
        username = params
        # Download search result pages
        log.info("BEGIN %s", params)
        try:
            profile, friends = get_user_encoded_profile(username)
            log.info("GOT PROFILE FOR USER %s", username)
            # Setup form and headers
            #    Although we used "upload" code, this is a plain POST
            upload_headers = dict(self.headers)
            form_data = {'username' : username,
                         'profile' : profile, 
                         'friends-list'  : FINDUSERS_SEPARATOR.join(friends),
                         'friends-list-count'  : str(len(friends)),
                         'client-id'    : self.id}
            # Upload the article
            logging.info("UPLOADING TO SERVER %s", params)
            upload_url = self.base_url + '/getprofile/' + username
            response = upload_aux.upload_form(upload_url, form_data,
                                              upload_headers)
        except PageNotFound:
            response = self.report_not_found_user(username, log)
        logging.info("END %s", params)
        # Ok. Command, handled. Now what?
        # Do what the server told us to.
        # Command MUST be SLEEP. We will sleep for at least self.MIN_SLEEP
        command = response.read()
        self._handleCommand(command, do_sleep=True)

    def getlibrary(self, params):
        """Retrive a user's music library.

        TODO: we should've encoded the command/job as "username#last_crawled_ts"
              but this will be left as pending work for the next crawling...

        Encoded params:
            username, as string
        """
        log = logging.getLogger("GETLIBRARY")
        # The only parameter we get is the user name
        username = params
        # XXX The listened_time_threshold was supposed to come encoded with
        # the username but we had to change too much stuff in the server-side
        # to make this happen. See above todo.
        listened_time_threshold = LibrarySnapshotsRetriever.DAY_ONE
        # Download search result pages
        log.info("BEGIN %s", params)
        try:
            result = retrieve_encoded_user_library_snapshot(username,
                listened_time_threshold)
            library, last_crawled_ts = result
            log.info("GOT LIBRARY FOR USER %s", username)
            # Setup form and headers
            #    Although we used "upload" code, this is a plain POST
            upload_headers = dict(self.headers)
            form_data = {'username' : username,
                         'library' : library, 
                         'last-crawled-ts' : str(int(last_crawled_ts)), 
                         'client-id'    : self.id}
            # Upload the article
            logging.info("UPLOADING TO SERVER %s", params)
            upload_url = self.base_url + '/getlibrary/' + username
            response = upload_aux.upload_form(upload_url, form_data,
                                              upload_headers)
        # XXX We are not handling errors -- 
        logging.info("END %s", params)
        # Ok. Command, handled. Now what?
        # Do what the server told us to.
        # Command MUST be SLEEP. We will sleep for at least self.MIN_SLEEP
        command = response.read()
        self._handleCommand(command, do_sleep=True)



    def report_not_found_user(self, username, log):
        log.info("REPORTING 404 ERROR BACK TO SERVER FOR USER '%s'", username)
        req = urllib2.Request(self.base_url + '/notfound/' + \
                                    username, headers=self.headers)
        response = urllib2.urlopen(req)

        return response





######################################################################
# MAIN
######################################################################


#TODO(macambira): move main out of this module or refactor it into a set of small helper functions


def main(base_url, store_dir, log_to_screen=False):
    """Setup enviroment and run client."""

    # TODO Merge as much of this code as possible with __main__

    hostname = gethostname()

    id_filename = store_dir + "/" + hostname + '.id'
    log_filename = store_dir + "/" + hostname + '.log'
    out_filename = store_dir + "/" + hostname + '.out' # FIXME DEPRECATED!!!!

    # Setup logging
    extra_log_options = {"level" : logging.DEBUG, "flushlevel": logging.NOTSET}
    if not log_to_screen:
        extra_log_options['filename'] = log_filename
    logging.basicConfig( **extra_log_options )
    # Setup client id
    client_id = getUUID(id_filename)

    cli = LastFMClient(client_id, base_url=base_url, store_dir=store_dir)
    logging.info("STARTED %s", time.asctime())

    cli.run()


def parse_command_line():
    """As the name says, parses the command line."""
    parser = OptionParser()

    parser.add_option("-d", "--outdir", dest="store_dir", default=None,
                      help=("Write log reports and other files to DIR. "
                            "Defaults to the current directory."), 
                      metavar="DIR")
    parser.add_option("-f", "--foreground",
                      action="store_true", dest="foreground", default=False,
                      help="runs the client in foreground")
    parser.add_option("-l", "--log-to-screen", dest="toscreen", default=False,
                      action="store_true",
                      help=("Log to stdout instead of to log file. "
                            "Defaults to False"))

    (options, args) = parser.parse_args()

    return options, args


if __name__ == '__main__':
    BASE_URL = 'http://www.speed.dcc.ufmg.br/lastfm'
    #BASE_URL = 'http://localhost:8700'
    BASE_DIR = os.getcwd()  # "." loses its meaning as soon as we deamonize
    STDOUT_REDIR_FILENAME = BASE_DIR + "/daemon.out"

    options, args = parse_command_line()

    store_dir = BASE_DIR
    if options.store_dir:
        store_dir = os.path.join(BASE_DIR, options.store_dir)
        if not os.path.isdir(store_dir):
            os.makedirs(store_dir)

    # TODO Merge as much of this code as possible with main()
    # Dettach the current proceess from the terminal and became 
    # a daemon
    if not options.foreground:
        print "Becoming a daemon"
        res = createDaemon()
        # We closed all stdio and redirected them for /dev/null
        # Just in case we need them back, let's reconfigure stdout and stderr
        reconfigStdout(STDOUT_REDIR_FILENAME)
        print "Became a daemon"
    
    try:
        main(BASE_URL, store_dir, options.toscreen)
    except urllib2.HTTPError, e:
        log_urllib2_exception(e)
        raise
    except:
        log_backtrace()
        raise


# vim: set ai tw=80 et sw=4 sts=4 fileencoding=utf-8 :
