#include <Arduino.h>
#include <utils.h>
#include <defs.h>

extern uint8_t status;
extern uint16_t adcValue;
extern uint16_t lastSent;
static uint8_t buf[8], idx;

uint8_t setupTWI(){
    delayMicroseconds(100);
    TWI0.SCTRLA |= TWI_DIEN_bm | TWI_APIEN_bm | TWI_PIEN_bm;
    TWI0.SADDR = (findAddress())<<1;
    TWI0.SCTRLA |= TWI_ENABLE_bm;
    return 1;
}

ISR(TWI0_TWIS_vect){
  uint8_t s = TWI0_SSTATUS;
  if (s & TWI_APIF_bm){
    if((s & TWI_AP_bm) ){ // add something like && (status & ADC_VAL_NEW_bm) in future
      uint16_t v = adcValue;
      lastSent = v;
      buf[0] = v;
      buf[1] = v >>8;
      idx = 0;
      status &= ~ADC_VAL_NEW_bm;
      TWI0.SCTRLB = TWI_SCMD_RESPONSE_gc;
    } 
    else TWI0.SCTRLB = TWI_SCMD_COMPTRANS_gc;
  }
  else if (s & TWI_DIF_bm){
    if(s & TWI_DIR_bm){ // Master Read
        if(s & TWI_RXACK_bm && idx > 0){ // Master NACKed the last byte, so we are done
            TWI0.SCTRLB = TWI_SCMD_COMPTRANS_gc;
        }
        else{
            TWI0.SDATA = (idx < 2) ? buf[idx++] : 0xFF;
            TWI0.SCTRLB = TWI_SCMD_RESPONSE_gc;
        }
        
    }
    else{
        (void)TWI0.SDATA; // Read the data to clear the interrupt
        TWI0.SCTRLB = TWI_SCMD_RESPONSE_gc;
    } 
  }
}