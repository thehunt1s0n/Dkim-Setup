#!/usr/bin/env python3

import argparse
import subprocess
import os

# This Script must be run as root
if os.geteuid() != 0:
    print("This script must be run as root.")
    exit(1)

# Parse arguments
parser = argparse.ArgumentParser(description="Configure OpenDKIM for a domain")
parser.add_argument("-d", "--domain", required=True, help="The domain name")
parser.add_argument("-r", "--random-number", required=True, help="A random number to use in the key table")

args = parser.parse_args()

domain = args.domain
random_number = args.random_number

# This is the base_domain variable for example: google.com, the base_domain will be: google
base_domain = domain.split('.')[0]

# Install OpenDKIM
subprocess.run(["apt-get", "update"], check=True)
subprocess.run(["apt-get", "install", "-y", "opendkim", "opendkim-tools"], check=True)
subprocess.run(["mkdir", "-p", "/etc/opendkim"], check=True)
subprocess.run(["mkdir", "-p", "/etc/opendkim/keys"], check=True)

# Configure OpenDKIM
#with open("/etc/opendkim.conf", "w") as f:
#    config_lines = [
#        "AutoRestart             Yes",
#        "AutoRestartRate         10/1h",
#        "UMask                   002",
#        "Syslog                  yes",
#        "SyslogSuccess           Yes",
#        "LogWhy                  Yes",
#        "Canonicalization        relaxed/simple",
#        "ExternalIgnoreList      refile:/etc/opendkim/trusted.hosts",
#        "InternalHosts           refile:/etc/opendkim/trusted.hosts",
#        "KeyTable                refile:/etc/opendkim/key.table",
#        "SigningTable            refile:/etc/opendkim/signing.table",
#        "Mode                    sv",
#        "PidFile                 /var/run/opendkim/opendkim.pid",
#        "SignatureAlgorithm      rsa-sha256",
#        "Socket                  inet:8891@localhost",
#        "UserID                  opendkim",
#        "Domain                  {domain}",
#        "TrustAnchorFile         /usr/share/dns/root.key",
#        "OversignHeaders         From"
#    ]
#    f.write('\n'.join(config_lines))

# Key.table config
with open("/etc/opendkim/key.table", "a") as f:
    key_table_line = f"\n{base_domain}    {domain}:{random_number}:/etc/opendkim/keys/{base_domain}.private"
    f.write(key_table_line)

# Signing.table config
with open("/etc/opendkim/signing.table", "a") as f:
    signing_table_line = f"\n*@{domain}    {base_domain}"
    f.write(signing_table_line)

# trusted.hosts config
with open("/etc/opendkim/trusted.hosts", "a") as f:
    trusted_hosts = [
        "\n127.0.0.1",
        "localhost",
        f"*.{domain}"
    ]
    f.write('\n'.join(trusted_hosts))

# Generate key using domain name as the selector
subprocess.run(["opendkim-genkey", "-b", "2048", "-d", domain, "-D", "/etc/opendkim/keys/", "-s", base_domain, "-v"], check=True)
subprocess.run(["chown", "opendkim:opendkim", f"/etc/opendkim/keys/{base_domain}.private"], check=True)

subprocess.run(["systemctl", "enable", "opendkim"], check=True)
subprocess.run(["systemctl", "start", "opendkim"], check=True)

print(f"OpenDKIM has been installed and configured for the domain {domain} with random number {random_number}.")
