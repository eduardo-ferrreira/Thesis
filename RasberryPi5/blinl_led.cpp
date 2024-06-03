#include <wiringPi.h>
#include <iostream>

#define LED_PIN 17 // Define the GPIO pin for the LED

int main() {
    // Initialize wiringPi library using BCM GPIO numbering
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to initialize wiringPi." << std::endl;
        return 1;
    }

    // Set GPIO pin as output
    pinMode(LED_PIN, OUTPUT);

    std::cout << "Blinking LED on GPIO 17 every 1 second." << std::endl;

    while (true) {
        // Turn the LED on
        digitalWrite(LED_PIN, HIGH);
        std::cout << "LED ON" << std::endl;
        delay(1000); // Wait for 1 second

        // Turn the LED off
        digitalWrite(LED_PIN, LOW);
        std::cout << "LED OFF" << std::endl;
        delay(1000); // Wait for 1 second
    }

    return 0;
}
