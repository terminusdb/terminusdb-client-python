#!/bin/sh

[ -z "$1" ] && exec /usr/bin/python3

exec /usr/local/bin/terminusdb "$@"
