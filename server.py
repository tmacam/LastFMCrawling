#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A Distributed Crawler for LastFM resources."""

__version__ = "0.4.lastfm"
__date__ = "2008-11-11"
__author__ = "Tiago Alves Macambira & Rafael Sachetto"
__copyright__ = "Copyright (c) 2006-2008 Tiago Alves Macambira"
__license__ = "X11"


import itertools
import os
import gdbm
from DistributedCrawler.server import GdbmBaseControler, \
        BaseDistributedCrawlingServer
from twisted.python import log
from twisted.python.logfile import DailyLogFile
from twisted.web import resource
from common import FINDUSERS_PAGE_COUNT, FINDUSERS_SEPARATOR


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # From Python's Official itertools documentation.
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = itertools.cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.islice(nexts, pending))


class FindUsersController(GdbmBaseControler):
    """Task Controller tha receives a list of 'discovered' LastFM users.
    
    Users are discovered by crawling LastFM's user search page -- both
    for male and for female users. Tasks in this controller are in the
    following format:

        {m|f}<page number>

    For instance: M1000 is a task that instructs a client to retrieve
    the 1000th page of the male users search. The result of such task,
    to be received by the render_POST method is a form with the following
    content:
        page-id: the task in question, in the format explained above.
        page-users: a list of usernames, separated by FINDUSERS_SEPARATOR,
            i.e., null-characters (0x00).
        page-users-count: number of users in the page-users list.

    The list of discovered users is stored in a GDBM file.
    """
    ACTION_NAME = "FINDUSERS"
    PREFIX_BASE = "findusers"

    def __init__(self, sched, prefix, client_reg, users_db):
        """
        @param users_db GDBM file where the list of discovered users is kept.
        """
        GdbmBaseControler.__init__(self, sched, prefix, client_reg)
        # Setup a GDBM file where we store discovered users.
        # It is opened for synchronized R/W and created if it doesn't exist.
        self.users_db = gdbm.open(users_db, "cs")

    def render_POST(self, request):
        """Process the list of discovered users returned by a client."""
        client_id = self.client_reg.updateClientStats(request)
        # get the page identification and the list of users found
        page_id = request.args['page-id'][0]
        page_users = request.args['page-users'][0]
        page_users_count = int(request.args['page-users-count'][0])
        # save the list of found users
        users = page_users.split(FINDUSERS_SEPARATOR)
        assert len(users) == page_users_count
        for u in users :
            self.users_db[u] = '1'
        # Ok! List of found users saved
        self.markJobAsDone(page_id)
        self.client_reg.updateClientStats(request, job_done=True)
        log.msg("FINDUSERS %s done by client %s." % (page_id, client_id))
        return self.scheduler.renderPing(client_id, just_ping=True)

    @classmethod
    def initializeListOfPages(cls, prefix, n_male, n_female):
        """Setup the list of pending pages to be crawled -- probably for the
        first time.

        This is a static method. It should probably be called in a separated
        script but was coded here just to keep its code in the same place.

        Observe that we don't check for repeated page ranges -- i.e., we don't
        check the request agains pages in the DONE, ERROR or even already in
        the PENDING queue.
        """
        # Prepare the store
        store_path = prefix + "/" + cls.PREFIX_BASE
        if not os.path.isdir(store_path):
            os.makedirs(store_path)
        queue_store_path = store_path + "/queue.gdbm"
        # Interleave searches for male users w/ searches for female users
        step = FINDUSERS_PAGE_COUNT # ask this many pages in a single command
        male_pages = ("m%i" % page for page in range(1, n_male + 1, step))
        female_pages = ("f%i" % page for page in range(1, n_female + 1, step))
        pages = roundrobin(male_pages, female_pages)
        # Store commands in DB
        # Load for syncrhonized read and write, creating the DBs if necessary
        store = gdbm.open(queue_store_path, "cs")
        for p in pages:
            store[p] = '1'
        store.reorganize()
        store.close()
        # XXX: we are storing things in a dictionary, order is not
        # garanteed to be preserved. Oh! boy, too late.



