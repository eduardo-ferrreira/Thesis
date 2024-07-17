#include <iostream>
#include <unistd.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <random>
#define I2C_ADDR 0x27 // Your LCD's I2C address
#define LCD_CHR 1     // Mode - sending data
#define LCD_CMD 0     // Mode - sending command
#define LCD_BACKLIGHT 0x08  // On
#define ENABLE 0b00000100   // Enable bit
#define LCD_WIDTH 16        // Assuming a 16x2 LCD
#define LCD_LINE_1 0x80     // LCD RAM address for the 1st line
#define LCD_LINE_2 0xC0     // LCD RAM address for the 2nd line


///////////////////  LCD SETUP  ///////////////////////////////////////////


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

///////////////////////////// RASPBERRY PI SETUP  ////////////////////////////////////

int raspberry_pi() {
	if (wiringPiSetupGpio() == -1) {
		std::cerr << "Unable to initialize wiringPi." << std::endl;
		return 1;
	}

	int gpio_pins[24] = {18, 22, 37, 13, 7, 29, 31, 26, 24, 21, 19, 23, 32, 33, 8, 10, 36, 11, 12, 35, 38, 40, 15, 16};

	for (int i = 0; i < 24; ++i) {
		pinMode(gpio_pins[i], INPUT);
		pullUpDnControl(gpio_pins[i], PUD_DOWN);
	}

   /*pinMode(7, INPUT);
    pullUpDnControl(7, PUD_DOWN);
    pinMode(8, INPUT);
    pinMode(10, INPUT);
    pinMode(11, INPUT);
    pinMode(12, INPUT);
    pinMode(13, INPUT);
    pinMode(15, INPUT);
    pinMode(16, INPUT);
    pinMode(18, INPUT);
    pinMode(19, INPUT);
    pinMode(21, INPUT);
    pinMode(22, INPUT);
    pinMode(23, INPUT);
    pinMode(24, INPUT);
    pinMode(26, INPUT);
    pinMode(29, INPUT);
    pinMode(31, INPUT);
    pinMode(32, INPUT);
    pinMode(33, INPUT);
    pinMode(35, INPUT);
    pinMode(36, INPUT);
    pinMode(37, INPUT);
    pinMode(38, INPUT);
    pinMode(40, INPUT);*/

    return 0;

}


int main() {

    // Initialize LCD
    lcd_init();

    // Set GPIO pins used as INPUT
    raspberry_pi();

	// Define 24 bits GPIO pins array
    //int gpio_pins[24] = {18, 22, 37, 13, 7, 29, 31, 26, 24, 21, 19, 23, 32, 33, 8, 10, 36, 11, 12, 35, 38, 40, 15, 16};
    int gpio_pins[24] = {24,25,26,27,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23};
    int bit_states[24]; // Array to hold the state of each GPIO pin and store in bit_states array


	while (true) {

		bool all_low = true;
				
		for (int i = 0; i < 24; ++i) {
			bit_states[i] = digitalRead(gpio_pins[i]);
		 	
            if (bit_states[i] != LOW){
            	all_low = false;
            	}	
            }  

	    if (bit_states[0] == HIGH){
	    	lcd_display("BIT 00 HIGH");
	    }  

	    if (bit_states[1] == HIGH){
	    	lcd_display("BIT 01 HIGH");
	    }       

	    if (bit_states[2] == HIGH){
	    	lcd_display("BIT 02 HIGH");
	    }

	    if (bit_states[3] == HIGH){
	    	lcd_display("BIT 03 HIGH");
	    }

	    if (bit_states[4] == HIGH){
	    	lcd_display("BIT 04 HIGH");
	    }

	    if (bit_states[5] == HIGH){
	    	lcd_display("BIT 05 HIGH");
	    }

	    if (bit_states[6] == HIGH){
	    	lcd_display("BIT 06 HIGH");
	    }

	    if (bit_states[7] == HIGH){
	    	lcd_display("BIT 07 HIGH");
	    }
		
	    if (bit_states[8] == HIGH){
	    	lcd_display("BIT 08 HIGH");
	    }

	    if (bit_states[9] == HIGH){
	    	lcd_display("BIT 09 HIGH");
	    }

	    if (bit_states[10] == HIGH){
	    	lcd_display("BIT 10 HIGH");
	    }

	    if (bit_states[11] == HIGH){
	    	lcd_display("BIT 11 HIGH");
	    }

	    if (bit_states[12] == HIGH){
	    	lcd_display("BIT 12 HIGH");
	    }

	    if (bit_states[13] == HIGH){
	    	lcd_display("BIT 13 HIGH");
	    }

	    if (bit_states[14] == HIGH){
	    	lcd_display("BIT 14 HIGH");
	    }

	    if (bit_states[15] == HIGH){
	    	lcd_display("BIT 15 HIGH");
	    }

	    if (bit_states[16] == HIGH){
	    	lcd_display("BIT 16 HIGH");
	    }

	    if (bit_states[17] == HIGH){
	    	lcd_display("BIT 17 HIGH");
	    }

	    if (bit_states[18] == HIGH){
	    	lcd_display("BIT 18 HIGH");
	    }

	    if (bit_states[19] == HIGH){
	    	lcd_display("BIT 19 HIGH");
	    }    

	    if (bit_states[20] == HIGH){
	    	lcd_display("BIT 20 HIGH");
	    }

	    if (bit_states[21] == HIGH){
	    	lcd_display("BIT 21 HIGH");
	    }

	    if (bit_states[22] == HIGH){
	    	lcd_display("BIT 22 HIGH");
	    }

	    if (bit_states[23] == HIGH){
	    	lcd_display("BIT 23 HIGH");
	    }

	    if (all_low){
	    	lcd_display("ALL BITS LOW");
	    }

	    sleep(1);
	}



    return 0;
}
