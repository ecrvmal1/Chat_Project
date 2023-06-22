import datetime

from sqlalchemy import create_engine, Table, Column, \
    Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker

from Lesson3.common.server_variables import SERVER_DATABASE


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


    def __init__(self):
        self.db_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)
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

        # ------------ Create Tables ---------------------
        self.metadata.create_all(self.db_engine)

        #-------------- Create Mappers --------------------
        #            funct.class     table
        mapper(self.AllUsers, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)

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

# Отладка
if __name__ == '__main__':
    test_db = ServerStorage()
    # выполняем 'подключение' пользователя
    test_db.db_user_login('client_1', '192.168.1.4', 8888)
    test_db.db_user_login('client_2', '192.168.1.5', 7777)
    # выводим список кортежей - активных пользователей
    print(test_db.db_active_users_list())
    # выполянем 'отключение' пользователя
    test_db.db_user_logout('client_1')
    # выводим список активных пользователей
    print(test_db.db_active_users_list())
    # запрашиваем историю входов по пользователю
    test_db.db_login_history_list('client_1')
    # выводим список известных пользователей
    print(test_db.db_all_users_list())

