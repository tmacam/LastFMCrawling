#!/usr/bin/python

from server import FindUsersController

def main(male, female):
    db_path = "./db/"
    FindUsersController.initializeListOfPages(db_path, male, female)

if __name__ == '__main__':
    main(50842,  32186)
