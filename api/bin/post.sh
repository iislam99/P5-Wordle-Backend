#!/bin/sh

http --verbose POST localhost:5000/words/ @"$1"
