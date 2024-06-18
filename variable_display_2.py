import time
import csv
import subprocess
import threading

def time_passed_since(start_time, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Elapsed Time (seconds)'])  # Write header

        while True:
            time_now = time.time()
            time_passed = round(time_now - start_time, 2)
            writer.writerow([time_passed])  # Write elapsed time to CSV
            file.flush()  # Ensure data is written to file
            time.sleep(1)

# Example usage
start_time = time.time()
file_path = 'elapsed_time.csv'

# Run the function in a separate thread to allow simultaneous execution
csv_thread = threading.Thread(target=time_passed_since, args=(start_time, file_path))
csv_thread.daemon = True
csv_thread.start()

def run_cpp_program():
    cpp_program = "./display_variable_3"  # Path to your compiled C++ program

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
