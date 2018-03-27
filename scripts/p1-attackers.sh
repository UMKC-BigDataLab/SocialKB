#!/bin/bash

# Anas Katib, July 23, 2016
#
# Usage: ./p1-attackers.sh <mar_out_file>
#
#	Retrieves the attacker id for the attackers with probability 1.0000
#


grep 1.0000$'\t'attacker $1 | cut -d '(' -f2 | cut -d ')' -f1
