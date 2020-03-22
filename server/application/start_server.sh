#!/bin/bash
kill $(lsof -t -i:5000)
python server.py &
