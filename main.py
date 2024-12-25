import os
import cv2
import curses
import time
from functools import lru_cache

video_path = input("Enter the video path:")


video = cv2.VideoCapture(video_path)

width = 120

fps = video.get(cv2.CAP_PROP_FPS)

characters = [' ', '.', ',', '-', '~', ':', ';', '=', '!', '*', '#', '$', '@']

char_range = int(255 / len(characters))


@lru_cache
def get_char(val):
    return characters[min(int(val/char_range), len(characters)-1)]

try:
    if type(video) is str and not os.path.isfile(video):
        print("failed to find video at:", video_path)

    ok, frame = video.read()
    if not ok:
        print("could not extract frame from video")

    ratio = width/frame.shape[1]
    height = int(frame.shape[0]*ratio) // 2
    print(frame.shape)
    print(width, height, ratio)

    curses.initscr()
    window = curses.newwin(height, width, 0, 0)

    frame_count = 0
    frames_per_ms = fps/1000
    start = time.perf_counter_ns()//1000000
    while True:
        ok, orig_frame = video.read()
        if not ok:
            break

        frame = cv2.resize(orig_frame, (width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for y in range(0, frame.shape[0]):
            for x in range(0, frame.shape[1]):
                try:
                    window.addch(y, x, get_char(frame[y, x]))
                except (curses.error):
                    pass

        elapsed = (time.perf_counter_ns()//1000000) - start
        supposed_frame_count = frames_per_ms * elapsed
        if frame_count > supposed_frame_count:
            time.sleep((frame_count-supposed_frame_count)*(1/frames_per_ms)/1000)
        window.refresh()
        frame_count += 1

        
finally:
    cv2.destroyAllWindows()
    curses.endwin()
    fps = frame_count / (((time.perf_counter_ns()//1000000) - start) / 1000)
    print("played on average at %d fps" % fps)