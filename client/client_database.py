from client.client_variables import *
import datetime
import os
import sys
import logging

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, or_
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import default_comparator

sys.path.append('../')


# from client_variables import *

class ClientDatabase:
    """
    the class for client database
    """
    class KnownUsers:
        """
        Database class for known users
        """

        def __init__(self, user):
            self.id = None
            self.username = user

    class MessageRegister:
        """
        the database class for message registration
        """

        def __init__(self, from_user, to_user, message_text):
            self.id = None
            self.message_from = from_user
            self.message_to = to_user
            self.message_date = datetime.datetime.now()
            self.message_text = message_text

    class Contacts:
        """the client database class for contacts"""

        def __init__(self, contact):
            self.id = None
            self.contact_name = contact

    def __init__(self, name):
        proj_path = os.path.abspath(os.getcwd())

        db_file = os.path.join(proj_path, 'client', f'client_{name}.db3')
        print(f'db_file = {db_file}')

        self.database_engine = create_engine(
            f'sqlite:////{db_file}',
            echo=False,
            pool_recycle=7200,
            connect_args={
                'check_same_thread': False})

        self.metadata = MetaData()

        known_users_table = Table('known_users', self.metadata,
                                  Column('id', Integer, primary_key=True),
                                  Column('username', String)
                                  )

        message_register_table = Table('message_history', self.metadata,
                                       Column('id', Integer, primary_key=True),
                                       Column('message_from', String),
                                       Column('message_to', String),
                                       Column('message_date', DateTime),
                                       Column('message_text', String)
                                       )

        contacts_table = Table('contacts_table', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('contact_name', String, unique=True)
                               )

        self.metadata.create_all(self.database_engine)

        mapper(self.KnownUsers, known_users_table)
        mapper(self.MessageRegister, message_register_table)
        mapper(self.Contacts, contacts_table)

        # make session
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # clear "contacts" table, since they will be downloaded from server
        self.session.query(self.Contacts).delete()
        self.session.commit()
        # clear "KnownUsers" table, since they will be downloaded from server
        self.session.query(self.KnownUsers).delete()
        self.session.commit()

    # function add contact
    def db_add_contact(self, contact):
        """
        The client database method for add contact
        :param contact:
        :return:
        """
        contact_exist: int = self.session.query(
            self.Contacts).filter_by(
            contact_name=contact).count()
        known_names = self.session.query(
            self.KnownUsers.username).filter_by(
            username=contact).count()
        if contact_exist:
            raise ValueError('Contact already exist')
        if not known_names:
            raise ValueError('Contact not Known')
        contact_row = self.Contacts(contact)
        self.session.add(contact_row)
        self.session.commit()

    def db_del_contact(self, contact):
        """
        The client database method for del single contact
        :param contact:
        :return:
        """
        test: int = self.session.query(
            self.Contacts).filter_by(
            contact_name=contact).count()
        if test:
            self.session.query(
                self.Contacts).filter_by(
                contact_name=contact).delete()
            self.session.commit()
            print(f'Contact "{contact}" deleted')

    def db_del_contacts(self):
        """
        The client database method for del all contacts
        :return:
        """
        '''Метод очищающий таблицу со списком контактов.'''
        self.session.query(self.Contacts).delete()

    def db_get_contacts(self):
        """
        The client database method to get list of contacts
        :return:
        """
        contacts_items = self.session.query(self.Contacts.contact_name).all()
        # print(f'ocntacts: {contacts_items}')
        return [contact[0] for contact in contacts_items]

    def db_check_contact(self, contact):
        """
        The client database method for checking contact
        :param contact:
        :return:
        """
        if self.session.query(
                self.Contacts).filter_by(
                contact_name=contact).count():
            return True
        else:
            return False

    def db_message_register(self, from_user, to_user, message_text):
        """
        The client database method for message registration
        :param from_user:
        :param to_user:
        :param message_text:
        :return:
        """
        message_row = self.MessageRegister(from_user, to_user, message_text)
        self.session.add(message_row)
        self.session.commit()

    def db_get_message_history(self, user=None):
        """The client database method to get message history"""
        if user:

            # msg_history = self.session.query(self.MessageRegister) \
            #     .filter(or_(self.MessageRegister.message_from == user, self.MessageRegister.message_to == user)).all()
            # return [(message.message_from, message.message_to, message.message_date, message.message_text)
            #         for message in msg_history]
            msg_history_from = self.session.query(
                self.MessageRegister).filter_by(
                message_from=user).all()
            msg_history_list1 = [
                (msg.message_from,
                 msg.message_to,
                 msg.message_date,
                 msg.message_text) for msg in msg_history_from]
            # print(f'list_from : {msg_history_list1}')
            msg_history_to = self.session.query(
                self.MessageRegister).filter_by(
                message_to=user).all()
            msg_history_list2 = [
                (msg.message_from,
                 msg.message_to,
                 msg.message_date,
                 msg.message_text) for msg in msg_history_to]
            # print(f'list_to : {msg_history_list2}')
            return msg_history_list1 + msg_history_list2

        else:
            msg_history = self.session.query(self.MessageRegister)
            return [(msg.message_from, msg.message_to, msg.message_date,
                     msg.message_text) for msg in msg_history.all()]

    def db_add_known_users(self, username):
        """
        The client database method for adding known user
        :param username:
        :return:
        """
        test = self.session.query(
            self.KnownUsers).filter_by(
            username=username).count()
        if test:
            return
        known_user_row = self.KnownUsers(username)
        self.session.add(known_user_row)
        self.session.commit()

    def db_get_known_users(self):
        """
        The client database method for get list of users
        :return:
        """
        # known_users_items = self.session.query(self.KnownUsers.username).all()
        known_users_items = self.session.query(self.KnownUsers).all()
        # return [user[0] for user in known_users_items]
        return [user.username for user in known_users_items]

    def db_check_known_user(self, user):
        """
        The client database method for checking known user
        :param user:
        :return:
        """
        if self.session.query(
                self.KnownUsers).filter_by(
                username=user).count():
            return True
        else:
            return False

    def db_del_known_users(self, user=None):
        """
        The client database method for deletion of known user
        :param user:
        :return:
        """
        if user:
            if self.session.query(
                    self.KnownUsers).filter_by(
                    username=user).first():
                self.session.query(
                    self.KnownUsers).filter_by(
                    username=user).delete()
            else:
                print(f'db_del_known_user: user {user}not found')
                return False
        else:
            self.session.query(self.KnownUsers).delete()


