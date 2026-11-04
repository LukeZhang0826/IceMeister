#include <Arduino.h>

uint8_t findAddress(){
  uint8_t addr = 0;
  for(uint8_t i = 0; i < 6; i++){
    if(~VPORTA.IN & (0x80>>i)){
      addr |= (1<<(i));
    }
  }
  return addr + 0x08;
}

uint8_t setupPorts(uint8_t pullups){
    PORTA.DIRCLR = 0xFE; // all pins of PORTA as input except PA0 (updi pin)
    PORTA.PIN1CTRL = PORT_ISC_INPUT_DISABLE_gc;
    if (pullups & PIN2_bm) PORTA.PIN2CTRL |= PORT_PULLUPEN_bm;
    if (pullups & PIN3_bm) PORTA.PIN3CTRL |= PORT_PULLUPEN_bm;
    if (pullups & PIN4_bm) PORTA.PIN4CTRL |= PORT_PULLUPEN_bm;
    if (pullups & PIN5_bm) PORTA.PIN5CTRL |= PORT_PULLUPEN_bm;
    if (pullups & PIN6_bm) PORTA.PIN6CTRL |= PORT_PULLUPEN_bm;
    if (pullups & PIN7_bm) PORTA.PIN7CTRL |= PORT_PULLUPEN_bm;
    PORTB.DIRSET = PIN3_bm; // Set PB2 as output, LED
    return 1;
}

uint8_t setupADC(){
    ADC0.CTRLA &= ~ADC_RESSEL_bm; //set 10 bit resolution
    ADC0.CTRLC |= ADC_REFSEL_VDDREF_gc; //set reference voltage to VDD
    ADC0.CTRLC |= ADC_PRESC_DIV4_gc; //set prescaler to 4
    ADC0.CTRLC |= ADC_SAMPCAP_bm;
    ADC0.MUXPOS = ADC_MUXPOS_AIN1_gc; //set input to PA2
    ADC0.INTCTRL |= ADC_RESRDY_bm; //enable interrupt on conversion complete
    ADC0.CTRLA |= ADC_ENABLE_bm; //enable ADC
    return 1;
}