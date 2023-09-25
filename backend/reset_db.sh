#!/bin/bash

source_dir="db_clean"
destination_dir="."

file_to_copy="db.sqlite3"

if [ -e "$source_dir/$file_to_copy" ]; then
    cp "$source_dir/$file_to_copy" "$destination_dir/"

    echo "File '$file_to_copy' copied from $source_dir to $destination_dir."
else
    echo "File '$file_to_copy' does not exist in $source_dir."
fi