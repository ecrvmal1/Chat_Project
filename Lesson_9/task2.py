"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.

script listing at lines:  39...287
"""
import time
from tabulate import tabulate
from task1 import host_ping


def host_range_ping(echo=False):
    ip_addr_list = []
    while True:
        start_ip = input('Please enter start IP address : ')
        delta_ip = int(input('Please enter number of addresses to check : '))

        last_octet_start = int(start_ip.split('.')[3])
        last_octet_end = last_octet_start + delta_ip
        if last_octet_end > 254:
            print('incorrect IP range')
        break
    header = f'{start_ip.split(".")[0]}.{start_ip.split(".")[1]}.{start_ip.split(".")[2]}.'
    for last_octet in range(last_octet_start, last_octet_end):
        ip_addr_string = f'{header}{last_octet}'
        ip_addr_list.append(ip_addr_string)
        # print(ip_addr_string)
    time.sleep(0.5)
    return host_ping(ip_addr_list, ping_attempts=1, echo=echo)


if __name__ == '__main__':
    ip_ok, ip_not_ok = host_range_ping(echo=True)
    # print('\n Доступны адреса : \n', tabulate(ip_ok))
    # print('\n Недоступны адреса :\n', tabulate(ip_not_ok))


"""
Script Listing

(venv) user1@ubuntu:~/Desktop/chat/Lesson_9$ python task2.py
Please enter start IP address : 192.168.1.1
Please enter number of addresses to check : 240
address 192.168.1.1 Доступен
address 192.168.1.2 Не доступен
address 192.168.1.3 Не доступен
address 192.168.1.4 Не доступен
address 192.168.1.5 Не доступен
address 192.168.1.6 Не доступен
address 192.168.1.7 Не доступен
address 192.168.1.8 Не доступен
address 192.168.1.9 Не доступен
address 192.168.1.10 Не доступен
address 192.168.1.11 Не доступен
address 192.168.1.12 Не доступен
address 192.168.1.13 Не доступен
address 192.168.1.14 Не доступен
address 192.168.1.15 Не доступен
address 192.168.1.16 Не доступен
address 192.168.1.17 Не доступен
address 192.168.1.18 Не доступен
address 192.168.1.19 Не доступен
address 192.168.1.20 Не доступен
address 192.168.1.21 Не доступен
address 192.168.1.22 Не доступен
address 192.168.1.23 Не доступен
address 192.168.1.24 Не доступен
address 192.168.1.25 Не доступен
address 192.168.1.26 Не доступен
address 192.168.1.27 Не доступен
address 192.168.1.28 Не доступен
address 192.168.1.29 Не доступен
address 192.168.1.30 Не доступен
address 192.168.1.31 Не доступен
address 192.168.1.32 Не доступен
address 192.168.1.33 Не доступен
address 192.168.1.34 Доступен
address 192.168.1.35 Не доступен
address 192.168.1.36 Не доступен
address 192.168.1.37 Не доступен
address 192.168.1.38 Не доступен
address 192.168.1.39 Не доступен
address 192.168.1.40 Не доступен
address 192.168.1.41 Не доступен
address 192.168.1.42 Не доступен
address 192.168.1.43 Не доступен
address 192.168.1.44 Не доступен
address 192.168.1.45 Не доступен
address 192.168.1.46 Не доступен
address 192.168.1.47 Не доступен
address 192.168.1.48 Не доступен
address 192.168.1.49 Не доступен
address 192.168.1.50 Не доступен
address 192.168.1.51 Не доступен
address 192.168.1.52 Не доступен
address 192.168.1.53 Не доступен
address 192.168.1.54 Не доступен
address 192.168.1.55 Не доступен
address 192.168.1.56 Не доступен
address 192.168.1.57 Не доступен
address 192.168.1.58 Не доступен
address 192.168.1.59 Не доступен
address 192.168.1.60 Не доступен
address 192.168.1.61 Не доступен
address 192.168.1.62 Не доступен
address 192.168.1.63 Не доступен
address 192.168.1.64 Не доступен
address 192.168.1.65 Не доступен
address 192.168.1.66 Не доступен
address 192.168.1.67 Не доступен
address 192.168.1.68 Не доступен
address 192.168.1.69 Не доступен
address 192.168.1.70 Не доступен
address 192.168.1.71 Не доступен
address 192.168.1.72 Не доступен
address 192.168.1.73 Не доступен
address 192.168.1.74 Не доступен
address 192.168.1.75 Не доступен
address 192.168.1.76 Не доступен
address 192.168.1.77 Не доступен
address 192.168.1.78 Не доступен
address 192.168.1.79 Не доступен
address 192.168.1.80 Не доступен
address 192.168.1.81 Не доступен
address 192.168.1.82 Не доступен
address 192.168.1.83 Не доступен
address 192.168.1.84 Не доступен
address 192.168.1.85 Не доступен
address 192.168.1.86 Не доступен
address 192.168.1.87 Не доступен
address 192.168.1.88 Не доступен
address 192.168.1.89 Не доступен
address 192.168.1.90 Не доступен
address 192.168.1.91 Не доступен
address 192.168.1.92 Не доступен
address 192.168.1.93 Не доступен
address 192.168.1.94 Не доступен
address 192.168.1.95 Не доступен
address 192.168.1.96 Не доступен
address 192.168.1.97 Не доступен
address 192.168.1.98 Не доступен
address 192.168.1.99 Не доступен
address 192.168.1.100 Не доступен
address 192.168.1.101 Не доступен
address 192.168.1.102 Не доступен
address 192.168.1.103 Не доступен
address 192.168.1.104 Не доступен
address 192.168.1.105 Не доступен
address 192.168.1.106 Не доступен
address 192.168.1.107 Не доступен
address 192.168.1.108 Не доступен
address 192.168.1.109 Не доступен
address 192.168.1.110 Не доступен
address 192.168.1.111 Не доступен
address 192.168.1.112 Не доступен
address 192.168.1.113 Не доступен
address 192.168.1.114 Не доступен
address 192.168.1.115 Не доступен
address 192.168.1.116 Не доступен
address 192.168.1.117 Не доступен
address 192.168.1.118 Не доступен
address 192.168.1.119 Не доступен
address 192.168.1.120 Не доступен
address 192.168.1.121 Не доступен
address 192.168.1.122 Не доступен
address 192.168.1.123 Не доступен
address 192.168.1.124 Не доступен
address 192.168.1.125 Не доступен
address 192.168.1.126 Не доступен
address 192.168.1.127 Не доступен
address 192.168.1.128 Не доступен
address 192.168.1.129 Не доступен
address 192.168.1.130 Не доступен
address 192.168.1.131 Не доступен
address 192.168.1.132 Не доступен
address 192.168.1.133 Не доступен
address 192.168.1.134 Не доступен
address 192.168.1.135 Не доступен
address 192.168.1.136 Доступен
address 192.168.1.137 Не доступен
address 192.168.1.138 Не доступен
address 192.168.1.139 Не доступен
address 192.168.1.140 Не доступен
address 192.168.1.141 Не доступен
address 192.168.1.142 Не доступен
address 192.168.1.143 Не доступен
address 192.168.1.144 Не доступен
address 192.168.1.145 Не доступен
address 192.168.1.146 Не доступен
address 192.168.1.147 Не доступен
address 192.168.1.148 Не доступен
address 192.168.1.149 Не доступен
address 192.168.1.150 Не доступен
address 192.168.1.151 Не доступен
address 192.168.1.152 Не доступен
address 192.168.1.153 Не доступен
address 192.168.1.154 Не доступен
address 192.168.1.155 Не доступен
address 192.168.1.156 Не доступен
address 192.168.1.157 Не доступен
address 192.168.1.158 Не доступен
address 192.168.1.159 Не доступен
address 192.168.1.160 Не доступен
address 192.168.1.161 Не доступен
address 192.168.1.162 Не доступен
address 192.168.1.163 Не доступен
address 192.168.1.164 Не доступен
address 192.168.1.165 Не доступен
address 192.168.1.166 Не доступен
address 192.168.1.167 Не доступен
address 192.168.1.168 Не доступен
address 192.168.1.169 Не доступен
address 192.168.1.170 Не доступен
address 192.168.1.171 Не доступен
address 192.168.1.172 Не доступен
address 192.168.1.173 Не доступен
address 192.168.1.174 Не доступен
address 192.168.1.175 Не доступен
address 192.168.1.176 Не доступен
address 192.168.1.177 Не доступен
address 192.168.1.178 Не доступен
address 192.168.1.179 Не доступен
address 192.168.1.180 Не доступен
address 192.168.1.181 Не доступен
address 192.168.1.182 Не доступен
address 192.168.1.183 Не доступен
address 192.168.1.184 Не доступен
address 192.168.1.185 Не доступен
address 192.168.1.186 Не доступен
address 192.168.1.187 Не доступен
address 192.168.1.188 Не доступен
address 192.168.1.189 Не доступен
address 192.168.1.190 Не доступен
address 192.168.1.191 Не доступен
address 192.168.1.192 Не доступен
address 192.168.1.193 Не доступен
address 192.168.1.194 Не доступен
address 192.168.1.195 Не доступен
address 192.168.1.196 Не доступен
address 192.168.1.197 Не доступен
address 192.168.1.198 Не доступен
address 192.168.1.199 Доступен
address 192.168.1.200 Не доступен
address 192.168.1.201 Не доступен
address 192.168.1.202 Не доступен
address 192.168.1.203 Не доступен
address 192.168.1.204 Не доступен
address 192.168.1.205 Не доступен
address 192.168.1.206 Не доступен
address 192.168.1.207 Не доступен
address 192.168.1.208 Не доступен
address 192.168.1.209 Не доступен
address 192.168.1.210 Не доступен
address 192.168.1.211 Не доступен
address 192.168.1.212 Не доступен
address 192.168.1.213 Не доступен
address 192.168.1.214 Не доступен
address 192.168.1.215 Не доступен
address 192.168.1.216 Не доступен
address 192.168.1.217 Не доступен
address 192.168.1.218 Не доступен
address 192.168.1.219 Не доступен
address 192.168.1.220 Не доступен
address 192.168.1.221 Не доступен
address 192.168.1.222 Не доступен
address 192.168.1.223 Не доступен
address 192.168.1.224 Не доступен
address 192.168.1.225 Не доступен
address 192.168.1.226 Не доступен
address 192.168.1.227 Не доступен
address 192.168.1.228 Не доступен
address 192.168.1.229 Не доступен
address 192.168.1.230 Не доступен
address 192.168.1.231 Не доступен
address 192.168.1.232 Не доступен
address 192.168.1.233 Не доступен
address 192.168.1.234 Не доступен
address 192.168.1.235 Не доступен
address 192.168.1.236 Не доступен
address 192.168.1.237 Не доступен
address 192.168.1.238 Не доступен
address 192.168.1.239 Не доступен
address 192.168.1.240 Не доступен

(venv) user1@ubuntu:~/Desktop/chat/Lesson_9$ 
"""