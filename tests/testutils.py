import random
import string


def random_string(l):
    return "".join(random.choice(string.ascii_letters) for i in range(l))