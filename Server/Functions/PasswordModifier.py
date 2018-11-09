def encrypt(password):
    encryptPassword = ""
    for i in password:
        encryptPassword += chr((ord(i) + 77) * 94 + 33)
    return encryptPassword