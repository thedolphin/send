#!/bin/bash

curl -X PUT --data-binary @config.json --unix-socket /var/run/control.unit.sock :/config
