def assemble(sign, s_name, r_name, length, msg):
    sign = sign.encode('utf-8')
    s_name = s_name.encode('utf-8')
    r_name = r_name.encode('utf-8')
    length = str(length).encode('utf-8')
    msg = msg.encode('utf-8')
    package = sign + b' ' + s_name + b' ' + r_name + b' ' + length + b' ' + msg
    return package

def analyze(package):
    sign, s_name, r_name, length, msg = package.split(b' ', 4)
    sign = sign.decode('utf-8')
    s_name = s_name.decode('utf-8')
    r_name = r_name.decode('utf-8')
    length = int(length.decode('utf-8'))
    return sign, s_name, r_name, length, msg

