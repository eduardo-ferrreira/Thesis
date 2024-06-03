//#include <wiringPi.h>
//#include <wiringPiI2C.h>
//#include <iostream>
//#include <unistd.h>

//#define I2C_ADDRESS 0x27 // Replace with your I2C device address

//int main() {
    // Initialize wiringPi and the I2C interface
 //   if (wiringPiSetup() == -1) {
   //     std::cerr << "Unable to initialize wiringPi." << std::endl;
     //   return 1;
   // }

    //int fd = wiringPiI2CSetup(I2C_ADDRESS);
    //if (fd == -1) {
      //  std::cerr << "Failed to initialize I2C device at address " << I2C_ADDRESS << std::endl;
       // return 1;
    //}

    //std::cout << "Reading from I2C device at address " << I2C_ADDRESS << std::endl;

    //while (true) {
        // Read a byte from a specific register (replace 0x00 with your register address)
      //  int data = wiringPiI2CReadReg8(fd, 0x00); // Replace 0x00 with the register you want to read
       // if (data == -1) {
         //   std::cerr << "Failed to read from I2C device." << std::endl;
       // } else {
         //   std::cout << "Read value: " << data << std::endl;
       // }
       // usleep(1000000); // Sleep for 1 second
    //}

    //return 0;
//}

#include <wiringPi.h>
#include <iostream>
#include <unistd.h>

#define SDA_PIN 27 // GPIO 2 (SDA)
#define SCL_PIN 28 // GPIO 3 (SCL)

int main() {
    // Initialize wiringPi library using BCM GPIO numbering
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to initialize wiringPi." << std::endl;
        return 1;
    }

    // Set SDA and SCL pins as input
    pinMode(SDA_PIN, INPUT);
    pinMode(SCL_PIN, INPUT);

    std::cout << "Reading from GPIO 2 (SDA) and GPIO 3 (SCL)." << std::endl;

    while (true) {
        // Read the value from the SDA pin
        int sda_value = digitalRead(SDA_PIN);
        std::cout << "SDA (GPIO 27) value: " << sda_value << std::endl;

        // Read the value from the SCL pin
        int scl_value = digitalRead(SCL_PIN);
        std::cout << "SCL (GPIO 28) value: " << scl_value << std::endl;

        usleep(500000); // Sleep for 0.5 second
    }

    return 0;
}

