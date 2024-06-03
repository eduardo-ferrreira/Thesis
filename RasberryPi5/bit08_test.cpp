#include <wiringPi.h>
#include <iostream>
#include <unistd.h>

#define INPUT_PIN 07 // Define the GPIO pin for input

int main() {
    // Initialize wiringPi library using BCM GPIO numbering
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to initialize wiringPi." << std::endl;
        return 1;
    }

    // Set GPIO pin as input
    pinMode(INPUT_PIN, INPUT);
    // Optionally, enable internal pull-up resistor
    pullUpDnControl(INPUT_PIN, PUD_UP);

    std::cout << "Reading from GPIO 07." << std::endl;

    while (true) {
        // Read the value from the GPIO pin
        int value = digitalRead(INPUT_PIN);
        std::cout << "GPIO 07 value: " << value << std::endl;
        usleep(500000); // Sleep for 0.5 second
    }

    return 0;
}
