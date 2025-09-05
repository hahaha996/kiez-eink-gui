#include <stdlib.h>     // exit()
#include <signal.h>     // signal()
#include <stdio.h>      // printf()
#include <string.h>     // strcmp()
#include "EPD_Test.h"   // Examples

void Handler(int signo)
{
    // System Exit
    printf("\r\nHandler:exit\r\n");
    DEV_Module_Exit();
    exit(0);
}

int main(int argc, char *argv[])
{
    // Exception handling: ctrl + c
    signal(SIGINT, Handler);

    if (argc < 4) {
        printf("Usage: %s <mode> <black_bmp_path> <ry_bmp_path>\r\n", argv[0]);
        return 1;
    }

    const char* mode = argv[1];
    const char* black_path = argv[2];
    const char* ry_path = argv[3];

    if (strcmp(mode, "kiezbox_epd13in3b") == 0) {
        return kiezbox_EPD_13in3b(black_path, ry_path);
    // }
    //  else if (strcmp(mode, "kiezbox_epd13in3b_shared") == 0) {
    //     return kiezbox_EPD_13in3b_shared(black_path, ry_path);
    } else {
        printf("Unknown mode: %s\r\n", mode);
        return 1;
    }
}

/*
#include <stdlib.h>     //exit()
#include <signal.h>     //signal()
#include "EPD_Test.h"   //Examples

void  Handler(int signo)
{
    //System Exit
    printf("\r\nHandler:exit\r\n");
    DEV_Module_Exit();

    exit(0);
}

int main(void)
{
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);
    
#ifdef  epd13in3b
    EPD_13in3b_test();

#else
    printf("Please specify the EPD model when making. \r\n");
    printf("Example: When you run the EPD_7in5_V2_test() program, input: sudo make clean && make EPD=epd7in5V2 \r\n");
    printf("Don't know which program you need to run? Refer to the user manual (Wiki) and main.c \r\n");
#endif
    
    return 0;
}

*/