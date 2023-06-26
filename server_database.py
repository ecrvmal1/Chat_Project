import datetime
import time

from sqlalchemy import create_engine, Table, Column, \
    Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker

from common.server_variables import SERVER_DATABASE, FROM, TO, ACTION, MESSAGE, TIME, MESSAGE_TEXT


class ServerStorage:

    # ------------------  Create functional classes   ------------------------
    class AllUsers:
        def __init__(self, username):
            self.id = None
            self.name = username
            self.last_login_date = datetime.datetime.now()

    class ActiveUsers():
        def __init__(self, user_id, ip_address, port, login_time):
            self.id = None
            self.user_id = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time

    class LoginHistory:
        def __init__(self, user_id, date, ip_address, port):
            self.id = None
            self.user_id = user_id
            self.date_time = datetime.datetime.now()
            self.ip_address = ip_address
            self.port = port

    class UserContacts:
        def __init__(self, user_id, contact):
            self.id = None
            self.user_id = user_id
            self.contact_id = contact

    class UserMessageCounter:
        def __init__(self, user_id):
            self.id = None
            self.user_id = user_id
            self.messages_sent = 0
            self.messages_received = 0


    def __init__(self):
        # self.db_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)
        self.db_engine = create_engine('sqlite:///server_test_db.db3', echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        # ------------------  Define tables  ------------------------

        all_users_table = Table('All_users', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('name', String, unique=True),
                                Column('last_login_date', DateTime),
                                )

        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', ForeignKey('All_users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        user_login_history = Table('User_login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', ForeignKey('All_users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip_address', String),
                                   Column('port', String)
                                   )

        user_contacts_table = Table('User_contacts_table', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user_id', ForeignKey('All_users.id')),
                                    Column('contact_id', ForeignKey('All_users.id')),
                                    )

        user_message_counter_table = Table('User_message_counter_table', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user_id', ForeignKey('All_users.id')),
                                    Column('messages_sent', Integer),
                                    Column('messages_received', Integer),
                                           )

        # ------------ Create Tables ---------------------
        self.metadata.create_all(self.db_engine)

        # -------------- Create Mappers --------------------
        #            funct.class     table
        mapper(self.AllUsers, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        mapper(self.UserContacts, user_contacts_table)
        mapper(self.UserMessageCounter, user_message_counter_table)

        # -----------------  Create Session -----------------
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

        # ----------------  Clean Active User ---------------
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def db_user_login(self, username, ip_address, port):
        print(f'db_login username: {username},  ip: {ip_address},  port : {port}')
        rez = self.session.query(self.AllUsers).filter_by(name=username)
        # if   if_user is in AllUsers
        if rez.count():
            user = rez.first()
            user.last_login_date = datetime.datetime.now()
        else:
            # create inctance of AllUsers class
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        #                 functional class here
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        self.session.commit()

        # -----------------  create record in logon history -------------
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)
        self.session.commit()

    def db_user_logout(self, username):
        # take from AllUsers(functional) record for user
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        # delete record from ActiveUsers(functional class)
        self.session.query(self.ActiveUsers).filter_by(user_id=user.id).delete()
        self.session.commit()

    def db_all_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login_date
        )
        return query.all()

    def db_active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def db_login_history_list(self, username=None):
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip_address,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    def db_message_counter_update(self, message):
        sender = self.session.query(self.AllUsers).filter_by(name=message[FROM]).first()
        sender_raw = self.session.query(self.UserMessageCounter).filter_by(user_id=sender.id).first()

        if sender_raw:
            sender_raw.messages_sent += 1
            self.session.commit()
        else:
            record = self.UserMessageCounter(sender.id)
            record.messages_sent += 1
            self.session.add(record)
            self.session.commit()

        receiver = self.session.query(self.AllUsers).filter_by(name=message[TO]).first()
        receiver_raw = self.session.query(self.UserMessageCounter).filter_by(user_id=receiver.id).first()

        if receiver_raw:
            receiver_raw.messages_received += 1
            self.session.commit()
        else:
            record = self.UserMessageCounter(receiver.id)
            record.messages_received += 1
            self.session.add(record)
            self.session.commit()

    def db_message_counter_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.UserMessageCounter.messages_sent,
            self.UserMessageCounter.messages_received,
        ).join(self.AllUsers)
        return query.all()

    def db_contacts_add(self, user_name, contact_name):
        user = self.session.query(self.AllUsers).filter_by(name=user_name).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact_name).first()
        existing_contact = self.session.query(self.UserContacts).filter_by(user_id=user.id, contact_id=contact.id).first()
        if not contact or existing_contact:
            return
        new_contact = self.UserContacts(user.id, contact.id)
        self.session.add(new_contact)
        self.session.commit()

    def db_contacts_remove(self, user_name, contact_name):
        user = self.session.query(self.AllUsers).filter_by(name=user_name).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact_name).first()
        existing_contact = self.session.query(self.UserContacts).filter_by(user_id=user.id,
                                                                           contact_id=contact.id).first()
        if not existing_contact:
            return
        self.session.delete(existing_contact)
        # self.session.query(self.UsersContacts).filter(self.UsersContacts.user == user.id,
        #                                               self.UsersContacts.contact == contact.id).delete()
        self.session.commit()

    def db_contacts_list(self, username=None):
        if username:
            user = self.session.query(
                # self.UserContacts.id,
                self.AllUsers).filter_by(name=username).first()

            query = self.session.query(self.UserContacts). \
                filter_by(user_id=user.id).join(self.AllUsers, self.UserContacts.user_id == self.AllUsers.id)
            return [contact.contact_id for contact in query.all()]

        
        else:
            # query = self.session.query(
            #     self.AllUsers.name,
            #     self.AllUsers.name,
            # )
            query = self.session.query(
                self.UserContacts.user_id,
                self.UserContacts.contact_id,
            )
            return query.all()


