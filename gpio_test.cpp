#include <iostream>
#include <unistd.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>

#define I2C_ADDR 0x27 // Your LCD's I2C address
#define LCD_CHR 1     // Mode - sending data
#define LCD_CMD 0     // Mode - sending command
#define LCD_BACKLIGHT 0x08  // On
#define ENABLE 0b00000100   // Enable bit
#define LCD_WIDTH 16        // Assuming a 16x2 LCD
#define LCD_LINE_1 0x80     // LCD RAM address for the 1st line
#define LCD_LINE_2 0xC0     // LCD RAM address for the 2nd line

int lcd_fd; // LCD file descriptor

void lcd_byte(int bits, int mode);
void lcd_toggle_enable(int bits);
void lcd_init();
void lcd_display(const std::string &message);
void lcd_clear();

void lcd_byte(int bits, int mode) {
    int bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT;
    int bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT;

    // High bits
    write(lcd_fd, &bits_high, 1);
    lcd_toggle_enable(bits_high);

    // Low bits
    write(lcd_fd, &bits_low, 1);
    lcd_toggle_enable(bits_low);
}

void lcd_toggle_enable(int bits) {
    usleep(500);
    int temp = bits | ENABLE;
    write(lcd_fd, &temp, 1);
    usleep(500);
    temp = bits & ~ENABLE;
    write(lcd_fd, &temp, 1);
    usleep(500);
}

void lcd_init() {
    lcd_fd = wiringPiI2CSetup(I2C_ADDR);
    if (lcd_fd == -1) {
        std::cerr << "Failed to initialize I2C device." << std::endl;
        exit(1);
    }

    lcd_byte(0x33, LCD_CMD); // Initialize
    lcd_byte(0x32, LCD_CMD); // Initialize
    lcd_byte(0x06, LCD_CMD); // Cursor move direction
    lcd_byte(0x0C, LCD_CMD); // Display on, cursor off, blink off
    lcd_byte(0x28, LCD_CMD); // Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD); // Clear display
    usleep(500);
}

void lcd_display(const std::string &message) {
    lcd_clear();

    // Center align the text
    int pad = (LCD_WIDTH - message.length()) / 2;
    std::string display_message = std::string(pad, ' ') + message;

    lcd_byte(LCD_LINE_1, LCD_CMD);
    for (char c : display_message) {
        lcd_byte(c, LCD_CHR);
    }
}

void lcd_clear() {
    lcd_byte(0x01, LCD_CMD);
    usleep(500);
}

int main() {
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to initialize wiringPi." << std::endl;
        return 1;
    }

    // Initialize LCD
    lcd_init();

    // Set GPIO 17 as INPUT and GPIO 18 as OUTPUT with pull-down resistor
    pinMode(17, INPUT);
    pinMode(18, OUTPUT);
   // pullUpDnControl(17, PUD_DOWN);

    std::cout << "WiringPi and GPIO pins initialized." << std::endl;

    while (true) {
        // Toggle GPIO 18
        digitalWrite(18, HIGH);
	//sleep(1);
        int state = digitalRead(17);
	std::string state_str = (state == HIGH)? "HIGH" : "LOW";
        std::cout << "GPIO 17 state: " << state << std::endl;
        lcd_display("GPIO 17: " + state_str);
	sleep(5);

        digitalWrite(18, LOW);
        //sleep(1);
	state = digitalRead(17);
	state_str = (state == HIGH)? "HIGH" : "LOW";
        std::cout << "GPIO 17 state: " << state << std::endl;
        lcd_display("GPIO 17: " + state_str);
	sleep(5);
    }

    return 0;
}
