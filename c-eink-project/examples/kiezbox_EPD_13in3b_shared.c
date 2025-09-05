#include "EPD_Test.h"
#include "EPD_13in3b.h"
#include <time.h>


#include <stdio.h>

typedef struct {
    const char *text;   // string
    int         box[4]; // [x1, y1, x2, y2]
    const char *color;  // "red" or "black"
} TextItem;

typedef struct {
    int id;
    double value;
} Item;

void print_something() {
        printf("Printing something!\n");
}

void process_items(Item *items, int count) {
    if (items) {
        for (int i = 0; i < count; i++) {
            printf("Item %d: id=%d, value=%.2f\n", i, items[i].id, items[i].value);
        }
    } else {
        printf("NO ITEMS!");
    }
}

void process_text_items(TextItem *text_items, int count) {
    if (text_items) {
        for (int i = 0; i < count; i++) {
            // You can only check inner pointers, e.g., the strings:
            if (!text_items[i].text) { puts("item.text=NULL"); continue; }

            printf("text: %s\n", text_items[i].text);
            printf("box: [%d, %d, %d, %d]\n",
                   text_items[i].box[0], text_items[i].box[1],
                   text_items[i].box[2], text_items[i].box[3]);
            printf("color: %s\n", text_items[i].color ? text_items[i].color : "(null)");
        }
    } else {
        puts("NO ITEMS!");
    }
}

