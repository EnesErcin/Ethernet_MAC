def rvrs_bits(n, no_of_bits = 8):
    result = 0
    for i in range(no_of_bits):
        result <<= 1
        result |= n & 1
        n >>= 1
    return result