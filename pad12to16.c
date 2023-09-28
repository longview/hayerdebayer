// pad12to16.c
// Mark Setchell
// Pad 12-bit data to 16-bit
//
// Compile with:
// gcc pad12to16.c -o pad12to16
//
// Run with:
// ./pad12to16 < 12-bit.dat > 16-bit.dat

#include <stdio.h>
#include <sys/uio.h>
#include <unistd.h>
#include <sys/types.h>

#define BYTESPERREAD    6
#define PIXPERWRITE     4

int main(){
    unsigned char  buf[BYTESPERREAD];
    unsigned short pixel[PIXPERWRITE];

    // Read 6 bytes at a time and decode to 4 off 16-bit pixels
    // scaling 12 to 16 bit
    while(read(0,buf,BYTESPERREAD)==BYTESPERREAD){
       pixel[0] = buf[0] | ((buf[1] & 0xf) << 8)*16;
       pixel[1] = (buf[2] << 4) | ((buf[1] & 0xf0) >> 4)*16;
       pixel[2] = buf[3] | ((buf[2] & 0xf) << 8)*16;
       pixel[3] = (buf[5] << 4) | ((buf[4] & 0xf0) >> 4)*16;
       write(1,pixel,PIXPERWRITE*2);
    }
    return 0;
}