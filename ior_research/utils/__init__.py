import ior_research.utils

from ior_research.utils.aes import ControlNetAES
from ior_research.utils.proxy import ProxyClient, ProxyServer
import math, random

from random import randrange, getrandbits

def is_prime(n, k=128):
    """ Test if a number is prime
        Args:
            n -- int -- the number to test
            k -- int -- the number of tests to do
        return True if n is prime
    """
    # Test if n is not even.
    # But care, 2 is prime !
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    # find r and s
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    # do k tests
    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True
def generate_prime_candidate(length):
    """ Generate an odd integer randomly
        Args:
            length -- int -- the length of the number to generate, in bits
        return a integer
    """
    # generate random bits
    p = getrandbits(length)
    # apply a mask to set MSB and LSB to 1
    p |= (1 << length - 1) | 1
    return p

def generate_prime_number(length=1024):
    p = 4
    # keep generating while the primality test fail
    while not is_prime(p, 128):
        p = generate_prime_candidate(length)
    return p

def countPrimitiveRoots(p):
    result = 1
    for i in range(2, p, 1):
        n = math.gcd(i, p)
        if (n == 1):
            result = i

    return result

def generateDiffieHellmanKeys():
    n = generate_prime_number()
    public = 5
    a = random.randint(1,20)
    b = random.randint(1,20)

    a_public = int(math.pow(public, a) % n)
    b_public = int(math.pow(public,b) % n)

    print(a_public, b_public)

    key1 = int(math.pow(b_public, a) % n)
    key2 = int(math.pow(a_public, b) % n)
    print(key1 == key2)
    print(key1, key2)

if __name__ == "__main__":
    generateDiffieHellmanKeys()