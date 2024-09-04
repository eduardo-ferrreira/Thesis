#include <iostream>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <vector>
#include <string>
#include <algorithm>
#include <utility> // for std::pair
#include <fstream>
#include <cctype>   // For isdigit and isspace

#define I2C_ADDR 0x27 // I2C address of your LCD
#define LCD_CHR 1 // Mode - sending data
#define LCD_CMD 0 // Mode - sending command
#define LCD_BACKLIGHT 0x08 // On
#define ENABLE 0b00000100 // Enable bit
#define LCD_WIDTH 16 // Maximum characters per line
#define LCD_LINE_1 0x80 // Address of the first line
#define LCD_LINE_2 0xC0 // Address of the second line

int lcd_fd; // LCD file descriptor

bool lcd_initialized = false; // Global variable to track LCD initialization status

// Function declarations
void lcd_byte(int bits, int mode);
void lcd_toggle_enable(int bits);
void lcd_init();
void lcd_display(const std::string &message, int line);
void lcd_clear();

// Function to send byte to data pins
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

// Function to toggle enable pin on LCD
void lcd_toggle_enable(int bits) {
    delayMicroseconds(500);
    wiringPiI2CWrite(lcd_fd, (bits | ENABLE));
    delayMicroseconds(500);
    wiringPiI2CWrite(lcd_fd, (bits & ~ENABLE));
    delayMicroseconds(500);
}

// Function to initialize the LCD
void lcd_init() {
    if (lcd_initialized) {
        // LCD is already initialized, so we skip this step
        return;
    }
    lcd_fd = wiringPiI2CSetup(I2C_ADDR);
    if (lcd_fd == -1) {
        std::cerr << "Failed to initialize I2C device." << std::endl;
        exit(1);
    }

    lcd_byte(0x33, LCD_CMD); // Initialize
    lcd_byte(0x32, LCD_CMD); // Initialize
    lcd_byte(0x06, LCD_CMD); // Cursor move direction
    lcd_byte(0x0C, LCD_CMD); // Display On, Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD); // Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD); // Clear display
    delayMicroseconds(500);
}

// Function to display message on LCD
void lcd_display(const std::string &message, int line) {
    lcd_byte(line, LCD_CMD);
    for (char c : message) {
        lcd_byte(c, LCD_CHR);
    }
    for (int i = message.length(); i < LCD_WIDTH; ++i) {
        lcd_byte(' ', LCD_CHR); // Fill the rest of the line with spaces
    }
}

// Function to clear the LCD
void lcd_clear() {
    lcd_byte(0x01, LCD_CMD);
    delayMicroseconds(500);
}

// Structure to hold pin importance and message
struct PinInfo {
    int pin;
    int state;
    int importance;
    std::string message;

    bool operator<(const PinInfo &other) const {
        return importance > other.importance; // Sort by importance descending
    }
};

// Structure to hold combination importance and message
struct CombinationInfo {
    std::vector<std::pair<int, int>> pin_states; // Vector of (pin, state)
    int importance;
    std::string message;
};