class GetProfileController(GdbmBaseControler):
    """Retrieve user profile information.
    
    Remember: we are NOT CONNECTED to FindUsersController. This mean you must
    manually add clients from FindUsersController.user_db to this controller.
    """
    ACTION_NAME = "GETPROFILE"
    PREFIX_BASE = "getprofile"

    def __init__(self, sched, prefix, client_reg, profile_db):
        """Constructor.

        Args:
            sched: Scheduler instance being used by the server.
            prefix: location where all DBs are kept.
            client_reg: ClientRegistry instance being used by the server.
            profile_db: GDBM file where the list of discovered users is kept.
        """
        GdbmBaseControler.__init__(self, sched, prefix, client_reg)
        # Setup a GDBM file where we store discovered users.
        # It is opened for synchronized R/W and created if it doesn't exist.
        self.profile_db = gdbm.open(profile_db, "cs")

    def render_POST(self, request):
        """Process the user profile data returned by a client."""
        client_id = self.client_reg.updateClientStats(request)
        # get the profile identification and the list of users found
        username = request.args['username'][0]
        profile_data = request.args['profile'][0]
        friends_data = request.args['friends-list'][0]
        friends_count = int(request.args['friends-list-count'][0])
        # Process list of friends
        friends = []
        if friends_count:
            friends = friends_data.split(FINDUSERS_SEPARATOR)
        assert len(friends) == friends_count
        for f in friends:
            self.addJob(f)
        # Save user profile
        self.profile_db[username] = profile_data
        # Job done
        self.markJobAsDone(username)
        self.client_reg.updateClientStats(request, job_done=True)
        log.msg("GETPROFILE %s done by client %s." % (username, client_id))
        return self.scheduler.renderPing(client_id, just_ping=True)

    def render_notfound_error(self, request):
        """@warning only to be called by PageNotFoundController.render()"""
        client_id = self.client_reg.updateClientStats(request)
        username = request.postpath[0]
        self.markJobAsErroneus(username)
        log.msg("GETPROFILE %s reported as erroneus by client %s." % (
                                                    username, client_id))
        self.client_reg.updateClientStats(request, job_done=True)
        return self.scheduler.renderPing(client_id, just_ping=True)


class PageNotFoundController(resource.Resource):
    """Deals with "Nothing for you to see" error reports."""

    isLeaf = True

    def __init__(self, getprofile_controler):
        """Constructor.

        This controller only forwards error notifications to
        GetProfileController -- and that's it.

        @param scheduler A scheduler instance. Job will be added to it.
        @param prefix the base path where the store will be created/read.
        """
        resource.Resource.__init__(self)
        self.getprofile_controler = getprofile_controler

    def render(self, request):
        return self.getprofile_controler.render_notfound_error(request)


def main():
    print "\nInitializing server...\n"

    PORT = 8700
    PREFIX = './db/'
    INTERVAL = 60

    FINDUSERS_DB = PREFIX + '/users.db'
    GETPROFILE_DB = PREFIX + '/profiles.gdbm'

    # Setup logging
    logfile = DailyLogFile('lastfmcrawler.log', '.')
    log.startLogging(logfile)

    server = BaseDistributedCrawlingServer(PORT, PREFIX, INTERVAL)
    # Seting controllers up
    findusers_controller = FindUsersController(server.getScheduler(),
                                               PREFIX,
                                               server.getClientRegistry(),
                                               FINDUSERS_DB)
    getprofile_controller = GetProfileController(server.getScheduler(),
                                                 PREFIX,
                                                 server.getClientRegistry(),
                                                 GETPROFILE_DB)
    notfound_controller  = PageNotFoundController(getprofile_controller)

    # Registering Controllers
    server.registerTaskController(findusers_controller,
                                 'findusers',
                                 'FindUsers')
    server.registerTaskController(getprofile_controller,
                                 'getprofile',
                                 'Profiles')
    server.root.putChild('notfound', notfound_controller)

    print "\nServer setup done.\n"
    log.msg("Server setup done.")

    server.run()
    
    

if __name__ == '__main__':
    main()

# vim: set ai tw=80 et sw=4 sts=4 fileencoding=utf-8 :
