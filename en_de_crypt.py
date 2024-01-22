from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
import base64

def generate_key_pair():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

def save_key_pair(private_key, public_key, private_filename, public_filename):
    # Save the private key
    with open(private_filename, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save the public key
    with open(public_filename, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def load_key_pair(private_filename):
    with open(private_filename, 'rb') as f:
        private_key_data = f.read()
        private_key = serialization.load_pem_private_key(
            private_key_data,
            password=None,
            backend=default_backend()
        )

    return private_key, private_key.public_key()

# Function to read and return the content of the encrypted file
def read_encrypted_file(file_path):
    with open(file_path, 'rb') as file:
        encrypted_content = file.read()
    return encrypted_content

try:
    # Load the key pair from the file
    private_key, public_key = load_key_pair('private_key.pem')
except FileNotFoundError:
    # Generate and save the key pair
    private_key = generate_key_pair()
    public_key = private_key.public_key()
    save_key_pair(private_key, public_key, 'private_key.pem', 'public_key.pem')

file_path = r"C:\Users\AY\Desktop\encryption_test.txt"

# Read content from the file
with open(file_path, 'rb') as file:
    potential_DCC = file.read()

# Encrypt using the recipient's public key
encrypted_text = public_key.encrypt(
    potential_DCC,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

encrypted_file_path = r"C:\Users\AY\Desktop\encrypted_test_text.txt"  # Replace with your desired path
#with open(encrypted_file_path, 'wb') as encrypted_file:
#    encrypted_file.write(encrypted_text)

# Decrypt using the private key
decrypted_text = private_key.decrypt(
    encrypted_text,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

read_encrypted_text = read_encrypted_file(encrypted_file_path)

# Decrypt using the private key
read_decrypted_text = private_key.decrypt(
    read_encrypted_text,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Print the results
print("Original text:")
print(potential_DCC.decode('utf-8'))

print("\nEncrypted text:")
print(base64.b64encode(encrypted_text).decode('utf-8'))

print("\nread_Encrypted text:")
print(base64.b64encode(read_encrypted_text).decode('utf-8'))

print("\nDecrypted text:")
print(decrypted_text.decode('utf-8'))

print("\nread_Decrypted text:")
print(read_decrypted_text.decode('utf-8'))