// Function to get importance and message for a given pin and state
std::pair<int, std::string> get_importance(int pin, int state) {
    // Define importance and messages for each pin and state
    std::vector<PinInfo> pin_info = {
        {24, LOW, 5, "Bit 00 Low"}, {24, HIGH, 3, "Bit 00 High"},
        {25, LOW, 1, "Bit 01 Low"}, {25, HIGH, 3, "Bit 01 High"},
        {26, LOW, 1, "Bit 02 Low"}, {26, HIGH, 3, "Bit 02 High"},
        {27, LOW, 1, "Bit 03 Low"}, {27, HIGH, 3, "Bit 03 High"},
        {4, LOW, 1, "Bit 04 Low"}, {4, HIGH, 3, "Bit 04 High"},
        {5, LOW, 1, "Bit 05 Low"}, {5, HIGH, 3, "Bit 05 High"},
        {6, LOW, 1, "Bit 06 Low"}, {6, HIGH, 3, "Bit 06 High"},
        {7, LOW, 1, "Bit 07 Low"}, {7, HIGH, 3, "Bit 07 High"},
        {8, LOW, 1, "Bit 08 Low"}, {8, HIGH, 3, "Bit 08 High"},
        {9, LOW, 1, "Bit 09 Low"}, {9, HIGH, 7, "Bit 09 High"},
        {10, LOW, 1, "Bit 10 Low"}, {10, HIGH, 3, "Bit 10 High"},
        {11, LOW, 1, "Bit 11 Low"}, {11, HIGH, 3, "Bit 11 High"},
        {12, LOW, 1, "Bit 12 Low"}, {12, HIGH, 3, "Bit 12 High"},
        {13, LOW, 1, "Bit 13 Low"}, {13, HIGH, 3, "Bit 13 High"},
        {14, LOW, 1, "Bit 14 Low"}, {14, HIGH, 3, "Bit 14 High"},
        {15, LOW, 1, "Bit 15 Low"}, {15, HIGH, 3, "Bit 15 High"},
        {16, LOW, 1, "Bit 16 Low"}, {16, HIGH, 3, "Bit 16 High"},
        {17, LOW, 1, "Bit 17 Low"}, {17, HIGH, 3, "Bit 17 High"},
        {18, LOW, 1, "Bit 18 Low"}, {18, HIGH, 3, "Bit 18 High"},
        {19, LOW, 1, "Bit 19 Low"}, {19, HIGH, 3, "Bit 19 High"},
        {20, LOW, 1, "Bit 20 Low"}, {20, HIGH, 3, "Bit 20 High"},
        {21, LOW, 1, "Bit 21 Low"}, {21, HIGH, 3, "Bit 21 High"},
        {22, LOW, 1, "Bit 22 Low"}, {22, HIGH, 3, "Bit 22 High"},
        {23, LOW, 10, "Bit 23 Low"}, {23, HIGH, 3, "Bit 23 High"}
    };

    for (const auto& info : pin_info) {
        if (info.pin == pin && info.state == state) {
            return std::make_pair(info.importance, info.message);
        }
    }

    // Default return value if pin and state are not found
    return std::make_pair(0, "Unknown");
}

// Function to get importance and message for a given combination of pin states
std::vector<std::pair<int, std::string>> get_combination_importance(const std::vector<std::pair<int, int>> &pin_states) {
    // Define combinations of pin states with their importance and messages
    std::vector<CombinationInfo> combination_info = {
        { {{13, LOW}, {14, LOW}, {15, LOW}}, 12, "BIT 13 14 15 LOW" },
        { {{10, HIGH}, {11, HIGH}}, 15, "BIT 10 & 11 HIGH" }
        // Add more combinations as needed
    };

    std::vector<std::pair<int, std::string>> matching_combinations;

    // Iterate over all combinations
    for (const auto& combo : combination_info) {
        bool match = true;
        for (const auto& pin_state : combo.pin_states) {
            // Check if the pin_state is present in pin_states
            auto it = std::find_if(pin_states.begin(), pin_states.end(),
                [&pin_state](const std::pair<int, int>& ps) {
                    return ps.first == pin_state.first && ps.second == pin_state.second;
                });
            if (it == pin_states.end()) {
                match = false;
                break;
            }
        }
        if (match) {
            /* Print the detected combination and its importance
            std::cout << "Detected combination: ";
            for (const auto& pin_state : combo.pin_states) {
                std::cout << "{Pin: " << pin_state.first << ", State: " << (pin_state.second == HIGH ? "HIGH" : "LOW") << "} ";
            }
            std::cout << "| Importance: " << combo.importance << " | Message: " << combo.message << std::endl;*/

            matching_combinations.push_back(std::make_pair(combo.importance, combo.message));
        }
    }

    // If no combinations matched, return the default value
    if (matching_combinations.empty()) {
        return {std::make_pair(0, "Unknown")};
    }

    // Sort the matching combinations by importance in descending order
    std::sort(matching_combinations.begin(), matching_combinations.end(),
        [](const std::pair<int, std::string>& a, const std::pair<int, std::string>& b) {
            return a.first > b.first;
        });

    return matching_combinations;
}

// Function to filter out non-numeric characters except for the decimal point and minus sign
std::string filterNonNumeric(const std::string& input) {
    std::string result;
    result.reserve(input.size()); // Reserve space to avoid multiple allocations

    bool decimalPointEncountered = false;
    bool negativeSignEncountered = false;

    for (char ch : input) {
        if (std::isdigit(ch) || ch == '.' || ch == '-' || std::isspace(ch)) {
            // Handle negative sign and decimal point
            if (ch == '-' && !negativeSignEncountered) {
                // Allow the minus sign only if it is at the beginning or after a space
                if (result.empty() || std::isspace(result.back())) {
                    result.push_back(ch);
                    negativeSignEncountered = true;
                }
            } else if (ch == '.' && !decimalPointEncountered) {
                // Allow the decimal point only if it is not already in the result
                result.push_back(ch);
                decimalPointEncountered = true;
            } else if (std::isdigit(ch)) {
                result.push_back(ch);
            }
        }
    }

    // Remove leading and trailing spaces
    result.erase(result.find_last_not_of(" \t\n\r\f\v") + 1);
    result.erase(0, result.find_first_not_of(" \t\n\r\f\v"));

    return result;
}

