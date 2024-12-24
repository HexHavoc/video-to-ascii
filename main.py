import os
import cv2
import curses
import time

video_path = input("Enter the video path:")

video = cv2.VideoCapture(video_path)

width = 120

fps = video.get(cv2.CAP_PROP_FPS)

characters = [' ', '.', ',', '-', '~', ':', ';', '=', '!', '*', '#', '$', '@']

char_range = int(255 / len(characters))


def get_char(val):
    return characters[min(int(val / char_range), len(characters) - 1)]


def init_colors():
    curses.start_color()
    for i in range(0, 256):
        curses.init_pair(i + 1, i, -1)


def get_color_id(r, g, b):
    return 16 + (r // 51 * 36) + (g // 51 * 6) + (b // 51)


try:
    if not os.path.isfile(video_path):
        print("Failed to find video at:", video_path)
        exit()

    done, frame = video.read()
    if not done:
        print("Could not extract frame from video")
        exit()

    ratio = width / frame.shape[1]
    height = int(frame.shape[0] * ratio) // 2
    print(frame.shape)
    print(width, height, ratio)

    curses.initscr()
    curses.start_color()
    window = curses.newwin(height, width, 0, 0)
    curses.use_default_colors()
    init_colors()

    frame_count = 0
    frames_per_ms = fps / 1000
    start = time.perf_counter_ns() // 1000000
    while True:
        done, orig_frame = video.read()
        if not done:
            break

        frame = cv2.resize(orig_frame, (width, height))

        for y in range(frame.shape[0]):
            for x in range(frame.shape[1]):
                pixel = frame[y, x]
                r, g, b = pixel[2], pixel[1], pixel[0]
                intensity = sum(pixel) / 3
                color_id = get_color_id(r, g, b)
                color_pair = min(color_id, 255) + 1
                char = get_char(intensity)
                try:
                    window.addch(y, x, char, curses.color_pair(color_pair))
                except curses.error:
                    pass

        elapsed = (time.perf_counter_ns() // 1000000) - start
        supposed_frame_count = frames_per_ms * elapsed
        if frame_count > supposed_frame_count:
            time.sleep((frame_count - supposed_frame_count) * (1 / frames_per_ms) / 1000)
        window.refresh()
        frame_count += 1

finally:
    cv2.destroyAllWindows()
    curses.endwin()
    fps = frame_count / (((time.perf_counter_ns() // 1000000) - start) / 1000)
    print("Played on average at %d fps" % fps)
