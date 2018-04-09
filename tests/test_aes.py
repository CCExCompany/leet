import unittest
import random
import string
from crypto import AESCipher

class Test(unittest.TestCase):
    def test_cipher(self):
        cipher = AESCipher(None)

        message = ''.join(random.choice(string.ascii_uppercase + string.digits + 
string.ascii_lowercase) for _ in range(100))
        key = ''.join(random.choice(string.ascii_uppercase + string.digits + 
string.ascii_lowercase) for _ in range(32))
        
        # check cipher without key
        try:
            C = cipher.encrypt(message)
            self.assertFail()
        except Exception as err:
            self.assertEqual('Invalid key', str(err))

        cipher.key = key
        C = cipher.encrypt(message)
        M = cipher.decrypt(C)
        self.assertEqual(M, message)


if __name__ == '__main__':
    unittest.main()
        

if __name__ == '__main__':
    unittest.main()
