from PyP100 import PyP100
from user_input import tapo_ip, tapo_username, tapo_password


def get_tapo_device():
    p100 = PyP100.P100(tapo_ip, tapo_username, tapo_password)
    p100.handshake()
    p100.login()
    return p100


def tapo_device_is_on(p100):
    info = p100.getDeviceInfo()
    return info["result"]["device_on"]


def switch_tapo_device(p100, turn_on):
    if turn_on:
        p100.turnOn()
    else:
        p100.turnOff()
