#!/bin/bash

# Default repetitions to 1
N=1

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --N=*)
      N="${1#*=}"
      shift
      ;;
    *)
      input_list="$1"
      shift
      ;;
  esac
done

# Function to generate random float
rand_float() {
  awk -v min=0.2 -v max=7.0 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}'
}

# If a list is provided as a single argument, parse it
if [[ $input_list =~ ^\[.*\]$ ]]; then
  # Remove brackets and spaces, then split by comma
  values=$(echo $input_list | sed 's/\[//;s/\]//;s/ //g')
  IFS=',' read -ra arr <<< "$values"
  if [ ${#arr[@]} -ne 4 ]; then
    echo "Error: Please provide exactly 4 values in the list."
    exit 1
  fi
  SepalLengthCm=${arr[0]}
  SepalWidthCm=${arr[1]}
  PetalLengthCm=${arr[2]}
  PetalWidthCm=${arr[3]}
fi

for ((i=1; i<=N; i++)); do
  # Generate new random numbers for each request if no input list was provided
  if [[ ! $input_list =~ ^\[.*\]$ ]]; then
    SepalLengthCm=$(rand_float)
    SepalWidthCm=$(rand_float)
    PetalLengthCm=$(rand_float)
    PetalWidthCm=$(rand_float)
  fi
  echo "Request $i:"
  echo "Input: SepalLengthCm=${SepalLengthCm}, SepalWidthCm=${SepalWidthCm}, PetalLengthCm=${PetalLengthCm}, PetalWidthCm=${PetalWidthCm}"
  
  # Record start time
  start_time=$(date +%s.%N)
  
  response=$(curl -s -X POST \
    http://0.0.0.0:8000/predict \
    -H 'Content-Type: application/json' \
    -d '{
      "SepalLengthCm": '${SepalLengthCm}',
      "SepalWidthCm": '${SepalWidthCm}',
      "PetalLengthCm": '${PetalLengthCm}',
      "PetalWidthCm": '${PetalWidthCm}'
    }')
  
  # Record end time and calculate duration
  end_time=$(date +%s.%N)
  duration=$(echo "$end_time - $start_time" | bc -l)
  
  echo "Response: $response"
  echo "Response time: ${duration}s"
  echo -e "\n---"
done
