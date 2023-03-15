#!/usr/bin/env python3

import cgi
import json
import sys
import os

import cgitb
cgitb.enable()

filename = "user_input.json"

def readFile():
	with open(filename, "r") as f:
		j = json.load(f)
	return j


def writeFile(data):
	json_object = json.loads(data)
	with open(filename, "w") as f:
		f.write(json.dumps(json_object, indent=4))
	return {"success": True}


if __name__ == "__main__":
	output = {}
	request_method = os.environ["REQUEST_METHOD"]
	if request_method == "GET":
		output = readFile()
	elif request_method == "POST":
		content_length = int(os.environ["CONTENT_LENGTH"])
		request_body = sys.stdin.read(content_length)
		output = writeFile(request_body)

	print("Content-Type: application/json")
	print()
	print(json.dumps(output, default=str))