# ------------- Testing -----------------
if __name__ == '__main__':
    test_db = ServerStorage()
    # выполняем 'подключение' пользователя
    test_db.db_user_login('client_1', '192.168.1.4', 8888)
    test_db.db_user_login('client_2', '192.168.1.5', 7777)
    test_db.db_user_login('user_1', '192.168.1.6', 6666)
    test_db.db_user_login('user_2', '192.168.1.7', 5555)
    # выводим список кортежей - активных пользователей
    print(f'db_active_users_list : {test_db.db_active_users_list()}')
    # выполянем 'отключение' пользователя
    test_db.db_user_logout('client_1')
    # выводим список активных пользователей
    print(f'DB_active_users_list : {test_db.db_active_users_list()}')
    # запрашиваем историю входов по пользователю
    test_db.db_login_history_list('client_1')
    # выводим список известных пользователей
    print(f'DB All Users : {test_db.db_all_users_list()}')
    test_message1 = {
        ACTION: MESSAGE,
        FROM: "client_1",
        TO: "client_2",
        TIME: time.time(),
        MESSAGE_TEXT: "test message"
        }
    test_message2 = {
        ACTION: MESSAGE,
        FROM: "user_1",
        TO: "user_2",
        TIME: time.time(),
        MESSAGE_TEXT: "test message"
        }
    test_db.db_message_counter_update(test_message1)
    test_db.db_message_counter_update(test_message2)
    print(f'DB message_counter :  {test_db.db_message_counter_list()}')
    print(f'DB Contacts :  {test_db.db_contacts_list()}')
    test_db.db_contacts_add("client_1", 'client_2')
    test_db.db_contacts_add("client_2", 'client_1')
    test_db.db_contacts_add("user_1", 'client_1')
    test_db.db_contacts_add("user_1", 'client_2')
    test_db.db_contacts_add("user_1", 'user_2')
    print(f'DB Contacts :  {test_db.db_contacts_list()}')
    print(f'DB Contacts :  {test_db.db_contacts_list("user_1")}')


