#!/bin/bash

ulimit -c 0

# Check for the correct number of arguments, with defaults.
if [ "$#" -eq 0 ]; then
    NUM_CHUNKS=4
    START_DISPLAY=99
    DATASET_START=1
    DATASET_END=""
elif [ "$#" -eq 2 ]; then
    NUM_CHUNKS=$1
    START_DISPLAY=$2
    DATASET_START=1
    DATASET_END=""
elif [ "$#" -eq 4 ]; then
    NUM_CHUNKS=$1
    START_DISPLAY=$2
    DATASET_START=$3
    DATASET_END=$4
else
    echo "Usage: $0 [num_chunks start_display [dataset_start dataset_end]]"
    echo "Examples:"
    echo "  $0                    # Default: 4 chunks, display :99, full dataset"
    echo "  $0 4 99              # 4 chunks, display :99, full dataset"
    echo "  $0 4 99 1 100        # 4 chunks, display :99, dataset lines 1-100"
    exit 1
fi

# Validate arguments.
if ! [[ "$NUM_CHUNKS" =~ ^[0-9]+$ ]] || [ "$NUM_CHUNKS" -lt 1 ]; then
    echo "Error: num_chunks must be a positive number"
    exit 1
fi
if ! [[ "$START_DISPLAY" =~ ^[0-9]+$ ]]; then
    echo "Error: start_display must be a number"
    exit 1
fi
if ! [[ "$DATASET_START" =~ ^[0-9]+$ ]] || [ "$DATASET_START" -lt 1 ]; then
    echo "Error: dataset_start must be a positive number"
    exit 1
fi
if [ ! -z "$DATASET_END" ]; then
    if ! [[ "$DATASET_END" =~ ^[0-9]+$ ]]; then
        echo "Error: dataset_end must be a number"
        exit 1
    fi
    if [ "$DATASET_START" -gt "$DATASET_END" ]; then
        echo "Error: dataset_start cannot be greater than dataset_end"
        exit 1
    fi
fi

# Check for required files.
if [ ! -f "webs.txt" ]; then
    echo "Error: webs.txt not found"
    exit 1
fi
if [ ! -x "run_serial.sh" ]; then
    echo "Making run_serial.sh executable..."
    chmod +x run_serial.sh
fi

# Create log directory.
LOG_DIR="parallel_logs"
mkdir -p "$LOG_DIR"

# Determine task range.
TOTAL_LINES=$(wc -l < webs.txt)
if [ -z "$DATASET_END" ] || [ "$DATASET_END" -gt "$TOTAL_LINES" ]; then
    DATASET_END=$TOTAL_LINES
fi
TOTAL_TASKS=$((DATASET_END - DATASET_START + 1))
if [ "$TOTAL_TASKS" -lt "$NUM_CHUNKS" ]; then
    echo "Warning: More chunks than tasks, reducing chunks to $TOTAL_TASKS"
    NUM_CHUNKS=$TOTAL_TASKS
fi

# Calculate chunk size.
CHUNK_SIZE=$(( (TOTAL_TASKS + NUM_CHUNKS - 1) / NUM_CHUNKS ))
echo "Dataset range: lines $DATASET_START-$DATASET_END"
echo "Total tasks to process: $TOTAL_TASKS"
echo "Number of chunks: $NUM_CHUNKS"
echo "Tasks per chunk: $CHUNK_SIZE"
echo "Logs will be saved to: $LOG_DIR/"

PIDS=()

# Launch parallel jobs.
for ((chunk=0; chunk<NUM_CHUNKS; chunk++)); do
    CHUNK_START_OFFSET=$((chunk * CHUNK_SIZE))
    CHUNK_END_OFFSET=$((CHUNK_START_OFFSET + CHUNK_SIZE - 1))
    if [ $CHUNK_END_OFFSET -ge $TOTAL_TASKS ]; then
        CHUNK_END_OFFSET=$((TOTAL_TASKS - 1))
    fi
    
    START_LINE=$((DATASET_START + CHUNK_START_OFFSET))
    END_LINE=$((DATASET_START + CHUNK_END_OFFSET))
    
    DISPLAY_NUM=$((START_DISPLAY + chunk))
    LOG_FILE="$LOG_DIR/chunk_${chunk}_display_${DISPLAY_NUM}.log"
    
    echo "Starting chunk $((chunk + 1))/$NUM_CHUNKS (lines $START_LINE-$END_LINE) on display :$DISPLAY_NUM with worker ID $chunk"
    echo "Log file: $LOG_FILE"
    
    # Run the serial script for Next.js in the background.
    ./run_serial.sh $DISPLAY_NUM $START_LINE $END_LINE $chunk > "$LOG_FILE" 2>&1 &
    PIDS+=($!)
done

# Wait for all jobs to complete.
echo "Waiting for all chunks to complete..."
for pid in "${PIDS[@]}"; do
    wait $pid
    status=$?
    if [ $status -ne 0 ]; then
        echo "Warning: A chunk process (PID: $pid) exited with status $status"
    fi
done

echo "All chunks have completed."
echo "Check individual logs in: $LOG_DIR/" 