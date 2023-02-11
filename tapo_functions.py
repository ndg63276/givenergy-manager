#!/usr/bin/python3

from PyP100 import PyP100
from user_input import tapo_ip, tapo_username, tapo_password


def getTapoPlug():
    p100 = PyP100.P100(tapo_ip, tapo_username, tapo_password)
    p100.handshake()
    p100.login()
    return p100


def tapoPlugIsOn(p100):
    info = p100.getDeviceInfo()
    return info["result"]["device_on"]


def switchTapoPlug(p100, turnOn):
    if turnOn:
        p100.turnOn()
    else:
        p100.turnOff()
