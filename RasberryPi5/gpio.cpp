#include <wiringPi.h>
#include <iostream>

int main() {
    // Initialize wiringPi and set pin numbering
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to start wiringPi\n";
        return 1;
    }

    // Set all GPIO pins to outputs and set them to high
    for (int pin = 0; pin < 54; ++pin) { // Assuming Raspberry Pi 4 with 54 GPIO pins
        pinMode(pin, OUTPUT);
        digitalWrite(pin, HIGH);
        std::cout << "GPIO" << pin << " set to high\n";
    }

    return 0;
}
