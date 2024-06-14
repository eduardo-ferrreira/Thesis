import subprocess

def run_cpp_program():
    cpp_program = "./gpio_test"  # Path to your compiled C++ program

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
