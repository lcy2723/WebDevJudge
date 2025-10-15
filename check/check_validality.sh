#!/bin/bash
# nohup bash check_validality.sh 99 1 2 0 > check.log 2>&1 &
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <display_num> <start_line> <end_line>"
    echo "Example: $0 99 1 10"
    exit 1
fi

DISPLAY_NUM=$1
START_LINE=$2
END_LINE=$3
NEXTJS_WORKSPACE="workspace"
NEXTJS_PORT=3000
CURRENT_DIR=$(pwd)

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

# Process tasks within the specified line range.
echo "Processing webs from line $START_LINE to $END_LINE"
for ((i=START_LINE; i<=END_LINE; i++)); do
    base_dir=$(sed "${i}q;d" webs.txt)
    
    if [ -z "$base_dir" ]; then
        echo "Warning: Empty line at $i, skipping..."
        continue
    fi
    
    echo "==========================="
    echo "Processing web $i: $base_dir"
    echo "==========================="
    
    app_tsx_path="$base_dir/index.tsx"
    
    if [ ! -f "$app_tsx_path" ]; then
        echo "Error: app.tsx not found at $app_tsx_path"
        continue
    fi
    
    # Copy the new App.tsx into the Next.js workspace.
    echo "Copying $app_tsx_path to $NEXTJS_WORKSPACE/pages/index.tsx"
    cp -f "$app_tsx_path" "$NEXTJS_WORKSPACE/pages/index.tsx"
    
    # Start the Next.js dev server in the background.
    echo "Starting Next.js dev server..."
    cd "$NEXTJS_WORKSPACE"
    npm run dev -- -p $NEXTJS_PORT &
    NPM_PID=$!
    cd "$CURRENT_DIR"
    
    # Wait for the server to be ready.
    echo "Waiting for dev server to be ready on port $NEXTJS_PORT..."
    # Wait for the port to be in use, with a timeout
    timeout 30s bash -c "until netstat -tunlp 2>/dev/null | grep :$NEXTJS_PORT > /dev/null; do sleep 1; done"
    if [ $? -ne 0 ]; then
        echo "Error: Next.js dev server failed to start on port $NEXTJS_PORT for $base_dir."
        kill $NPM_PID > /dev/null 2>&1
        NPM_PID=""
        continue
    fi
    echo "Dev server is listening. Now verifying with web test..."

    # Run the Python web test script.
    python3 check_validality.py --url "http://localhost:$NEXTJS_PORT" --base_dir "$base_dir"

    # Check the exit status of the test script.
    if [ $? -ne 0 ]; then
        echo "Web test FAILED for $base_dir"
    else
        echo "Web test PASSED for $base_dir"
        echo "Web $i checked successfully: $base_dir"
    fi
    
    # Stop the dev server.
    echo "Stopping npm dev server (PID: $NPM_PID)..."
    # Kill processes using the port
    netstat -tunlp 2>/dev/null | grep :$NEXTJS_PORT | awk '{print $7}' | cut -d'/' -f1 | xargs kill -9 > /dev/null 2>&1
    kill $NPM_PID > /dev/null 2>&1
    NPM_PID="" # Clear PID after killing
    
    # Pause between tasks.
    if [ $i -lt $END_LINE ]; then
        sleep 1
    fi
done

# Final cleanup.
cleanup 