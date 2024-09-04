#!/usr/bin/env python3

import os
import sys
import subprocess

def add_user(username, password):
    """Add a new system user and set their password."""
    try:
        # Verify if the user already exists
        check_user = subprocess.run(['id', '-u', username], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check_user.returncode != 0:
            # User doesn't exist, proceed with creation
            subprocess.run(['sudo', 'useradd', '-m', '-s', '/bin/bash', username], check=True)
            # Update password for the user
            subprocess.run(['sudo', 'chpasswd'], input=f'{username}:{password}', text=True, check=True)
            print(f"User {username} has been successfully created.")
        else:
            print(f"User {username} already exists.")
    except subprocess.CalledProcessError as err:
        print(f"Failed to create user: {err}")
        sys.exit(1)

def setup_maildir(username):
    """Set up Maildir structure in the user's home directory."""
    maildir_path = f'/home/{username}/Maildir'
    if not os.path.isdir(maildir_path):
        try:
            # Create necessary directories for Maildir
            subprocess.run(['sudo', '-u', username, 'mkdir', '-p', f'{maildir_path}/cur', f'{maildir_path}/new', f'{maildir_path}/tmp'], check=True)
            # Adjust permissions for the Maildir
            subprocess.run(['sudo', 'chown', '-R', f'{username}:{username}', maildir_path], check=True)
            subprocess.run(['sudo', 'chmod', '-R', '700', maildir_path], check=True)
            print(f"Maildir structure created for user {username} and permissions set.")
        except subprocess.CalledProcessError as err:
            print(f"Failed to create Maildir: {err}")
            sys.exit(1)
    else:
        print(f"Maildir structure already exists for user {username}.")

def main():
    if len(sys.argv) != 3:
        print("Usage: script.py <username> <password>")
        sys.exit(1)

    user = sys.argv[1]
    passwd = sys.argv[2]

    add_user(user, passwd)
    setup_maildir(user)

if __name__ == "__main__":
    main()
