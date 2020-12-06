from ior_research.utils.aes import ControlNetAES
from ior_research.utils.proxy import ProxyClient, ProxyServer
import math

def countPrimitiveRoots(p):
    result = 1
    for i in range(2, p, 1):
        n = math.gcd(i, p)
        if (n == 1):
            result = i

    return result
def generateDiffieHellmanKeys():
    n = 10
    public = countPrimitiveRoots(n)
    a = 15
    b = 10

    print(public)
    a_public = math.pow(public, a) % n
    b_public = math.pow(public,b) % n

    print(a_public, b_public)

    key1 = int(math.pow(b_public, a) % n)
    key2 = int(math.pow(a_public, b) % n)

    print(key1, key2)

if __name__ == "__main__":
    generateDiffieHellmanKeys()