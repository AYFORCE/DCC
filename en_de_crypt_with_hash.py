from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import hashlib

# Function to generate a key pair
def generate_key_pair():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

# Function to save a key pair to files
def save_key_pair(private_key, public_key, private_filename, public_filename):
    for key, filename in [(private_key, private_filename), (public_key, public_filename)]:
        with open(filename, 'wb') as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )) if isinstance(key, rsa.RSAPrivateKey) else f.write(key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

# Function to read the contents of a file
def read_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

# Function to calculate the hash of a file
def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

print(f"1. step\nWe start out creating 2 keysets, one named \"Customer_key\" the other named \"FORCE_signature\"")

# Generate key pairs for keyholders
keyholders = ["Customer_key", "FORCE_signature"]
private_keys = {key: generate_key_pair() for key in keyholders}
public_keys = {key: private_keys[key].public_key() for key in keyholders}

# File paths
file_path = r"C:\Users\AY\Desktop\encryption_test.txt"
hash_path = r"C:\Users\AY\Desktop\hash.txt"
decrypted_path = r"C:\Users\AY\Desktop\read_DCC.txt"

# Read confidential file
potential_DCC = read_file(file_path)

print(f"2. step\nOur confidential file looks like this\n\"\n{potential_DCC.decode()}\n\"\nimagine it was a DCC\n")

print(f"3. step\nwe now make a hash of the confidential file looking like this\n\"\n{calculate_hash(file_path).encode('utf-8')}\n\"")

# Calculate and save the hash of the confidential file
with open(hash_path, 'wb') as hash_file_pc:
    hash_file_pc.write(calculate_hash(file_path).encode('utf-8'))

print(f"4. step\nNow we encrypt the confidential file using the public \"Customer_key\"")

# Encrypt File using FORCE's public key
encrypted_text = public_keys["Customer_key"].encrypt(
    potential_DCC,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print(f"5. step\nThe encrypted confidential file looks like this\n\"\n{encrypted_text}\n\"")

print(f"6. step\nNow we sign the confidential hash using the private \"FORCE_signature\"")

# Encrypt hash using FORCE's signature private key
hash_read = read_file(hash_path)
encrypted_hash = private_keys["FORCE_signature"].sign(
    hash_read,
    padding.PKCS1v15(),
    hashes.SHA256()
)

print(f"7. step\nThe signed hash looks like this\n\"\n{encrypted_hash}\n\"")

print(f"8. step\nThese files will then be send to a customer awaiting a DCC")

# Decrypt confidential file
decrypted_text = private_keys["Customer_key"].decrypt(
    encrypted_text,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print(f"9. step\nThe customer recieving the encrypted DCC will now decrypt the file using their private \"Customer_key\" so it looks like this\n\"\n{decrypted_text.decode()}\n\"")

# Save the decrypted file
with open(decrypted_path, 'wb') as read_DCC:
    read_DCC.write(decrypted_text)

print(f"10. step\nThe customer will now verify authenticity using the public \"FORCE_signature\"")

# Verify the signature using FORCE's public key
try:
    public_keys["FORCE_signature"].verify(
        encrypted_hash,
        hash_read,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    print(f"11. step\nSignature verified. Hash is authentic.")
except Exception as e:
    print(f"11. step\nSignature verification failed. Hash may be tampered.", e)
