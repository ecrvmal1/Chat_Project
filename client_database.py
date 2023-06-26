from datetime import time

from common.client_variables import *
import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import mapper, sessionmaker


class ClientDatabase:
    class KnownUsers:
        def __init__(self, user):
            self.id = None
            self.username = user

    class MessageHistory:
        def __init__(self, message):
            self.id = None
            self.message_from = message[FROM]
            self.message_to = message[TO]
            self.message_date = message[TIME]
            self.message_text = message[MESSAGE_TEXT]

    class Contacts:
        def __init__(self, contact):
            self.id = id
            self.contact_name = contact

    def __init__(self, name):
        self.database_engine = create_engine(f'sqlite:///client_{name}.db3', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})

        self.metadata = MetaData()

        known_users_table = Table('known_users', self.metadata,
                                  Column('id', Integer, primary_key=True),
                                  Column('username',String)
                                  )

        message_history_table = Table('message_history', self.metadata,
                                      Column('id',Integer, primary_key=True),
                                      Column('message_from', String),
                                      Column('message_to', String ),
                                      Column('message_date',DateTime),
                                      Column('message_text',String)
                                      )

        contacts_table = Table('contacts_table', self.metadata,
                               Column('id', Integer, primary_key=True,),
                               Column('contact_name', String, unique=True)
                               )

        self.metadata.create_all(self.database_engine)

        mapper(self.KnownUsers, known_users_table)
        mapper(self.MessageHistory, message_history_table)
        mapper(self.Contacts, contacts_table)

        # make session
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # clear "contacts" table, since they will be downloaded from server
        # self.session.query(self.Contacts).delete()
        # self.session.commit()

    # function add contact
    def db_add_contact(self, contact):
        test: int = self.session.query(self.Contacts).filter_by(contact_name=contact).count()
        if not test:
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def db_del_contact(self, contact):
        test: int = self.session.query(self.Contacts).filter_by(contact_name=contact).count()
        if test:
            self.session.query(self.Contacts).filter_by(contact_name=contact).delete()
            self.session.commit()
            print(f'Contact "{contact}" deleted')

    def db_get_contacts(self):
        contacts_items = self.session.query(self.Contacts.contact_name).all()
        return [contact[0] for contact in contacts_items  ]

    def db_check_contact(self, contact):
        if self.session.query(self.Contacts).filter_by(contact_name=contact).count():
            return True
        else:
            return False

    def db_message_register(self, message):
        message_row = self.MessageHistory(message)
        self.session.add(message_row)
        self.session.commit()

    def db_get_message_history(self, from_who=None, to_who=None):
        query = self.session.query(self.MessageHistory)
        if from_who:
            query = query.filter_by(message_from =from_who)
        if to_who:
            query = query.filter_by(message_to=to_who)

        return [(history_row.from_user, history_row.to_user, history_row.message, history_row.date)
                for history_row in query.all()]

    def db_add_known_users(self, username):
        test : int = self.session.query(self.KnownUsers).flter_by(username=username)
        if test:
            return
        known_user_row = self.KnownUsers(username)
        self.session.add(known_user_row)
        self.session.commit()

    def db_get_known_users(self):
        known_users_items = self.session.query(self.KnownUsers.username).all()
        return [user[0] for user in known_users_items]

    def db_check_known_user(self, user):
        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False


if __name__ == '__main__':
    test_db = ClientDatabase('test1')

    # test contacts part
    for i in ['test2', 'test3', 'test4']:
        test_db.db_add_contact(i)
        print(f'db contacts : {test_db.db_get_contacts()}')
    test_db.db_add_contact('test5')
    print(f'db contacts : {test_db.db_get_contacts()}')
    print(f'db check contacts : {test_db.db_check_contact()}')
    print(f'db check contacts : {test_db.db_check_contact()}')

    # test message part
    test_message1 = {
        ACTION: MESSAGE,
        FROM: "test1",
        TO: "test2",
        TIME: time.time(),
        MESSAGE_TEXT: 'test message1  from test1 to test2'
    }
    test_message2 = {
        ACTION: MESSAGE,
        FROM: "test3",
        TO: "test1",
        TIME: time.time(),
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