if __name__ == '__main__':
    test_db = ClientDatabase('user1')
    print(test_db.db_get_message_history('user1'))
"""
    # test contacts part
    for i in ['test2', 'test3', 'test4']:
        test_db.db_add_contact(i)
        print(f'db contacts : {test_db.db_get_contacts()}')
    test_db.db_add_contact('test5')
    print(f'db contacts : {test_db.db_get_contacts()}')
    print(f'db check contacts : {test_db.db_check_contact("test3")}')
    print(f'db check contacts : {test_db.db_check_contact("test6")}')

    # test message part
    test_message1 = {
        ACTION: MESSAGE,
        FROM: "test1",
        TO: "test2",
        TIME: datetime.datetime.now(),
        MESSAGE_TEXT: 'test message1  from test1 to test2'
    }
    test_message2 = {
        ACTION: MESSAGE,
        FROM: "test3",
        TO: "test1",
        TIME: datetime.datetime.now(),
        MESSAGE_TEXT: 'test message2  from test3 to test1'
    }
    test_db.db_message_register(test_message1)
    test_db.db_message_register(test_message2)
    print(f'message history : {test_db.db_get_message_history()}')

    # test KnownUsers part
    test_db.db_add_known_users("test3")
    test_db.db_add_known_users("test4")
    print(f'get_known_users : {test_db.db_get_known_users()}')
    print(f'check_known_user : {test_db.db_check_known_user("test3")}')
    print(f'check_known_user : {test_db.db_check_known_user("test5")}')
"""
