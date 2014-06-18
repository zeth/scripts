"""
Encrypted data storage.
-----------------------

The class DataStorage has a save method which takes your application data 
as a string of any length and then saves it, the load method can then 
retrieve the string. 

For further details, read the documentation below.

"""

# Standard library modules
from __future__ import division
from os import urandom
import sys
import hashlib
from base64 import b64encode, b64decode

# PyCrypto module.
try:
    from Crypto.Cipher import AES as DEFAULT_ALGORITHM

except ImportError:
    print "You need the PyCrypto module installed."
    print """Get it from your package manager 
    or from http://pypi.python.org/pypi/pycrypto/."""
    sys.exit(1)

class DataStorage(object):
    """The class provides encrypted data storage from the application's data.

    Here is an example of saving the data:

    >>> from cocrypto import DataStorage, _TEST_DATA
    >>> data = DataStorage()
    >>> data.save(_TEST_DATA, 'dickens.data', 'dickens.key')

    Here is an example of loading back the data.

    >>> from cocrypto import DataStorage, _TEST_DATA
    >>> new_data = DataStorage()
    >>> new_data.load('dickens.data', 'dickens.key')
    >>> new_data.text == _TEST_DATA
    True

    You can remove the test data when you are finished.

    >>> import os; os.remove('dickens.data'); os.remove('dickens.key')

    The following explains the how the default approach is implemented.

    Saving the data produces a data file and a key file. 

    Key files are intended for one-time encryption. When your application 
    saves the data again, and thus re-encrypts the data, a new key file is 
    generated. So the key file and data file must match. A copy of an older key 
    is useless with a newer version of the data file.

    The data file is encrypted using the AES algorithm and a 256 bit key. The 
    first line of the data file contains an additional 256 bit unique shared 
    value. 

    The key file contains:
        * the same 256 bit value that is also in the datafile,
        * the 256 bit encryption key and a 256 bit initialization vector (IV),
        * a 512 bit hash of the data file,
        * a 512 bit hash of the key file.

    For the data to be loaded, the following conditions must be true:
        * both files must contain the same 256 bit unique shared value,
        * the encryption key and IV in the key file need to be correct,
        * both files must not have been modified,
        * the correct encryption algorithm and encryption mode need to be set.
    
    """
    def __init__(self,
                 hash_algorithm = 'sha512',
                 block_algorithm = 'default',
                 mode = 'CFB'):
        """Initiate the Data Storage.

        Choosing a good combination of block_algorithm and mode operation is
        a somewhat of a specialist art. If you set these arguments incorrectly
        then it may be possible to read the data without the key. This makes
        the whole exercise pointless.
        
        Unless you are an encryption buff, stick to the default __init__ 
        arguments.  
        
        Available hash algorithms are md5, sha1, sha224, sha256, sha384, 
        and sha512. Some of these have known hash collision weaknesses or are 
        completely cracked.
        
        Available block algorithms are:
        AES, ARC2, ARC4, Blowfish, CAST, DES, DES3, IDEA, RC5, XOR
        
        Some of these are cracked or useless.
        
        Available modes are: 
        CBC, CFB, CTR, ECB, OFB, PGP
          
        Modes are explained at: 
        http://en.wikipedia.org/wiki/Block_cipher_mode_of_operation
        
        Some modes, e.g. ECB, are not very secure.

        >>> from cocrypto import DataStorage, DEFAULT_ALGORITHM
        >>> data = DataStorage()
        >>> data.block_algorithm == DEFAULT_ALGORITHM
        True
        >>> data.mode == DEFAULT_ALGORITHM.MODE_CFB
        True
        >>> from hashlib import sha512
        >>> data.hasher == sha512
        True
        
        """
        # Set the encryption algorithms.
        self.hasher = getattr(hashlib, hash_algorithm)
        self.block_algorithm = DEFAULT_ALGORITHM
        if block_algorithm != 'default':
            algorithm_module = 'Crypto.Cipher.' + block_algorithm
            self.block_algorithm = __import__(algorithm_module)            
        mode_string = 'MODE_' + mode
        self.mode = getattr(self.block_algorithm, mode_string)

        # 
        self.key = None
        self.vector = None
        self.unique_name = None
        self.cipher = None
        self.text = None


    def save(self, 
             text, 
             filename = 'datafile.ddf',
             key_filename = 'datafile.key'
             ):
        """Save the data to disk.
        
        >>> from cocrypto import DataStorage, _TEST_DATA
        >>> data = DataStorage()
        >>> data.save(_TEST_DATA, 'dickens.data', 'dickens.key')
        >>> import os; os.remove('dickens.data'); os.remove('dickens.key')
        
        """
        self.text = text
        self._create_key()
        self._encrypt()
        data_file = open(filename, 'w')
        data_file.write(self._create_data_file())
        key_file = open(key_filename, 'w')
        key_file.write(self._create_key_file())
                
    def load(self,
             filename = 'datafile.ddf',
             key_filename = 'datafile.key'
             ):
        """Load the data from disk.
        
        >>> from cocrypto import DataStorage, _TEST_DATA
        >>> data = DataStorage()
        >>> data.save(_TEST_DATA, 'dickens.data', 'dickens.key')
        >>> new_data = DataStorage()
        >>> new_data.load('dickens.data', 'dickens.key')
        >>> new_data.text == _TEST_DATA
        True
        >>> import os; os.remove('dickens.data'); os.remove('dickens.key')

        """
        # Open the files
        data = open(filename, 'r').readlines()
        key_data = open(key_filename, 'r').readlines()
        # Check the files have not been tamered with.
        self._check_files(data, key_data)
        # Get out the various parts
        self.key = b64decode(key_data[2].rstrip())
        self.vector = b64decode(key_data[3].rstrip())
        self.cipher = data[2].rstrip()
        # Decrypt the data
        self._decrypt()

    def _sign(self, text):
        """Create a hash of a given text.
        
        You should not need to call this method directly.
        save() uses this to create signatures.
        load() uses this to check the signatures.
        
        >>> from cocrypto import DataStorage, _TEST_DATA
        >>> data = DataStorage()
        >>> data._sign(_TEST_DATA)
        'HrQGl1FJIJZOty1NAkTGzTvnzPO3K+KtKSfLEDXcrrzpB5ddMwaujATMlcbq/9VkcL3hp+imf/3oJ2NgFjyujQ=='
        
        """
        secure_hash = self.hasher()
        secure_hash.update(text)
        return b64encode(secure_hash.digest())

    def _create_key(self, length = 16):
        """Create the key, vector and unique shared value.
        
        You should not need to call this method directly.
        save() uses this to create new one-time use values.
        
        >>> from cocrypto import DataStorage, _TEST_DATA
        >>> data = DataStorage()
        >>> data._create_key()
        >>> len(data.key)
        16
        >>> len(data.vector)
        16
        >>> len(data.unique_name)
        16
        
        """
        self.key = urandom(length) 
        self.vector = urandom(length)
        self.unique_name = urandom(length)

    def _encrypt(self):
        """Encrypt the data.

        You should not need to call this method directly.
        save() uses this to encrypt the data. 
        
        Note, apart for debug and testing purposes, don't set the key, vector
        and unique values manually (like below). Instead use _create_key() to
        create new one-time use values.

        >>> from cocrypto import DataStorage, _TEST_DATA
        >>> data = DataStorage()
        >>> data.key = 'abcderghijklmnop'
        >>> data.vector = 'qrstuvwxyz123456'
        >>> data.unique_name = 'qazwsxedcrfvtgby'
        >>> data.text = _TEST_DATA
        >>> data._encrypt()
        >>> data.cipher == 'dYHaoLzvcW0OXFg47Dtgs0g3R/3XEEcp+yVA8KzBJMtoaXtiYuDTnONLihHbC1j6bXIsi+ssSuphcJ2By6yoD1WwD4MnGGPZg8fsXXZE4apI7ErPIxvqmBpUoE3AKNNGevQrbWU6Eov9mTJRmNEx/AURWeaY8EmoVQieYqRmYWDczDLQWHDqnW/+yc/ittk0lXPY2MSMHCLpKIvj8twdP56B07iXrbIfetdV7fTzQt8AJJRN/x6Gw9S/NjRn+lSG2Ux2/C9Wn/cRddOriX0qBcyf3Rj9+5Y8pQJoljcxSYzMfU3A8IKCqiOKxOVPgfMp0xYGqW8EJn6g6RzSHRmgHVZkPMttIJcpf12pLlOCJLmzFxyxsRPaWQbqDXM0T4f0KPaCsRU7u7REYdgWhwlJWxS7eF38zQvsKYV0spjI3mAiPN1vyRYz5sMI5Ydv1imI5bULNkOH25Lt78IXU7wBAxlgiIJu3ijbIhCIMKcX4JvH18aC9MOQtb45D3s/A14A7oYvMsvJprkD5Wgk2kO5TJMsFNnCKwbHdXpasCEJXC3DyIOCcHa0MYEcIKPAvkXQ'
        True

        """
        text = str(len(self.text)) + '\n' + self.text
        # Pad the text into a multiple of 16."""
        length = len(text)
        if (length / 16) != (length // 16):    
            multiples_required = (length // 16) + 1
            length_required = multiples_required * 16
            extra_length = length_required - length
            text = text + extra_length * "X"

        # Create the encrypter object         
        encrypter = self.block_algorithm.new(self.key, 
                                             self.mode, 
                                             self.vector)        
        
        # Encrypt the text
        self.cipher = b64encode(encrypter.encrypt(text))


    def _decrypt(self):
        """Decrypt the files.

        You should not need to call this method directly.
        load() uses this to decrypt the data. 

                
        >>> from cocrypto import DataStorage, _TEST_DATA
        >>> data = DataStorage()
        >>> data._create_key() 
        >>> data.text = _TEST_DATA
        >>> data._encrypt()
        >>> new_data = DataStorage()
        >>> new_data.key = data.key
        >>> new_data.vector = data.vector
        >>> new_data.unique_name = data.unique_name
        >>> new_data.cipher = data.cipher
        >>> new_data._decrypt()
        >>> new_data.text == _TEST_DATA
        True
        
        """
        # Create the decrypter object         
        decrypter = self.block_algorithm.new(self.key, 
                                             self.mode, 
                                             self.vector)   
        
        # decrypt the text
        plain_text = decrypter.decrypt(b64decode(self.cipher))
        head, tail = plain_text.split('\n', 1)
        self.text = tail[0:int(head)]

    def _check_files(self, data_file, key_file): 
        """Check that the unique value and hashes are correct.
        
        You should not need to call this method directly.
        load() uses this to check the data has not been tampered with. 

        >>> from cocrypto import DataStorage, _TEST_DATA
        >>> data = DataStorage()
        >>> data.save(_TEST_DATA, 'dickens.data', 'dickens.key')
        >>> new_data = DataStorage()
        >>> data = open('dickens.data', 'r').readlines()
        >>> key_data = open('dickens.key', 'r').readlines()
        >>> new_data._check_files(data, key_data)
        True
        >>> import os; os.remove('dickens.data'); os.remove('dickens.key')
        
        """        
        # Test we have the right key by testing the unique names
        if data_file[1] != key_file[1]:
            print """You do have the correct datafile/ keyfile combination."""
            sys.exit(1)

        # Test the keyfile hash
        top_part = ""
        for line in key_file[1:5]:
            top_part += line
        if key_file[5].rstrip() != self._sign(top_part):
            print """The key may have been altered."""
            sys.exit(1)

        # Test the file hash
        if key_file[4].rstrip() != self._sign(data_file[2].rstrip()):
            print """The file may have been altered."""
            sys.exit(1)
            
        # Files are all good
        return True

    def _create_data_file(self):
        """Create the data file.
        
        You should not need to call this method directly.
        save() uses this to create the data file. 
        
        >>> from cocrypto import DataStorage, _TEST_DATA
        >>> data = DataStorage()
        >>> data.text = _TEST_DATA
        >>> data._create_key()
        >>> data._encrypt()
        >>> len(data._create_data_file().splitlines())
        4
        
        """
        # Unique name
        data_text = b64encode(self.unique_name) + "\n"
        # Encrypted data
        data_text += self.cipher + "\n"

        data_text = "-----BEGIN CONTACTS DIRECTORY DATA FILE-----\n" + \
            data_text + "-----END CONTACTS DIRECTORY DATA FILE-----\n"
        return data_text

    def _create_key_file(self):
        """Create a key file.
        
        You should not need to call this method directly.
        save() uses this to create the key file. 

        >>> from cocrypto import DataStorage, _TEST_DATA
        >>> data = DataStorage()
        >>> data.text = _TEST_DATA
        >>> data._create_key()
        >>> data._encrypt()
        >>> len(data._create_key_file().splitlines())
        7
        
        """
        # Unique name
        key_text = b64encode(self.unique_name)  + "\n"
        # Key
        key_text += b64encode(self.key)  + "\n"
        # Initialization vector
        key_text += b64encode(self.vector) + "\n"
        # Hash of text
        key_text += self._sign(self.cipher) + "\n"
        # Hash of key file
        key_text += self._sign(key_text) + "\n"
        key_text = "-----BEGIN CONTACTS DIRECTORY PRIVATE KEY-----\n" + \
            key_text + "-----END CONTACTS DIRECTORY PRIVATE KEY-----\n"        
        return key_text

def main():
    """Run doctests when called directly."""
    _test()

def _test():
    """Doctests, returns nothing if all tests past.
    use python cocrypto -V at the command line for verbose output."""
    import doctest
    return doctest.testmod()

_TEST_DATA = """It was the best of times, it was the worst of times, 
it was the age of wisdom, it was the age of foolishness,
it was the epoch of belief, it was the epoch of incredulity,
it was the season of Light, it was the season of Darkness,
it was the spring of hope, it was the winter of despair,
we had everything before us, we had nothing before us,
we were all going direct to Heaven, we were all going direct
the other way."""

# start the ball rolling
if __name__ == "__main__": 
    main()

