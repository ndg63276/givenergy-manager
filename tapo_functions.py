from PyP100 import PyP100
from user_input import tapo_ip, tapo_username, tapo_password


def get_tapo_device():
    p100 = PyP100.P100(tapo_ip, tapo_username, tapo_password)
    try:
        p100.handshake()
        p100.login()
        return p100
    except:
        return None

def tapo_device_is_on(p100):
    info = p100.getDeviceInfo()
    return info["result"]["device_on"]


def switch_tapo_device(turn_on):
    p100 = get_tapo_device()
    if p100 is None:
        return False
    if turn_on and not tapo_device_is_on(p100):
        p100.turnOn()
        return True
    elif tapo_device_is_on(p100) and not turn_on:
        p100.turnOff()
        return True
    else:
        return False
