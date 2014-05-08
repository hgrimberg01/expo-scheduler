#!/usr/bin/env bash

for ((i = 1; i <= 100; i++)); do
        echo "--- Iteration #$i: $(date) ---"
            time python3 ./attempt2.py
        done 2>&1 | tee timing.log
