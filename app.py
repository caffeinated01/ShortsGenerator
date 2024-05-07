import glob
import os
from platform import system
from random import choice
import shutil
from threading import Semaphore
from datetime import datetime
import time
from reddit import RedditShort
from trivia import TriviaShort

BACKGROUND_FILE_NAME = './assets/backgrounds/{}.mp4'.format(choice(['bg_minecraft']))
MUSIC_FILE_NAME = './assets/songs/{}.mp3'.format(choice(['bg_phonk']))
FONT_FILE_NAME = './assets/font.ttf'
QN_COUNT = 5

# Helper functions
def generate_job_id():
  timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
  return f'job_{timestamp}'

def clear_screen():
  os_name = system()
  if os_name == 'Windows':
    os.system('cls')
  elif os_name in ('Linux', 'Darwin'):
    os.system('clear')

# Generate Trivia
def generate_trivia():
    print('Specify what to automate...')
    
    n_videos = int(input('How many videos: '))
    n_questions_per_video = int(input('How many questions per video: '))
    n_threads = input("How many thread to dedicate (recommended ~5), 'n' to disable multithreading: ")

    job_id = generate_job_id()

    # Generate directory for video output
    os.makedirs(f'./out/{job_id}')

    if n_threads.lower() == 'n':
        for i in range(n_videos):
            clear_screen()
            short = TriviaShort(BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME, n_questions_per_video, 'trivia_' + str(i+1), job_id, i+1)
            short.start_thread()

            if short.running:
                short.thread.join()

    else:
        semaphore = Semaphore(int(n_threads))

        for i in range(n_videos):
            clear_screen()
            # Multithreading
            with semaphore:
                short = TriviaShort(BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME, n_questions_per_video, 'trivia_' + str(i+1), job_id, i+1)
                short.start_thread()
                # Delay so can fetch questions
                time.sleep(10)

# Generate Reddit
def generate_reddit():
    print('Specify what to automate...')
    
    n_videos = int(input('How many videos: '))
    n_comments_per_video = int(input('How many comments per video: '))
    subreddit = input('What subreddit to find post from: r/')
    n_threads = input("How many thread to dedicate (recommended ~5), 'n' to disable multithreading: ")

    job_id = generate_job_id()

    # Generate directory for video output
    os.makedirs(f'./out/{job_id}')

    if n_threads.lower() == 'n':
        for i in range(n_videos):
            clear_screen()
            short = RedditShort(BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME, subreddit, n_comments_per_video, 'reddit_' + str(i+1), job_id, i+1)
            short.start_thread()

            if short.running:
                short.thread.join()

    else:
        semaphore = Semaphore(int(n_threads))

        for i in range(n_videos):
            clear_screen()
            # Multithreading
            with semaphore:
                short = RedditShort(BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME, subreddit, n_comments_per_video, 'reddit_' + str(i+1), job_id, i+1)
                short.start_thread()
                
                time.sleep(10)

def main():
    clear_screen()
    print('''
 ___       __ _      _ _                  ___ _ _ _      _    
|_ _|_ _  / _(_)_ _ (_) |_ ___   ||_||_  / __| (_) |_ __| |_  
 | || ' \|  _| | ' \| |  _/ -_) (_-<_-< | (_ | | |  _/ _| ' \ 
|___|_||_|_| |_|_||_|_|\__\___| / _/ _/  \___|_|_|\__\__|_||_|
                                 || ||                        
A Shorts Automation CLI
          ''')
    choices = {
        '1': 'Trivia Short',
        '2': 'Reddit Short'
    }

    choice_to_fn = {
        '1': generate_trivia,
        '2': generate_reddit,
    }

    if not os.path.exists('./out'):
       os.mkdir('./out')
    
    if not os.path.exists('./temp'):
       os.mkdir('./temp')

    if not os.path.isfile('.env'):
        env = open('.env', 'w')
        env.write('''REDDIT_CLIENT_ID = 
REDDIT_CLIENT_SECRET = 
''')

    c = None
    while c == None:
        c_text = '\n'.join([f'[{i}] '+choices[i] for i in choices.keys()])
        print(f'Options\n{c_text}')
        choice = input('What to generate: ')
        if choice not in choices.keys():
            print(f'{choice} is not a valid choice!\n')
            continue
        c = choice
    clear_screen()

    choice_to_fn[c]()

    # Clear temp folder
    shutil.rmtree('temp/')

if __name__ == "__main__":
    main()