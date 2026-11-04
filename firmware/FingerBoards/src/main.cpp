#include <Arduino.h>
#include <avr/io.h>
#include <util/delay.h>
#include <utils.h>
#include <raw_twi.h>
#include <util/atomic.h>
#include <defs.h>

volatile uint16_t adcValue = 0;
volatile uint8_t status = 0;
volatile uint16_t lastSent;

void setup() {
  Serial.begin(9600, SERIAL_TX_ONLY);

  setupPorts(0xFC);   //enables pullups on pins 2-7, sets pin 1 as pot input, sets up pin0 for updi
  setupADC();  //setup ADC
  setupTWI();
  
  //PORTB.OUTSET = PIN3_bm; //turn on LED
  ADC0.COMMAND = ADC_STCONV_bm;
}

void loop() {
  uint16_t a, s;
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) { a = adcValue; s = lastSent; }
  Serial.print(a); Serial.print(" / sent "); Serial.println(s);
  Serial.print("ADC Value: ");
  Serial.println(adcValue);
  _delay_ms(1000);
}

ISR(ADC0_RESRDY_vect){
  adcValue = ADC0.RES;
  status |= ADC_VAL_NEW_bm;
  ADC0.COMMAND = ADC_STCONV_bm;
}