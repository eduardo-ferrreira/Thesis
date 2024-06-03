#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <iostream>
#include <unistd.h>

#define I2C_ADDR 0x27 // Replace with your LCD's I2C address
#define LCD_CHR 1     // Mode - sending data
#define LCD_CMD 0     // Mode - sending command

// LCD Commands
#define LCD_CLEAR 0x01
#define LCD_HOME 0x02

// Timing constants
#define ENABLE 0b00000100 // Enable bit

// LCD device handle
int lcd_fd;

// Function declarations
void lcd_byte(int bits, int mode);
void lcd_init();
void lcd_display(const std::string& message);

// Initialize the display
void lcd_init() {
    lcd_fd = wiringPiI2CSetup(I2C_ADDR);
    if (lcd_fd == -1) {
        std::cerr << "Failed to initialize I2C device." << std::endl;
        exit(1);
    }

    // Initialize display
    lcd_byte(0x33, LCD_CMD);
    lcd_byte(0x32, LCD_CMD);
    lcd_byte(0x06, LCD_CMD);
    lcd_byte(0x0C, LCD_CMD);
    lcd_byte(0x28, LCD_CMD);
    lcd_byte(LCD_CLEAR, LCD_CMD);
    usleep(500);
}

// Send a byte to the LCD
void lcd_byte(int bits, int mode) {
    int bits_high = mode | (bits & 0xF0) | ENABLE;
    int bits_low = mode | ((bits << 4) & 0xF0) | ENABLE;

    // High bits
    wiringPiI2CReadReg8(lcd_fd, bits_high);
    wiringPiI2CReadReg8(lcd_fd, bits_high & ~ENABLE);
    usleep(50);

    // Low bits
    wiringPiI2CReadReg8(lcd_fd, bits_low);
    wiringPiI2CReadReg8(lcd_fd, bits_low & ~ENABLE);
    usleep(50);
}

// Display a string on the LCD
void lcd_display(const std::string& message) {
    for (char c : message) {
        lcd_byte(c, LCD_CHR);
    }
}

int main() {
    // Initialize wiringPi and the LCD
    if (wiringPiSetup() == -1) {
        std::cerr << "Unable to initialize wiringPi." << std::endl;
        return 1;
    }

    lcd_init();
    lcd_display("Hello, World!");

    return 0;
}
