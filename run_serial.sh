#!/bin/bash

# Check for the correct number of arguments.
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <display_num> <start_line> <end_line> <worker_id>"
    echo "Example: $0 99 1 10 0"
    exit 1
fi

DISPLAY_NUM=$1
START_LINE=$2
END_LINE=$3
WORKER_ID=$4
NEXTJS_WORKSPACE="workspace/workspace_${WORKER_ID}"
NEXTJS_PORT=$((3000 + WORKER_ID))
CURRENT_DIR=$(pwd)

# Validate arguments.
if [ "$START_LINE" -gt "$END_LINE" ]; then
    echo "Error: start_line cannot be greater than end_line"
    exit 1
fi

# Check if the pre-configured Next.js workspace directory exists.
if [ ! -d "$NEXTJS_WORKSPACE" ]; then
    echo "Error: Next.js workspace '$NEXTJS_WORKSPACE' not found."
    echo "Please create and configure it manually before running the script."
    echo "You can use 'bash setup_nextjs_env.sh $NEXTJS_WORKSPACE' to set it up."
    exit 1
fi

# Check if webs.txt exists.
if [ ! -f "webs.txt" ]; then
    echo "Error: webs.txt not found"
    exit 1
fi

# Set up display environment variables.
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
    if [ ! -z "$NPM_PID" ]; then
        echo "Stopping npm dev server (PID: $NPM_PID)..."
        # Kill processes using the port
        netstat -tunlp 2>/dev/null | grep :$NEXTJS_PORT | awk '{print $7}' | cut -d'/' -f1 | xargs kill -9 > /dev/null 2>&1
        kill $NPM_PID > /dev/null 2>&1
        NPM_PID="" # Clear PID after killing
    fi
    if [ ! -z "$XVFB_PID" ]; then
        echo "Stopping Xvfb..."
        kill $XVFB_PID
    fi
    exit
}

# Set a trap to call cleanup on exit.
trap cleanup SIGINT SIGTERM

# Process web directories within the specified line range from webs.txt.
echo "Processing web directories from line $START_LINE to $END_LINE of webs.txt"
for ((i=START_LINE; i<=END_LINE; i++)); do
    web_dir=$(sed "${i}q;d" webs.txt)
    
    if [ -z "$web_dir" ]; then
        echo "Warning: Empty line at $i in webs.txt, skipping..."
        continue
    fi
    
    echo "==========================="
    echo "Processing web directory $i: $web_dir"
    echo "==========================="
    
    index_tsx_path="$web_dir/index.tsx"
    tasks_file_path="$web_dir/tasks.txt"
    
    if [ ! -f "$index_tsx_path" ]; then
        echo "Error: index.tsx not found at $index_tsx_path"
        continue
    fi
    
    if [ ! -f "$tasks_file_path" ]; then
        echo "Error: tasks.txt not found at $tasks_file_path"
        continue
    fi
    
    # Copy the new index.tsx into the Next.js workspace.
    echo "Copying $index_tsx_path to $NEXTJS_WORKSPACE/pages/index.tsx"
    cp -f "$index_tsx_path" "$NEXTJS_WORKSPACE/pages/index.tsx"
    
    # Start the Next.js dev server in the background.
    echo "Starting Next.js dev server..."
    cd "$NEXTJS_WORKSPACE"
    npm run dev -- -p $NEXTJS_PORT &
    NPM_PID=$!
    cd "$CURRENT_DIR"
    
    # Wait for the server to be ready.
    echo "Waiting for dev server to be ready on port $NEXTJS_PORT..."
    timeout 30s bash -c "until netstat -tunlp 2>/dev/null | grep :$NEXTJS_PORT > /dev/null; do sleep 1; done"
    if [ $? -ne 0 ]; then
        echo "Error: Next.js dev server failed to start on port $NEXTJS_PORT."
        kill $NPM_PID > /dev/null 2>&1
        NPM_PID="" # Clear PID
        continue
    fi
    echo "Dev server is ready."

    # Process all tasks for this web page
    echo "Processing tasks from $tasks_file_path"
    while IFS= read -r task_dir; do
        if [ -z "$task_dir" ]; then
            echo "Warning: Empty line in $tasks_file_path, skipping..."
            continue
        fi

        echo "--- Processing task: $task_dir ---"
        # Run the Python agent script.
        python3 run_gui_agent.py --base_dir "$task_dir" --port "$NEXTJS_PORT"
        
        # Check the exit status of the agent.
        if [ $? -ne 0 ]; then
            echo "Task failed: $task_dir"
        else
            echo "Task completed successfully: $task_dir"
        fi
    done < "$tasks_file_path"

    # Stop the dev server.
    echo "Stopping npm dev server (PID: $NPM_PID)..."
    # Kill processes using the port
    netstat -tunlp 2>/dev/null | grep :$NEXTJS_PORT | awk '{print $7}' | cut -d'/' -f1 | xargs kill -9 > /dev/null 2>&1
    kill $NPM_PID > /dev/null 2>&1
    NPM_PID="" # Clear PID after killing
    
    # Pause between web directories.
    if [ $i -lt $END_LINE ]; then
        sleep 3
    fi
done

# Final cleanup.
cleanup 