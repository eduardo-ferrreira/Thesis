#include <wiringPi.h>
#include <iostream>

int main() {
    // initialize wiringPiand set pin numbering
    if (wiringPiSetupGpio() == -1) {
        std::cerr<<"Unable to start wiringPin \n";
        exit (1);
    }

// iterate through all 26 GPIO pins and set their value to high
for (int pin = 2; pin <= 26; ++pin) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);
    if (pin == 9) {
        digitalWrite(pin, LOW);
    }
    std::cout<<"GPIO" << pin << "set to  high \n";
}

return 0;
}
