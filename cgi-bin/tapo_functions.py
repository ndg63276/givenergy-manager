from PyP100 import PyP100


def get_tapo_device(device):
    p100 = PyP100.P100(device["ip"], device["username"], device["password"])
    try:
        p100.handshake()
        p100.login()
        return p100
    except:
        return None


def tapo_device_is_on(p100):
    info = p100.getDeviceInfo()
    return info["result"]["device_on"]


def switch_tapo_device(device, turn_on):
    p100 = get_tapo_device(device)
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
