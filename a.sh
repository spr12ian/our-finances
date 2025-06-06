#!/bin/bash


db_filename="our_finances.sqlite"
if [ -f "${db_filename}" ]; then
    echo rm -fv "${db_filename}"
    rm -fv "${db_filename}" >/dev/null
fi


rm -fv ./*.log >/dev/null

./do_it_all.sh >do_it_all.log 2>do_it_all_error.log

# Check if the file exists and its size is zero
if [ -f "do_it_all_error.log" ] && [ ! -s "do_it_all_error.log" ]; then
    rm -fv "do_it_all_error.log"
    echo "do_it_all_error.log was empty and has been removed."
else
    echo "do_it_all_error.log exists and is not empty."
    echo "Please check the log file for details."
fi
