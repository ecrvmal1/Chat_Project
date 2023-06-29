import datetime
import time

from sqlalchemy import create_engine, Table, Column, \
    Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker

from common.server_variables import SERVER_DATABASE, FROM, TO, ACTION, MESSAGE, TIME, MESSAGE_TEXT
# from common.server_utils import send_message

class ServerStorage:

    # ------------------  Create functional classes   ------------------------
    class AllUsers:
        def __init__(self, username):
            self.id = None
            self.name = username
            self.last_login = datetime.datetime.now()

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

    class MessageCounter:
        def __init__(self, user_id):
            self.id = None
            self.messages_count_user_id = user_id
            self.messages_count_sent = 0
            self.messages_count_received = 0

    class MessageRegister:
        def __init__(self, message):
            self.id = None
            self.messages_reg_from_id = message[FROM]
            self.messages_reg_to_id = message[TO]
            self.messages_reg_date = datetime.datetime.now()
            self.messages_reg_text = message[MESSAGE_TEXT]


    def __init__(self, db_path=None):
        # self.db_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)
        if not db_path:
            db_path = 'server_test_db.db3'
        self.db_engine = create_engine(f'sqlite:///{db_path}', echo=False, pool_recycle=7200,
                                       connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        # ------------------  Define tables  ------------------------

        all_users_table = Table('All_users', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('name', String, unique=True),
                                Column('last_login', DateTime),
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

        message_counter_table = Table('Message_counter_table', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('messages_count_user_id', ForeignKey('All_users.id')),
                                    Column('messages_count_sent', Integer),
                                    Column('messages_count_received', Integer)
                                      )

        message_register_table = Table('Message_register_table', self.metadata,
                                       Column('id', Integer, primary_key=True),
                                       Column('messages_reg_from_id', ForeignKey('All_users.id')),
                                       Column('messages_reg_to_id', ForeignKey('All_users.id')),
                                       Column('messages_reg_date', DateTime),
                                       Column('messages_reg_text', String)
                                       )

        # ------------ Create Tables ---------------------
        self.metadata.create_all(self.db_engine)

        # -------------- Create Mappers --------------------
        #            funct.class     table
        mapper(self.AllUsers, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        mapper(self.UserContacts, user_contacts_table)
        mapper(self.MessageCounter, message_counter_table)
        mapper(self.MessageRegister, message_register_table)

        # -----------------  Create Session -----------------
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

        # ----------------  Clean Active User ---------------
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def db_user_login(self, username, ip_address, port):
        print(f'db_login username: {username},  ip: {ip_address},  port : {port}')
        check_all_users = self.session.query(self.AllUsers).filter_by(name=username)
        # if   if_user is in AllUsers
        if check_all_users.count():
            user = check_all_users.first()
            user.last_login = datetime.datetime.now()
        else:
            # create inctance of AllUsers class
            new_user = self.AllUsers(username)
            self.session.add(new_user)
            self.session.commit()

        #                 functional class here
        check_active_user = self.session.query(self.ActiveUsers).join(self.AllUsers).filter_by(name=username).first()
        if not check_active_user:
            user = self.session.query(self.AllUsers).filter_by(name=username).first()
            new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
            self.session.add(new_active_user)
            self.session.commit()

        # -----------------  create record in logon history -------------
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
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
            self.AllUsers.last_login
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
        sender_raw = self.session.query(self.MessageCounter).\
            filter_by(messages_count_user_id=sender.id).first()

        if sender_raw:
            sender_raw.messages_count_sent += 1
            self.session.commit()
        else:
            record = self.MessageCounter(sender.id)
            record.messages_count_sent += 1
            self.session.add(record)
            self.session.commit()

        receiver = self.session.query(self.AllUsers).filter_by(name=message[TO]).first()
        receiver_raw = self.session.query(self.MessageCounter).filter_by(messages_count_user_id=receiver.id).first()

        if receiver_raw:
            receiver_raw.messages_count_received += 1
            self.session.commit()
        else:
            record = self.MessageCounter(receiver.id)
            record.messages_count_received += 1
            self.session.add(record)
            self.session.commit()

    def db_message_counter_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.MessageCounter.messages_count_sent,
            self.MessageCounter.messages_count_received,
        ).join(self.AllUsers)
        return query.all()

    def db_message_register_update(self, message):
        sender = self.session.query(self.AllUsers).filter_by(name=message[FROM]).first()
        receiver = self.session.query(self.AllUsers).filter_by(name=message[TO]).first()
        record = self.MessageRegister(message)
        record.messages_reg_from_id = sender.id
        record.messages_reg_to_id = receiver.id
        record.messages_reg_date = datetime.datetime.now()
        record.messages_reg_text = message['message_text']
        self.session.add(record)
        self.session.commit()

    def db_message_register_list(self):
        query = self.session.query(self.MessageRegister.messages_reg_from_id,
                                   self.MessageRegister.messages_reg_to_id,
                                   self.MessageRegister.messages_reg_date,
                                   self.MessageRegister.messages_reg_text,
                                   )
        return query.all()

    def db_contacts_add(self, user_name, contact_name):
        user = self.session.query(self.AllUsers).filter_by(name=user_name).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact_name).first()
        if not user:
            raise ValueError(f"Server DB : incorect user_name")
        if not contact:
            raise ValueError(f"Server DB : incorect contact_name")
        existing_contact = self.session.query(self.UserContacts).filter_by(user_id=user.id, contact_id=contact.id).first()
        if existing_contact:
            raise ValueError("Server DB :Contact already exists")
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
                self.AllUsers).filter_by(name=username).one()

            query = self.session.query(self.UserContacts, self.AllUsers.name). \
                filter_by(user_id=user.id).join(self.AllUsers, self.UserContacts.contact_id == self.AllUsers.id)
            return [contact[1] for contact in query.all()]
        else:
            query = self.session.query(self.UserContacts, self.AllUsers.name). \
                join(self.AllUsers, self.UserContacts.contact_id == self.AllUsers.id)
            return [contact[1] for contact in query.all()]

            # query = self.session.query.(
            #     self.UserContacts.user_id.name,
            #     self.UserContacts.contact_id.name,
            # ).join(self.AllUsers.name)

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
    print(f'db_all_users_list : {test_db.db_all_users_list()}')
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
    test_db.db_message_register_update(test_message1)
    test_db.db_message_register_update(test_message2)
    print(f'DB message_register :  {test_db.db_message_register_list()}')
    try:
        test_db.db_contacts_add("client_1", 'client_2')
    except ValueError as err:
        print(f'Adding contact error {err}')
    try:
        test_db.db_contacts_add("client_2", 'client_1')
    except ValueError as err:
        print(f'Adding contact error {err}')
    try:
        test_db.db_contacts_add("user_1", 'client_1')
    except ValueError as err:
        print(f'Adding contact error {err}')
    try:
        test_db.db_contacts_add("user_1", 'client_2')
    except ValueError as err:
        print(f'Adding contact error {err}')
    try:
        test_db.db_contacts_add("user_1", 'user_2')
    except ValueError as err:
        print(f'Adding contact error {err}')
    print(f'DB Contacts All :  {test_db.db_contacts_list()}')
    print(f'DB Contacts for user_1 :  {test_db.db_contacts_list("user_1")}')