int kiezbox_EPD_13in3b_with_text(const char* black_bmp_path, const char* ry_bmp_path, TextItem *text_items, int count)
{
    // process_items(text_items, count);
    process_text_items(text_items, count);
    printf("Files: %s %s\n", black_bmp_path, ry_bmp_path);
    // return -111111;

    printf("KiezBox kiezbox_EPD_13in3b_with_text Demo\r\n");
    if (DEV_Module_Init() != 0) {
        return -1;
    }

    if (!black_bmp_path || !ry_bmp_path) {
        printf("Error: image paths must not be null.\r\n");
        DEV_Module_Exit();
        return -1;
    }

    printf("e-Paper Init and Clear...\r\n");
    EPD_13IN3B_Init();
    EPD_13IN3B_Clear();

    // Create frame buffers
    UBYTE *BlackImage, *RYImage; // Red or Yellow
    UDOUBLE Imagesize = ((EPD_13IN3B_WIDTH % 8 == 0) ? (EPD_13IN3B_WIDTH / 8) : (EPD_13IN3B_WIDTH / 8 + 1)) * EPD_13IN3B_HEIGHT;
    if ((BlackImage = (UBYTE *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for black memory...\r\n");
        DEV_Module_Exit();
        return -1;
    }
    if ((RYImage = (UBYTE *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for red memory...\r\n");
        free(BlackImage);
        DEV_Module_Exit();
        return -1;
    }

    printf("NewImage: BlackImage and RYImage\r\n");
    Paint_NewImage(BlackImage, EPD_13IN3B_WIDTH, EPD_13IN3B_HEIGHT, 0, WHITE);
    Paint_NewImage(RYImage,    EPD_13IN3B_WIDTH, EPD_13IN3B_HEIGHT, 0, WHITE);

    printf("show bmp------------------------\r\n");
    Paint_SelectImage(BlackImage);
    GUI_ReadBmp(black_bmp_path, 0, 0);  // <-- use provided black image path

    Paint_SelectImage(RYImage);
    GUI_ReadBmp(ry_bmp_path, 0, 0);     // <-- use provided red/RY image path

    /////////

    Paint_SelectImage(BlackImage);
    Paint_DrawString_EN(10, 0, "THIS IS a  long test test test llgpio -lm -D DEBUG", &Font16, WHITE, BLACK);
    // Print supplied texts
    if (text_items) {
        for (int i = 0; i < count; i++) {
            if (!strcmp(text_items[i].color, "black")) {
                if (!text_items[i].text) { puts("item.text=NULL"); continue; }
    
                printf("text: %s\n", text_items[i].text);
                printf("box: [%d, %d, %d, %d]\n",
                       text_items[i].box[0], text_items[i].box[1],
                       text_items[i].box[2], text_items[i].box[3]);
                printf("color: %s\n", text_items[i].color ? text_items[i].color : "(null)");
                Paint_DrawString_EN(text_items[i].box[0], text_items[i].box[1], text_items[i].text, &Font16, WHITE, BLACK);
            }
        }
    } else {
        puts("NO ITEMS!");
    }


    Paint_SelectImage(RYImage);
    Paint_DrawString_EN(10, 0, "THIS IS a  long test test test llgpio -lm -D DEBUG", &Font16, WHITE, BLACK);
    // Print supplied texts
    if (text_items) {
        for (int i = 0; i < count; i++) {
            if (!strcmp(text_items[i].color, "red")) {
                if (!text_items[i].text) { puts("item.text=NULL"); continue; }
    
                printf("text: %s\n", text_items[i].text);
                printf("box: [%d, %d, %d, %d]\n",
                       text_items[i].box[0], text_items[i].box[1],
                       text_items[i].box[2], text_items[i].box[3]);
                printf("color: %s\n", text_items[i].color ? text_items[i].color : "(null)");
                Paint_DrawString_EN(text_items[i].box[0], text_items[i].box[1], text_items[i].text, &Font16, WHITE, BLACK);
            }
        }
    } else {
        puts("NO ITEMS!");
    }
    /////////

    EPD_13IN3B_Display_Base(BlackImage, RYImage);
    DEV_Delay_ms(3000);

    printf("Goto Sleep...\r\n");
    EPD_13IN3B_Sleep();

    free(BlackImage);
    free(RYImage);
    BlackImage = NULL;
    RYImage = NULL;

    DEV_Delay_ms(2000); // important, at least 2s
    printf("close 5V, Module enters 0 power consumption ...\r\n");
    DEV_Module_Exit();
    return 0;
}


/*****************************************************************************
* | File      	:   EPD_13IN3B_test.c
* | Author      :   Waveshare team
* | Function    :   13.3inch e-paper (B) test demo
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2024-04-08
* | Info        :
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
******************************************************************************/
/*
#include "EPD_Test.h"
#include "EPD_13in3b.h"
#include <time.h> 

int kiezbox_EPD_13in3b_test(const char* black_bmp_path, const char* ry_bmp_path)
{
    printf("EPD_13IN3B_test Demo\r\n");
    if(DEV_Module_Init()!=0){
        return -1;
    }

    printf("e-Paper Init and Clear...\r\n");
	EPD_13IN3B_Init();
    EPD_13IN3B_Clear();


    //Create a new image cache named IMAGE_BW and fill it with white
    UBYTE *BlackImage, *RYImage; // Red or Yellow
    UDOUBLE Imagesize = ((EPD_13IN3B_WIDTH % 8 == 0)? (EPD_13IN3B_WIDTH / 8 ): (EPD_13IN3B_WIDTH / 8 + 1)) * EPD_13IN3B_HEIGHT;
    if((BlackImage = (UBYTE *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for black memory...\r\n");
        return -1;
    }
    if((RYImage = (UBYTE *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for red memory...\r\n");
        return -1;
    }
    printf("NewImage:BlackImage and RYImage\r\n");
    Paint_NewImage(BlackImage, EPD_13IN3B_WIDTH, EPD_13IN3B_HEIGHT, 0, WHITE);
    Paint_NewImage(RYImage, EPD_13IN3B_WIDTH, EPD_13IN3B_HEIGHT, 0, WHITE);

    //Select Image
    //Paint_SelectImage(BlackImage);
    //Paint_Clear(WHITE);
    //Paint_SelectImage(RYImage);
    //Paint_Clear(WHITE);
	
#if 1   // show bmp
    printf("show bmp------------------------\r\n");
    Paint_SelectImage(BlackImage);
    GUI_ReadBmp("./pic/static1.bmp", 0, 0);
    Paint_SelectImage(RYImage);
    GUI_ReadBmp("./pic/13in3b_r.bmp", 0, 0);
    EPD_13IN3B_Display_Base(BlackImage, RYImage);
    DEV_Delay_ms(3000);
#endif

#if 0  // Drawing on the image
    //Horizontal screen
    //1.Draw black image
    EPD_13IN3B_Init();
    printf("Draw black image\r\n");
    Paint_SelectImage(BlackImage);
    Paint_Clear(WHITE);
    Paint_DrawPoint(10, 80, BLACK, DOT_PIXEL_1X1, DOT_STYLE_DFT);
    Paint_DrawPoint(10, 90, BLACK, DOT_PIXEL_2X2, DOT_STYLE_DFT);
    Paint_DrawPoint(10, 100, BLACK, DOT_PIXEL_3X3, DOT_STYLE_DFT);
    Paint_DrawPoint(10, 110, BLACK, DOT_PIXEL_3X3, DOT_STYLE_DFT);
    Paint_DrawLine(20, 70, 70, 120, BLACK, DOT_PIXEL_1X1, LINE_STYLE_SOLID);
    Paint_DrawLine(70, 70, 20, 120, BLACK, DOT_PIXEL_1X1, LINE_STYLE_SOLID);      
    Paint_DrawRectangle(20, 70, 70, 120, BLACK, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawRectangle(80, 70, 130, 120, BLACK, DOT_PIXEL_1X1, DRAW_FILL_FULL);
    Paint_DrawString_EN(10, 0, "waveshare", &Font16, BLACK, WHITE);    
    Paint_DrawString_CN(130, 20, "΢ѩ����", &Font24CN, WHITE, BLACK);
    Paint_DrawNum(10, 50, 987654321, &Font16, WHITE, BLACK);
    
    //2.Draw red image
    printf("Draw red image\r\n");
    Paint_SelectImage(RYImage);
    Paint_Clear(WHITE);
    Paint_DrawCircle(160, 95, 20, BLACK, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawCircle(210, 95, 20, BLACK, DOT_PIXEL_1X1, DRAW_FILL_FULL);
    Paint_DrawLine(85, 95, 125, 95, BLACK, DOT_PIXEL_1X1, LINE_STYLE_DOTTED);
    Paint_DrawLine(105, 75, 105, 115, BLACK, DOT_PIXEL_1X1, LINE_STYLE_DOTTED);  
    Paint_DrawString_CN(130, 0,"���abc", &Font12CN, BLACK, WHITE);
    Paint_DrawString_EN(10, 20, "hello world", &Font12, WHITE, BLACK);
    Paint_DrawNum(10, 33, 123456789, &Font12, BLACK, WHITE);

    printf("EPD_Display\r\n");
    EPD_13IN3B_Display_Base(BlackImage, RYImage);
    DEV_Delay_ms(2000);
#endif

#if 0
	printf("Partial refresh\r\n");
    Paint_NewImage(BlackImage, Font20.Width * 7, Font20.Height, 0, WHITE);
    Debug("Partial refresh\r\n");
    Paint_SelectImage(BlackImage);
    Paint_Clear(WHITE);
	
    PAINT_TIME sPaint_time;
    sPaint_time.Hour = 12;
    sPaint_time.Min = 34;
    sPaint_time.Sec = 56;
    UBYTE num = 10;
    for (;;) {
        sPaint_time.Sec = sPaint_time.Sec + 1;
        if (sPaint_time.Sec == 60) {
            sPaint_time.Min = sPaint_time.Min + 1;
            sPaint_time.Sec = 0;
            if (sPaint_time.Min == 60) {
                sPaint_time.Hour =  sPaint_time.Hour + 1;
                sPaint_time.Min = 0;
                if (sPaint_time.Hour == 24) {
                    sPaint_time.Hour = 0;
                    sPaint_time.Min = 0;
                    sPaint_time.Sec = 0;
                }
            }
        }
        Paint_ClearWindows(0, 0, Font20.Width * 7, Font20.Height, WHITE);
        Paint_DrawTime(0, 0, &sPaint_time, &Font20, WHITE, BLACK);
        num = num - 1;
        if(num == 0) {
            break;
        }
		EPD_13IN3B_Display_Partial(BlackImage, 10, 130, 10 + Font20.Width * 7, 130 + Font20.Height);
		DEV_Delay_ms(500);//Analog clock 1s
    }
#endif

	//printf("Clear...\r\n");
    //EPD_13IN3B_Init();
    //EPD_13IN3B_Clear();
	
    printf("Goto Sleep...\r\n");
    EPD_13IN3B_Sleep();
    free(BlackImage);
    free(RYImage);
    BlackImage = NULL;
    RYImage = NULL;
    DEV_Delay_ms(2000);//important, at least 2s
    // close 5V
    printf("close 5V, Module enters 0 power consumption ...\r\n");
    DEV_Module_Exit();
    return 0;
}

*/