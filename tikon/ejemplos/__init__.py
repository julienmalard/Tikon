import os


def en_ejemplos(dirección):
    if os.path.splitdrive(dirección)[0]:
        return dirección

    dir_ej = os.path.split(__file__)[0]
    return os.path.join(dir_ej, dirección)
