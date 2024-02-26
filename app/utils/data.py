def dict_without_key(d, key):
    new_d = d.copy()
    try:
        new_d.pop(key)
    except:
        pass
    return new_d
