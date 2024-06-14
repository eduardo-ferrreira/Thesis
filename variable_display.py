import time
import csv
import subprocess

def time_passed_since(start_time, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Elapsed Time (seconds)'])  # Write header

        while True:
            time_now = time.time()
            time_passed = time_now - start_time
            writer.writerow([time_passed])  # Write elapsed time to CSV
            file.flush()  # Ensure data is written to file
            time.sleep(1)

# Example usage
start_time = time.time()
file_path = 'elapsed_time.csv'

# Run the function
time_passed_since(start_time, file_path)

def run_cpp_program():
    cpp_program = "./variable_display"  # Path to your compiled C++ program

    try:
        process = subprocess.Popen(cpp_program, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        stderr = process.communicate()[1]
        if stderr:
            print("Errors from C++ program:")
            print(stderr)
    except Exception as e:
        print(f"Failed to run the C++ program: {e}")

run_cpp_program()
