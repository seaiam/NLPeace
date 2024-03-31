#!/bin/bash

binary_name="more_simple_api"

binary_path="../target/debug/more_simple_api"

pkill -f $binary_name

sleep 10

$binary_path &

echo "$binary_name restarted successfully."
