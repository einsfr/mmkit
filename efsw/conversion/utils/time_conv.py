def time_str_to_seconds(time_str):
    h, m, s = [float(i) for i in time_str.split(':')]
    return h * 3600 + m * 60 + s
