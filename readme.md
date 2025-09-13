

Compile if any change in the C++ program. In `c-eink-project`
```bash
sudo make -j4 EPD=kiezbox_epd13in3b
# now test the C++ program. It takes 3 params: model, paths to black-white and red-white images.
sudo ~/kiezbox-ha/c-eink-project/epd kiezbox_epd13in3b ~/kiezbox-ha/ready_to_use/static1_black_white.bmp ~/kiezbox-ha/ready_to_use/static1_red_white.bmp


python3 nina_warning_to_epd.py biw.BIWAPP-90480_NGRjZTkwNzI3NzRkZTBmNA --log-level DEBUG --use-local-json
# Stromausfall
python3 nina_warning_to_epd.py mow.DE-BR-B-SE017-20250909-17-001 --log-level DEBUG --use-local-json
```

```bash
Steps:

- Design ready-to-display image. Display whole image using the C program.
-> problem: the C program to display BMP img seems to handle whole img badly. Small detail and text can be displayed with missing parts.




- Font is fixed and provided by waveshare lib. There are supported size:.
The web page is therefore not helpful since the font is not available. That website is largely irrelevant if plotting img directly doesn't work.




###
sudo make -j4 EPD=kiezbox_epd13in3b
cd bin
gcc -shared -o libepd13in3b.so \
  font24CN.o font24.o font20.o font8.o \
  kiezbox_EPD_13in3b_test.o kiezbox_EPD_13in3b_shared.o \
  GUI_Paint.o GUI_BMPfile.o font16.o font12CN.o font12.o \
  DEV_Config.o EPD_13in3b.o dev_hardware_SPI.o \
  -Wl,-soname,libepd13in3b.so.1 -Wl,--no-undefined \
  -llgpio -lm

python3 text_on_template_to_c_program.py
###


```
The server is in charge of taking (any color depth) user image, upload it to folder `origin`, run a script to analyze and split the red and black pixels in black and red image.
These images can be found in `ready_to_use` folder and will be used for preview as well as for feeding the C++ program to show to the eink display.

To run the server, make sure we are at `~/kiezbox-ha` and run:
```
# Activate environment
source .venv/bin/activate
# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# run web
http://192.168.178.86:8000/

# split
http://192.168.178.86:8000/split
#insert
http://192.168.178.86:8000//insert

```
 

 ```json
 [
    {
        "text": "Hello",
        "box": [
            40,
            20,
            250,
            60
        ],
        "size": 28,
        "color": "black",
        "style": "normal"
    },
    {
        "text": "Persönliche Vorsorge",
        "box": [15, 300, 900, 330],
        "size": 28,
        "color": "red",
        "style": "normal"
    },
    {
        "text": "Essen und Trinken",
        "box": [15, 350, 900, 380],
        "size": 22,
        "color": "red",
        "style": "normal"
    },
    {
        "text": "This line is a bit longer.",
        "box": [15, 385, 900, 430],
        "size": 10,
        "color": "black",
        "style": "normal"
    }
]
```