#include <iostream>
#include <unistd.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <boost/python.hpp>
#include <string>
#include <fstream>
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

// Function to split a string by a delimiter and return a vector of tokens
std::vector<std::string> split(const std::string& s, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}

// Function to get a specific value from a CSV file
std::string get_value_from_csv(const std::string& filename, int row, int col) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return "";
    }

    std::string line;
    int current_row = 0;

    // Read file line by line
    while (std::getline(file, line)) {
        if (current_row == row) {
            // Split the line by comma
            std::vector<std::string> values = split(line, ',');
            file.close();

            if (col >= 0 && col < values.size()) {
                return values[col];
            } else {
                std::cerr << "Column index out of bounds." << std::endl;
                return "";
            }
        }
        current_row++;
    }
    file.close();

    std::cerr << "Row index out of bounds." << std::endl;
    return "";
}

int main() {
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to initialize wiringPi." << std::endl;
        return 1;
    }

    // Initialize LCD
    lcd_init();

    while (true) {
        std::string filename = "elapsed_time.csv";
        int row = 1;  // For example, get the value from the second row (index 1)
        int col = 0;  // For example, get the value from the first column (index 0)

        std::string value = get_value_from_csv(filename, row, col);

        if (!value.empty()) {
            std::cout << "Value: " << value << std::endl;
            lcd_display("Time: " + value);
        } else {
            std::cerr << "Failed to get value from CSV." << std::endl;
        }

        sleep(1);  // Add delay to avoid continuous looping without delay
    }

    return 0;
}
