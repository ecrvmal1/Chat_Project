import datetime
import logging
import time

from sqlalchemy import create_engine, Table, Column, \
    Integer, String, MetaData, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import default_comparator

from server.server_variables import FROM, TO, ACTION, MESSAGE, TIME, MESSAGE_TEXT

# from common.server_utils import send_message
LOGGER = logging.getLogger('server_logger')


class ServerStorage:
    """
    The server database class
    """

    # ------------------  Create functional classes   ------------------------
    class AllUsers:
        """
        The server database class AllUsers
        """

        def __init__(self, username, passwrd_hash):
            self.id = None
            self.name = username
            self.last_login = datetime.datetime.now()
            self.passwd_hash = passwrd_hash
            self.pubkey = None

    class ActiveUsers():
        """
        The server database class Active Users
        """

        def __init__(self, user_id, ip_address, port, login_time):
            self.id = None
            self.user_id = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time

    class LoginHistory:
        """
        The server database class Login History
        """

        def __init__(self, user_id, ip_address, port):
            self.id = None
            self.user_id = user_id
            self.date_time = datetime.datetime.now()
            self.ip_address = ip_address
            self.port = port

    class UserContacts:
        """
        The server database class UserContacts
        """

        def __init__(self, user_id, contact):
            self.id = None
            self.user_id = user_id
            self.contact_id = contact

    class MessageCounter:
        """
        The server database class MessageCounter
        """

        def __init__(self, user_id):
            self.id = None
            self.msgs_counter_user_id = user_id
            self.msgs_counter_sent = 0
            self.msgs_counter_received = 0

    class MessageRegister:
        """
        The server database class Message Register
        """

        def __init__(self, message):
            self.id = None
            self.msgs_reg_from_id = message[FROM]
            self.msgs_reg_to_id = message[TO]
            self.msgs_reg_date = datetime.datetime.now()
            self.msgs_reg_text = message[MESSAGE_TEXT]

    def __init__(self, db_path=None):
        # self.db_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)
        if not db_path:
            db_path = 'server_test_db.db3'
        self.db_engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,
            pool_recycle=7200,
            connect_args={
                'check_same_thread': False})
        self.metadata = MetaData()

        # ------------------  Define tables  ------------------------

        all_users_table = Table('All_users', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('name', String, unique=True),
                                Column('last_login', DateTime),
                                Column('passwd_hash', String),
                                Column('pubkey', Text)
                                )

        active_users_table = Table(
            'Active_users', self.metadata, Column(
                'id', Integer, primary_key=True), Column(
                'user_id', ForeignKey('All_users.id'), unique=True), Column(
                'ip_address', String), Column(
                    'port', Integer), Column(
                        'login_time', DateTime))

        user_login_history = Table(
            'User_login_history', self.metadata, Column(
                'id', Integer, primary_key=True), Column(
                'user_id', ForeignKey('All_users.id')), Column(
                'date_time', DateTime), Column(
                    'ip_address', String), Column(
                        'port', String))

        user_contacts_table = Table(
            'User_contacts_table', self.metadata, Column(
                'id', Integer, primary_key=True), Column(
                'user_id', ForeignKey('All_users.id')), Column(
                'contact_id', ForeignKey('All_users.id')), )

        message_counter_table = Table(
            'Message_counter_table', self.metadata, Column(
                'id', Integer, primary_key=True), Column(
                'msgs_counter_user_id', ForeignKey('All_users.id')), Column(
                'msgs_counter_sent', Integer), Column(
                    'msgs_counter_received', Integer))

        message_register_table = Table(
            'Message_register_table', self.metadata, Column(
                'id', Integer, primary_key=True), Column(
                'msgs_reg_from_id', ForeignKey('All_users.id')), Column(
                'msgs_reg_to_id', ForeignKey('All_users.id')), Column(
                    'msgs_reg_date', DateTime), Column(
                        'msgs_reg_text', String))

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

    def db_add_user(self, user_name, passwd_hash):
        """
        The server database method for adding user
        :param user_name:
        :param passwd_hash:
        :return:
        """
        new_user = self.session.query(self.AllUsers). \
            filter_by(name=user_name).first()
        if new_user:
            LOGGER.info(f'user {user_name} already exists')
            return
        new_user = self.AllUsers(user_name, passwd_hash)
        self.session.add(new_user)
        self.session.commit()

    def db_remove_user(self, user_name):
        """
        The server database method for removing user
        :param user_name:
        :return:
        """
        user = self.session.query(
            self.AllUsers).filter_by(
            name=user_name).first()
        self.session.query(
            self.ActiveUsers).filter_by(
            user_id=user.id).delete()
        self.session.query(
            self.LoginHistory).filter_by(
            user_id=user.id).delete()
        self.session.query(
            self.UserContacts).filter_by(
            user_id=user.id).delete()
        self.session.query(
            self.UserContacts).filter_by(
            contact_id=user.id).delete()
        self.session.query(
            self.MessageCounter).filter_by(
            msgs_counter_user_id=user.id).delete()
        self.session.query(
            self.MessageRegister).filter_by(
            msgs_reg_from_id=user.id).delete()
        self.session.query(
            self.MessageRegister).filter_by(
            msgs_reg_to_id=user.id).delete()
        self.session.query(self.AllUsers).filter_by(name=user_name).delete()
        self.session.commit()

    def db_user_login(self, username, ip_address, port, public_key):
        """
        The server database method for user login
        :param username:
        :param ip_address:
        :param port:
        :param public_key:
        :return:
        """
        print(
            f'db_login username: {username},  ip: {ip_address},  port : {port}')
        user = self.session.query(
            self.AllUsers).filter_by(
            name=username).first()
        # if   if_user is in AllUsers
        if user:
            user.last_login = datetime.datetime.now()
            if user.pubkey != public_key:
                user.pubkey = public_key
        else:
            raise ValueError("User isn't registered")
        new_active_user = self.ActiveUsers(
            user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        # и сохранить в историю входов
        new_history = self.LoginHistory(user.id, ip_address, port)
        self.session.add(new_history)

        # Сохрраняем изменения
        self.session.commit()

    def db_user_logout(self, username):
        """
        The server database method for user logout
        :param username:
        :return:
        """
        # take from AllUsers(functional) record for user
        user = self.session.query(
            self.AllUsers).filter_by(
            name=username).first()
        # delete record from ActiveUsers(functional class)
        self.session.query(
            self.ActiveUsers).filter_by(
            user_id=user.id).delete()
        self.session.commit()

    def db_check_user(self, username):
        """
        The server database method for cheking user
        :param username:
        :return:  False / True
        """
        # take from AllUsers(functional) record for user
        user = self.session.query(
            self.AllUsers).filter_by(
            name=username).first()
        if user:
            return True
        return False

    def db_all_users_list(self):
        """
        The server database method for getting user list
        :return:
        """
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )
        return query.all()

    def db_active_users_list(self):
        """
        The server database method for getting active user list
        :return:
        """
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def db_login_history_list(self, username=None):
        """
        The server database method for getting logun history list
        :param username:
        :return:
        """
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip_address,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    def db_message_counter_update(self, message):
        """
        The server database method for message counter update
        :param message:
        :return:
        """
        sender = self.session.query(
            self.AllUsers).filter_by(
            name=message[FROM]).first()
        sender_raw = self.session.query(self.MessageCounter). \
            filter_by(msgs_counter_user_id=sender.id).first()

        if sender_raw:
            sender_raw.msgs_counter_sent += 1
            self.session.commit()
        else:
            record = self.MessageCounter(sender.id)
            record.msgs_counter_sent += 1
            self.session.add(record)
            self.session.commit()

        receiver = self.session.query(
            self.AllUsers).filter_by(
            name=message[TO]).first()
        receiver_raw = self.session.query(
            self.MessageCounter).filter_by(
            msgs_counter_user_id=receiver.id).first()

        if receiver_raw:
            receiver_raw.msgs_counter_received += 1
            self.session.commit()
        else:
            record = self.MessageCounter(receiver.id)
            record.msgs_counter_received += 1
            self.session.add(record)
            self.session.commit()

    def db_message_counter_list(self):
        """
        The server database method for message counter list
        :return:
        """
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.MessageCounter.msgs_counter_sent,
            self.MessageCounter.msgs_counter_received,
        ).join(self.AllUsers)
        return query.all()

    def db_message_register_update(self, message):
        """
        The server database method for message register update
        :param message:
        :return:
        """

        sender = self.session.query(
            self.AllUsers).filter_by(
            name=message[FROM]).first()
        receiver = self.session.query(
            self.AllUsers).filter_by(
            name=message[TO]).first()
        record = self.MessageRegister(message)
        record.messages_reg_from_id = sender.id
        record.messages_reg_to_id = receiver.id
        record.messages_reg_date = datetime.datetime.now()
        record.messages_reg_text = message['message_text']
        self.session.add(record)
        self.session.commit()

    def db_message_register_list(self):
        """
        The server database methodfor getting message register list
        :return:
        """
        query = self.session.query(self.MessageRegister.messages_reg_from_id,
                                   self.MessageRegister.messages_reg_to_id,
                                   self.MessageRegister.messages_reg_date,
                                   self.MessageRegister.messages_reg_text,
                                   )
        return query.all()

    def db_contacts_add(self, user_name, contact_name):
        """
        The server database method for adding contact
        :param user_name:
        :param contact_name:
        :return:
        """
        user = self.session.query(
            self.AllUsers).filter_by(
            name=user_name).first()
        contact = self.session.query(
            self.AllUsers).filter_by(
            name=contact_name).first()
        if not user:
            raise ValueError(f"Server DB : incorect user_name")
        if not contact:
            raise ValueError(f"Server DB : incorect contact_name")
        existing_contact = self.session.query(
            self.UserContacts).filter_by(
            user_id=user.id,
            contact_id=contact.id).first()
        if existing_contact:
            raise ValueError("Server DB :Contact already exists")
        new_contact = self.UserContacts(user.id, contact.id)
        self.session.add(new_contact)
        self.session.commit()

    def db_contacts_remove(self, user_name, contact_name):
        """
        The server database method for contact remove
        :param user_name:
        :param contact_name:
        :return:
        """
        user = self.session.query(
            self.AllUsers).filter_by(
            name=user_name).first()
        contact = self.session.query(
            self.AllUsers).filter_by(
            name=contact_name).first()
        existing_contact = self.session.query(
            self.UserContacts).filter_by(
            user_id=user.id,
            contact_id=contact.id).first()
        if not existing_contact:
            return
        self.session.delete(existing_contact)
        # self.session.query(self.UsersContacts).filter(self.UsersContacts.user == user.id,
        # self.UsersContacts.contact == contact.id).delete()
        self.session.commit()

    def db_contacts_list(self, username=None):
        """
        The server database method for getting contact list
        :param username:
        :return:
        """
        if username:
            user = self.session.query(
                # self.UserContacts.id,
                self.AllUsers).filter_by(name=username).one()

            query = self.session.query(
                self.UserContacts,
                self.AllUsers.name). filter_by(
                user_id=user.id).join(
                self.AllUsers,
                self.UserContacts.contact_id == self.AllUsers.id)
            return [contact[1] for contact in query.all()]
        else:
            query = self.session.query(self.UserContacts, self.AllUsers.name). join(
                self.AllUsers, self.UserContacts.contact_id == self.AllUsers.id)
            return [contact[1] for contact in query.all()]

            # query = self.session.query.(
            #     self.UserContacts.user_id.name,
            #     self.UserContacts.contact_id.name,
            # ).join(self.AllUsers.name)

            return query.all()

    def db_get_hash(self, name):
        """
        The server database method for getting hash
        :param name:
        :return:
        """
        '''Метод получения хэша пароля пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.passwd_hash

    def db_get_pubkey(self, name):
        """
        The server database method for getting pubkey
        :param name:
        :return:
        """
        '''Метод получения публичного ключа пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.pubkey


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
