#include <wiringPi.h>
#include <iostream>
#include <unistd.h> // for sleep function

int main() {
    // Initialize WiringPi using the Broadcom pin numbers
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to initialize wiringPi." << std::endl;
        return 1;
    }

    // Set GPIO 18 as output
    pinMode(18, OUTPUT);

    // Set GPIO 18 to HIGH
    digitalWrite(18, HIGH);
    std::cout << "GPIO 18 set to HIGH" << std::endl;

    // Wait for 5 seconds
    sleep(5);

    // Set GPIO 18 to LOW
    digitalWrite(18, LOW);
    std::cout << "GPIO 18 set to LOW" << std::endl;

    // Wait for 5 seconds
    sleep(5);

    return 0;
}
