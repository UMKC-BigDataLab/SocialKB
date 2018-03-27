#!/bin/bash


cat /etc/dansguardian/blacklists/{hacking,malware,phishing,virusinfected}/urls  | sort | uniq > urls.txt
cat /etc/dansguardian/blacklists/{hacking,malware,phishing,spyware,virusinfected}/domains  | sort | uniq > domains.txt




