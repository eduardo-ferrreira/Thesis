#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <iostream>
#include <unistd.h>
#include <string>
#include <vector>
#include <sstream>

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
std::vector<std::string> split_message(const std::string &message);

void lcd_byte(int bits, int mode) {
    int bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT;
    int bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT;

    // High bits
    wiringPiI2CWrite(lcd_fd, bits_high);
    lcd_toggle_enable(bits_high);

    // Low bits
    wiringPiI2CWrite(lcd_fd, bits_low);
    lcd_toggle_enable(bits_low);
}

void lcd_toggle_enable(int bits) {
    usleep(500);
    wiringPiI2CWrite(lcd_fd, (bits | ENABLE));
    usleep(500);
    wiringPiI2CWrite(lcd_fd, (bits & ~ENABLE));
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

std::vector<std::string> split_message(const std::string &message) {
    std::istringstream words_stream(message);
    std::string word;
    std::vector<std::string> lines(2, "");

    while (words_stream >> word) {
        if (lines[0].length() + word.length() + 1 <= LCD_WIDTH) {
            if (!lines[0].empty()) {
                lines[0] += " ";
            }
            lines[0] += word;
        } else if (lines[1].length() + word.length() + 1 <= LCD_WIDTH) {
            if (!lines[1].empty()) {
                lines[1] += " ";
            }
            lines[1] += word;
        } else {
            lines[0] = "Error: Too many";
            lines[1] = "characters!";
            break;
        }
    }

    return lines;
}

void lcd_display(const std::string &message) {
    lcd_clear();

    std::vector<std::string> lines = split_message(message);

    // Center align the text
    int pad1 = (LCD_WIDTH - lines[0].length()) / 2;
    int pad2 = (LCD_WIDTH - lines[1].length()) / 2;

    lines[0] = std::string(pad1, ' ') + lines[0];
    lines[1] = std::string(pad2, ' ') + lines[1];

    lcd_byte(LCD_LINE_1, LCD_CMD);
    for (char c : lines[0]) {
        lcd_byte(c, LCD_CHR);
    }

    lcd_byte(LCD_LINE_2, LCD_CMD);
    for (char c : lines[1]) {
        lcd_byte(c, LCD_CHR);
    }
}

void lcd_clear() {
    lcd_byte(0x01, LCD_CMD);
    usleep(500);
}

int main() {
    if (wiringPiSetup() == -1) {
        std::cerr << "Unable to initialize wiringPi." << std::endl;
        return 1;
    }

    lcd_init();
    lcd_display("Hello, this is FISSIONIST!");

    return 0;
}
