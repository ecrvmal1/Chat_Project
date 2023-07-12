import sys
import os
import unittest
import json
sys.path.append(os.path.join(os.getcwd(), '../Lesson3'))

from server.server_utils import get_message, send_message


class Test_Sock():
    """
    Класс эмулирует поведение Socket, включая функции recv и send
    """
    def __init__(self):
        self.sock_sent_msg = None
        self.sock_received_msg = {'test': "test message"}

    def recv(self, packet_length):
        """
        Функция Позволяет тестировать поведение функций, включающих Socket.recv
        берет self.sock_received_msg ,
        делает > json.dumps > bynary string   ( Эмуляция работы функции Socket.recv )
        :param packet_length: max TCP package length;
        :return Bynary string:
        """
        json_obj = json.dumps(self.sock_received_msg)
        return json_obj.encode('utf-8')

    def send(self, byte_string):
        """
        Функция Позволяет тестировать поведение функций, включающих Socket.send
        берет byte_string ,
        восстанавливает > decode('utf-8) > json.loads
        записывает в переменную self.sock_sent_msg словарь , получающийся при декодировании Byte_string.
        :param byte_string:
        :return: None
        """
        json_string = byte_string.decode('utf-8')
        self.sock_sent_msg = json.loads(json_string)


class TestSendRcv(unittest.TestCase):

    def test_send_msg(self):
        """
        функция тестирования функции send_message
        Класс Test_Sock определяет функцию sock.send,
        которая декодирует передаваемое сообщение  в предполагаемый словарь
        записывает пердполагаемый передаваемый словарь в переменную self.sock_sent_msg
        далее сравнивеат переданный словарь "test_message" c декодированным словарем полученным из self.send
        :return:
        """
        sock = Test_Sock()
        test_message = {'response': 200}
        send_message(sock, test_message)
        self.assertEqual(sock.sock_sent_msg, test_message)

    def test_get_message(self):
        """
        функция тестирования функции get_message
        Класс Test_Sock определяет функцию self.recv,
        Функция get_message
        вызывает функцию  self.recv, которая врзвращает бинарнусю строку , соответсвующую тестовому словарю test_dict
        далее сравниваем рузельтат функции get_message и тестовый словарь
        :return:
        """
        sock = Test_Sock()
        test_dict = get_message(sock)
        self.assertEqual(sock.sock_received_msg, test_dict)


if __name__ == '__main__':
    unittest.main()








