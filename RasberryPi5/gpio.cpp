#include <wiringPi.h>
#include <iostream>
#include <unistd.h>  // for sleep function

#define OUTPUT_PIN 3
#define INPUT_PIN 25

int main() {
    // Initialize wiringPi and set pin numbering
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to start wiringPi\n";
        return 1;
    }

    // Set pin modes
    pinMode(OUTPUT_PIN, OUTPUT);
    pinMode(INPUT_PIN, INPUT);

    while (true) {
        // Read the state of the input pin
        int inputState = digitalRead(INPUT_PIN);

        // Print the state
        std::cout << "GPIO" << INPUT_PIN << " = " << inputState << "\n";

        // Set the output pin to match the input pin state
        digitalWrite(OUTPUT_PIN, inputState);

        // Wait for 0.3 seconds
        usleep(300000);
    }

    return 0;
}
