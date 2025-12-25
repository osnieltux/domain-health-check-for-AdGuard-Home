#!/bin/bash

# Script to open browser tabs for manual verification

# Assuming results.txt has the domains

while IFS= read -r line; do
    if [[ $line == ok* ]]; then
        domain=$(echo $line | cut -d' ' -f2)
        brotab open $domain
        echo "Opened $domain. Press Enter to block, or open another tab to skip."
        read
    fi
done < results.txt