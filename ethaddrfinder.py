"""Ethereum address generator and key finder

Private keys are numbers ranging from zero to
115792089237316195423570985008687907853269984665640564039457584007913129639935
or in scientific notation 1.16e+77 (a 78 digit long number) or in hex
0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff.

The public key (Ethereum address) is derived from this between zero and
1461501637330902918203684832716283019655932542975
or in scientific notation 1.46e+48 (a 48 digit long number) or in hex
0xffffffffffffffffffffffffffffffffffffffff.

For example this is a real key pair:
- 514631507655146329067041476604058508504754938497679340023711717715034542251
- 1087431988284488357839257190450193305568902695356

Or in hex notation:
- 0x1234567890abcdef01234567890abcdef01234567890abcdef01234567890ab
- 0xbe7a2305d46498e6b9634b3aaacebfb1b914c9bc

You can import the above private key in an Ethereum wallet (e.g. Metamask)
and see yourself that the wallet adress indeed will be what is shown above.


## Reverse engineering private keys from public keys

There is no known method to take a specific public key and find out the private
key - if there was, the whole point of private-public key encryption would
become moot.

The only way to find private keys for specific public keys is to try random
private keys and hope on being lucky. The chance of getting it right is one
in 1.46e+48 (a 78 digit long number).

If you don't need to have an exact match and are happy with just finding a
private key for any public key that ends in a specifix hexadecimal, your chances
are that one guess in 16 is right.

Length - hex example - number of guesses needed
1 >>> 0xf >>> 16
2 >>> 0xff >>> 256
3 >>> 0xfff >>> 4096
4 >>> 0xffff >>> 65 536
5 >>> 0xfffff >>> 1 048 576
6 >>> 0xffffff >>> 16 777 216
7 >>> 0xfffffff >>> 268 435 456
8 >>> 0xffffffff >>> 4 294 967 296

With a modern laptop that makes 5000 guesses per second you would have a 50%
chance to find a private key that ends in 4 specific hexadecimals in about 7
seconds. For 6 specific trailing hexadecimals you would need 28 minutes,
for 7 already 7,5 hours and for 8 hexadecimals as much as 5 days. For having
a 50% chance to find a private key for a public key that ends with 12 specific
hexadecimals you would already need thousands of years.

If you had 100 billion machines at your disposal, to have a 50% chance to find a
private key for *a 6specific 48 digit long public key* you would need to wait
for 4.6e+25 years, and also a nother solar system as the sun is predicted to
explode in 5e+9 years.


## Credits

This Python script was inspired by https://vanity-eth.tk/ and
https://hackernoon.com/how-to-generate-an-ethereum-address-from-private-key-using-python

"""

# Depends on custom library https://github.com/cslashm/ECPy
from ecpy.curves import Curve
from ecpy.keys import ECPrivateKey

from sha3 import keccak_256

import logging
import os
import sys
import time

FIND_SUFFIX = "a88"

def generate_key_pair(private_key: int = None) -> [int, bytes]:
    """Given private key, generate public key (Ethereum wallet address)."""

    # If no private key is given, generate one at random
    if private_key is None:
        private_key = int.from_bytes(os.urandom(32), byteorder="big")

    cv = Curve.get_curve("secp256k1")
    pv_key = ECPrivateKey(private_key, cv)
    pu_key = pv_key.get_public_key()

    concat_x_y = pu_key.W.x.to_bytes(32, byteorder="big") + \
                 pu_key.W.y.to_bytes(32, byteorder="big")

    # alternatively:
    # concat_x_y = bytes.fromhex(hex(pu_key.W.x)[2:] + \
    #                            hex(pu_key.W.y)[2:])

    public_key = keccak_256(concat_x_y).digest()[-20:]

    return private_key, public_key


def main():
    """Program entrypoint."""

    # https://docs.python.org/3/library/logging.html#levels
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # If program not running with DEBUG=1, don't log anything
    if os.environ.get('DEBUG', False) is False:
        logging.disable()

    counter = 0
    start_time = time.time()

    # initial_key = 0x01234567890abcdef01234567890abcdef01234567890abcdef01234567890aa
    # initial_key = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
    initial_key = int.from_bytes(os.urandom(32), byteorder="big")

    prefix_length = len(FIND_SUFFIX)

    print(f"Trying private keys until Ethereum address suffix matches: {FIND_SUFFIX}")
    print(f"Press Ctrl+C to abort")

    print(f"Initial private key: {hex(initial_key)}")

    try:
        while True:
            counter += 1

            # Regular progress info
            if counter % 1000 == 0:
                mid_time = time.time() - start_time
                keys_per_second = counter / mid_time
                logger.info(f"Tested {counter} keys in {mid_time:.0f} seconds "
                            f"(~{keys_per_second:.0f}/s)")

            # Generate key pair
            private_key, public_key = generate_key_pair(initial_key + counter)
            eth_addr = public_key.hex()
            logger.debug(f"private key: {hex(private_key)}")
            logger.debug(f"eth address: 0x{eth_addr}")

            # Show what key we are testing, but avoid wasting I/O bandwidth so
            # only update progress on every 10th key
            if counter % 10 == 0:
                print(f"Testing private key: {hex(private_key)}", end="\r")

            # Stop if prefix found
            if eth_addr[-prefix_length:] == FIND_SUFFIX:
                print("Success! Found key pair:")
                print(f"Private key: {hex(private_key)}")
                print(f"Ethereum wallet address: 0x{eth_addr}")
                break

    except KeyboardInterrupt:
        logger.info("Exiting per user request (CTRL+C)")
        # tell all processes to terminate and wait
        print("Quitting (CTRL+C)...")

    except Exception as error:
        logging.error(error)
        raise

    finally:
        end_time = time.time() - start_time
        keys_per_second = counter / end_time
        logger.info(f"Program ran for {end_time:.0f} seconds generating "
                    f"{counter} keys (~{keys_per_second:.0f}/s).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
