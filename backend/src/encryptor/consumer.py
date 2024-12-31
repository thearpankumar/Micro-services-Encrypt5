import pika
import sys
import os
import time
import ctypes

# Load the CUDA encryption and decryption libraries
cuda_enc_lib = ctypes.CDLL('/app/Encrypt5_SecurityProtocols/build/padlibencrypt.so')
cuda_dec_lib = ctypes.CDLL('/app/Encrypt5_SecurityProtocols/build/padlibdecrypt.so')

# Define the argument types for the encrypt_files function
cuda_enc_lib.encrypt_files.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]

# Define the argument types for the decrypt_files function
cuda_dec_lib.decrypt_files.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]

def encrypt_files(input_file, encrypted_file, key_file):
    """
    Encrypts a file using the CUDA encryption library.
    """
    # Call the CUDA function
    cuda_enc_lib.encrypt_files(input_file.encode(), encrypted_file.encode(), key_file.encode())

def decrypt_files(encrypted_file, key_file, decrypted_file):
    """
    Decrypts a file using the CUDA decryption library.
    """
    # Call the CUDA function
    cuda_dec_lib.decrypt_files(encrypted_file.encode(), key_file.encode(), decrypted_file.encode())

def main():
    """
    Consumes messages from RabbitMQ and starts the encryption process.
    """
    # RabbitMQ connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # Declare the queue
    queue_name = os.environ.get("ENC_FILE_QUEE")
    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        """
        Callback function to process messages from RabbitMQ.
        """
        try:
            # Decode the message
            message = body.decode()
            print(f"Received message: {message}")

            # Parse the message (expected format: "input_file,encrypted_file,key_file")
            input_file, encrypted_file, key_file = message.split(',')

            # Start the encryption process
            print(f"Encrypting file: {input_file} -> {encrypted_file}")
            encrypt_files(input_file, encrypted_file, key_file)
            print(f"Encryption completed: {encrypted_file}")

            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {e}")
            # Reject the message in case of an error
            ch.basic_nack(delivery_tag=method.delivery_tag)

    # Set up the consumer
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)