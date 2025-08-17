

Compile if any change in the C++ program. In `c-eink-project`
```bash
sudo make -j4 EPD=kiezbox_epd13in3b
# now test the C++ program. It takes 3 params: model, paths to black-white and red-white images.
sudo ~/kiezbox-ha/c-eink-project/epd kiezbox_epd13in3b ~/kiezbox-ha/ready_to_use/static1_black_white.bmp ~/kiezbox-ha/ready_to_use/static1_red_white.bmp
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


```
 