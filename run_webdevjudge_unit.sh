#!/bin/bash

# Check for the correct number of arguments.

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <display_num> <start_line> <end_line>"
    echo "Example: $0 100 1 10"
    exit 1
fi

DISPLAY_NUM=$1
START_LINE=$2
END_LINE=$3

# Validate arguments.
if [ "$START_LINE" -gt "$END_LINE" ]; then
    echo "Error: start_line cannot be greater than end_line"
    exit 1
fi

if [ ! -f "web_unit.txt" ]; then
    echo "Error: web_unit.txt not found"
    exit 1
fi

export DISPLAY=:${DISPLAY_NUM}
export SCREEN_WIDTH=1920
export SCREEN_HEIGHT=1080

echo "Starting Xvfb on display :${DISPLAY_NUM}"
Xvfb :${DISPLAY_NUM} -screen 0 ${SCREEN_WIDTH}x${SCREEN_HEIGHT}x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
sleep 2 # Wait for Xvfb to start.

# Cleanup function to kill background processes.
cleanup() {
    echo "Cleaning up..."
    if [ ! -z "$XVFB_PID" ]; then
        echo "Stopping Xvfb..."
        kill $XVFB_PID
    fi
    exit
}

# Set a trap to call cleanup on exit.
trap cleanup SIGINT SIGTERM

echo "Processing web tasks from line $START_LINE to $END_LINE of web_unit.txt"
for ((i=START_LINE; i<=END_LINE; i++)); do
    web_dir=$(sed "${i}q;d" web_unit.txt)
    if [ -z "$web_dir" ]; then
        echo "Warning: Empty line at $i in web_unit.txt, skipping..."
        continue
    fi
    echo "==========================="
    echo "Processing web directory $i: $web_dir"
    echo "==========================="

    tasks_file_path="$web_dir/tasks.txt"

    if [ ! -f "$tasks_file_path" ]; then
        echo "Error: tasks.txt not found at $tasks_file_path"
        continue
    fi

    index_html_path="$web_dir/web.html"
    if [ ! -f "$index_html_path" ]; then
        echo "Error: index.html not found at $index_html_path"
        continue
    fi

    echo "Processing tasks from $tasks_file_path"
    while IFS= read -r task_dir; do
        if [ -z "$task_dir" ]; then
            echo "Warning: Empty line in $tasks_file_path, skipping..."
            continue
        fi

        echo "--- Processing task: $task_dir ---"
        python3 run_gui_agent.py --base_dir "$task_dir" --webdev_unit

        # Check the exit status of the agent.
        if [ $? -ne 0 ]; then
            echo "Process task: $task_dir with error"
        else
            echo "Task completed successfully: $task_dir"
        fi
    done < "$tasks_file_path"

    # Pause between web directories.
    if [ $i -lt $END_LINE ]; then
        sleep 1
    fi
done

# Final cleanup.
cleanup
    