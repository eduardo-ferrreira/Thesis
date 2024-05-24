#include <wiringPi.h>
#include <iostream>

// Define the maximum GPIO pin number
const int MAX_GPIO_PIN = 53;  // Assuming Raspberry Pi 4 with 54 GPIO pins

// Define the list of ground pins
const int GROUND_PINS[] = { 9, 14, 20, 25, 30, 34, 39 }; // Excluding pin 0

int main() {
    // Initialize wiringPi and set pin numbering
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to start wiringPi\n";
        return 1;
    }

    // Set all GPIO pins (excluding ground pins) to outputs and set them to high
    for (int pin = 0; pin <= MAX_GPIO_PIN; ++pin) {
        bool isGroundPin = false;
        for (int groundPin : GROUND_PINS) {
            if (pin == groundPin) {
                isGroundPin = true;
                break;
            }
        }
        if (!isGroundPin) {
            pinMode(pin, OUTPUT);
            digitalWrite(pin, HIGH);
            std::cout << "GPIO" << pin << " set to high\n";
        }
    }

    return 0;
}

