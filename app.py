import os
from platform import system
from random import choice
from datetime import datetime
import time
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

# Trivia function
def generate_trivia():
    print('Specify what to automate...')
    
    n_videos = int(input('How many videos: '))
    n_questions_per_video = int(input('How many questions per video: '))

    job_id = generate_job_id()

    # Generate directory for video output
    os.makedirs(f'./out/{job_id}')

    for i in range(n_videos):
        clear_screen()
        short = TriviaShort(BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME, n_questions_per_video, 'trivia_' + str(i+1), job_id)
        short.start_thread()

        # Uncomment for multithreading (make this an option later)
        if short.running:
            short.thread.join()

        print(f'{i+1}/{n_videos} done!')
        time.sleep(1)

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
        '2': '?? (Coming soon)'
    }

    choice_to_fn = {
        '1': generate_trivia
    }

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

if __name__ == "__main__":
    main()