// Function to check if there are active SSH connections
bool isSSHConnected() {
    FILE* pipe = popen("who | grep 'pts/'", "r");
    if (!pipe) return false;

    char buffer[128];
    bool sshConnected = false;

    while (fgets(buffer, 128, pipe) != NULL) {
        sshConnected = true;
        break;
    }

    pclose(pipe);
    return sshConnected;
}

int main(int argc, char* argv[]) {
    bool skip_lcd_init = false;

    if (argc > 1) {
        std::string arg = argv[1];
        if (arg == "--skip-lcd-init") {
            skip_lcd_init = true;
        }
    }

    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Unable to initialize wiringPi." << std::endl;
        return 1;
    }

    // Initialize LCD if not skipped
    if (!skip_lcd_init) {
        lcd_init();
    } else {
        lcd_initialized = true; // Assume the LCD is already initialized
    }

    // Set GPIO pins as INPUT
    std::vector<int> pins = {24, 25, 26, 27, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23};
    for (int pin : pins) {
        pinMode(pin, INPUT);
        pullUpDnControl(pin, PUD_DOWN);
    }

    while (true) {
        std::vector<std::pair<int, int>> pin_states;

        // Read pin states
        for (const int pin : pins) {
            int current_state = digitalRead(pin);
            pin_states.push_back(std::make_pair(pin, current_state));
        }

        // Collect importance and messages from combinations
        std::vector<std::pair<int, std::string>> importance_messages = get_combination_importance(pin_states);

        // Collect importance and messages from individual pins
        for (const auto& ps : pin_states) {
            auto [importance, message] = get_importance(ps.first, ps.second);
            importance_messages.push_back(std::make_pair(importance, message));
        }

        std::sort(importance_messages.begin(), importance_messages.end(),
            [](const std::pair<int, std::string>& a, const std::pair<int, std::string>& b) {
                return a.first > b.first;
            });

        std::string first_line_message = (importance_messages.size() > 0) ? importance_messages[0].second : "";
        std::string second_line_message = (importance_messages.size() > 1) ? importance_messages[1].second : "";

        std::ifstream infile("/home/fissionist/RaspberryPi/variable.txt");
        double k;
        std::string k_value;

        if (infile) {
            std::string k_string;
            if (std::getline(infile, k_string)) {
                k_value = filterNonNumeric(k_string);
                try {
                    k = std::stod(k_value);
                } catch (const std::invalid_argument&) {
                    std::cerr << "Invalid number format in variable.txt" << std::endl;
                    k = 0.0; // Or handle as needed
                }
            }
        }

        if (infile) {
            std::string k_value;
            if (std::getline(infile, k_value)) {
                std::string filteredLine = filterNonNumeric(k_value);
                k_value = std::stod(filteredLine);

                if (isSSHConnected()) {
                    if (k > 0.81 && k < 1.001) {
                        lcd_display(k_value, LCD_LINE_1);
                        lcd_display(first_line_message, LCD_LINE_2);
                    }

                    else {
                        lcd_display(first_line_message, LCD_LINE_1);
                        lcd_display(second_line_message, LCD_LINE_2);
                    }
                }

                else {
                    lcd_display(first_line_message, LCD_LINE_1);
                    lcd_display(second_line_message, LCD_LINE_2);
                }
            }
        }


        /*// Debug statement to verify value of k
        std::cout << "Value of k: " << k << std::endl;

        // Always attempt to display on the LCD
        if (k > 0.975 && k < 1.001) {
            lcd_display(k_value, LCD_LINE_1);
            lcd_display(first_line_message, LCD_LINE_2);
        } else {
            lcd_display(first_line_message, LCD_LINE_1);
            lcd_display(second_line_message, LCD_LINE_2);
        }*/

        if (first_line_message == "BIT 10 & 11 HIGH") {
            int bit = 1;
            std::cout << bit << std::endl;
        } else {
            int bit = 0;
            std::cout << bit << std::endl;
        }

        delay(30);
    }

    return 0;
}
