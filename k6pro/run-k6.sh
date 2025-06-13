#!/bin/sh
# Wait for backend to be ready
BACKEND_HOST="backend"
BACKEND_PORT=5000

echo "Waiting for backend to be ready at $BACKEND_HOST:$BACKEND_PORT..."
until nc -z "$BACKEND_HOST" "$BACKEND_PORT"; do
  echo "Backend not ready yet..."
  sleep 1
done

echo "Backend is ready. Starting performance tests."

TEST_DIR="."  # Not ./k6
RESULT_DIR="./results"
mkdir -p "$RESULT_DIR"

echo "Starting K6 performance tests..."

for script in "$TEST_DIR"/TC-PERF-*.js; do
    test_name=$(basename "$script" .js)
    timestamp=$(date +"%Y%m%d-%H%M%S")
    output_file="$RESULT_DIR/${test_name}_${timestamp}.json"
    log_file="$RESULT_DIR/${test_name}_${timestamp}.log"

    echo "Running $test_name..."

    # Record start time (in Unix seconds) for Prometheus query
    start_time=$(date +%s)
    echo "START_TIME=$start_time" > "$log_file"

    # Run the test
    k6 run --summary-export="$output_file" "$script"

    # Record end time
    end_time=$(date +%s)
    echo "END_TIME=$end_time" >> "$log_file"

    echo "$test_name finished. Results saved to:"
    echo "  - JSON: $output_file"
    echo "  - Log: $log_file"
    echo
done

echo "All test cases executed."
