import time
from datetime import datetime
from random import choice
import os
from platform import system
import shutil
from dotenv import set_key
import getpass
from threading import Semaphore
from instagrapi import Client
from reddit import RedditShort
from trivia import TriviaShort

BACKGROUND_FILE_NAME = './assets/backgrounds/{}.mp4'.format(
    choice(['bg_minecraft']))
MUSIC_FILE_NAME = './assets/songs/{}.mp3'.format(choice(['bg_phonk']))
FONT_FILE_NAME = './assets/font.ttf'


def generate_job_id():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'job_{timestamp}'


def clear_screen():
    os_name = system()
    if os_name == 'Windows':
        os.system('cls')
    elif os_name in ('Linux', 'Darwin'):
        os.system('clear')


def generate_trivia(job_id):
    n_videos = int(input('> How many videos: '))
    n_questions_per_video = int(input('> How many questions per video: '))
    n_threads = input(
        "> How many thread to dedicate (recommended ~5), 'n' to disable multithreading: ")

    # Generate directory for video output
    os.makedirs(f'./out/{job_id}')

    if n_threads.lower() == 'n':
        for i in range(n_videos):
            clear_screen()
            short = TriviaShort(BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME,
                                n_questions_per_video, 'trivia_' + str(i+1), job_id, i+1)
            short.start_thread()

            if short.running:
                short.thread.join()

    else:
        semaphore = Semaphore(int(n_threads))

        for i in range(n_videos):
            clear_screen()
            # Multithreading
            with semaphore:
                short = TriviaShort(BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME,
                                    n_questions_per_video, 'trivia_' + str(i+1), job_id, i+1)
                short.start_thread()
                # Delay so can fetch questions
                time.sleep(10)


def generate_reddit(job_id):
    env_user = os.getenv('REDDIT_CLIENT_ID')
    env_pw = os.getenv('REDDIT_CLIENT_SECRET')

    using_stored = False

    if env_user == '' or env_pw == '':
        print(
            'Reddit app credentials not found in config file [.env], please check https://github.com/caffeinated01/ShortsGenerator/blob/main/README.md for instructions')
    else:
        print('Reddit app credentials found in config file [.env]...')
        while True:
            use_credentials = input('> Use stored credentials? [y/n]: ')
            match use_credentials.lower():
                case 'y':
                    using_stored = True
                    break
                case 'n':
                    break
                case _:
                    print(f'{use_credentials} is not a valid choice!')
                    continue

    clear_screen()

    user = input(
        '> Reddit app Client ID: ') if using_stored == False else env_user
    if using_stored == False:
        print('Your Client Secret will not show as you type it (UX 101)')
    pw = getpass.getpass(
        prompt='> Reddit app Client Secret: ') if using_stored == False else env_pw

    exclude_existing = input(
        '> Do you want to skip posts that have already been generated before [y/n]: ')
    match exclude_existing.lower():
        case 'y':
            with open('reddit_generated_before.txt', 'r') as f:
                l = f.readlines()
            existing = [i.strip() for i in l]
            print(existing)
        case '_':
            existing = []

    n_videos = int(input('> How many videos: '))
    n_comments_per_video = int(input('> How many comments per video: '))
    subreddit = input('> What subreddit to find post from: r/')
    n_threads = input(
        "> How many thread to dedicate (recommended ~5), 'n' to disable multithreading: ")

    # Generate directory for video output
    os.makedirs(f'./out/{job_id}')

    if n_threads.lower() == 'n':
        for i in range(n_videos):
            clear_screen()
            short = RedditShort(user, pw, BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME,
                                subreddit, n_comments_per_video, existing, 'reddit_' + str(i+1), job_id, i+1)
            short.start_thread()

            if short.running:
                short.thread.join()

    else:
        semaphore = Semaphore(int(n_threads))

        for i in range(n_videos):
            clear_screen()
            # Multithreading
            with semaphore:
                short = RedditShort(BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME,
                                    subreddit, n_comments_per_video, 'reddit_' + str(i+1), job_id, i+1)
                short.start_thread()

                time.sleep(10)


def upload_to_ig(job_id):
    cl = Client()

    emojis = ['🤣', '😂', '😹', '🫵', '🙃', '🤔', '🤪', '👀']

    env_user = os.getenv('IG_USERNAME')
    env_pw = os.getenv('IG_PASSWORD')

    using_stored = False

    if env_user == '' or env_pw == '':
        pass
    else:
        print('Instagram credentials found in config file [.env]...')
        while True:
            use_credentials = input('> Use stored credentials? [y/n]: ')
            match use_credentials.lower():
                case 'y':
                    using_stored = True
                    print('Using stored credentials, logging in...')
                    break
                case 'n':
                    break
                case _:
                    print(f'{use_credentials} is not a valid choice!')
                    continue

    clear_screen()

    while True:
        user = input(
            '> Instagram username: ') if using_stored == False else env_user
        if using_stored == False:
            print('Your password will not show as you type it (UX 101)')
        pw = getpass.getpass(
            prompt='> Instagram password: ') if using_stored == False else env_pw
        print('Attempting to login...')
        try:
            cl.login(user, pw)
            break
        except Exception as e:
            print(e)
            print(
                'An error occured while logging in, check that your credentials are right')

    while True:
        store_credentials = 'n'

        if using_stored == False:
            store_credentials = input(
                'Do you want to store/overwrite current credentials in config file [y/n]: ')

        match store_credentials.lower():
            case 'y':
                set_key(dotenv_path='.env',
                        key_to_set='IG_USERNAME', value_to_set=user)
                set_key(dotenv_path='.env',
                        key_to_set='IG_PASSWORD', value_to_set=pw)
                break
            case 'n':
                break
            case _:
                print(f'{store_credentials} is not a valid choice!')
                continue

    c = input(
        '> Enter a caption (skip for default) [You can add hashtags like #YourHashTag]: ')
    caption = f'Follow @{user} for more {choice(emojis)} #reddit #redditstory #askreddit #showerthoughts #trivia #shorts #cool #story #reels #didyouknow #foryoupage #fyp' if c == '' else c

    dir = f'out/{job_id}'

    for f in os.listdir(dir):
        if f.endswith('.mp4'):
            cl.clip_upload(path=f'out/{job_id}/{f}', caption=caption, thumbnail=f'out/{job_id}/{f[:-3]}png', extra_data={
                'like_and_view_counts_disabled': 1
            })
            print('Sucess!')


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
        '2': 'Reddit Short',
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
IG_USERNAME = 
IG_PASSWORD = 
''')
        env.close()

    if not os.path.isfile('reddit_generated_before.txt'):
        f = open('reddit_generated_before.txt', 'w')
        f.close()

    c = None
    while c == None:
        c_text = '\n'.join([f'[{i}] '+choices[i] for i in choices.keys()])
        print(f'Options\n{c_text}')
        choice = input('> What to generate: ')
        if choice not in choices.keys():
            print(f'{choice} is not a valid choice!\n')
            continue
        c = choice
    clear_screen()

    job_id = generate_job_id()

    choice_to_fn[c](job_id)

    while True:
        upload_choice = input('> Upload to instagram [y/n]: ')
        match upload_choice.lower():
            case 'y':
                upload_to_ig(job_id)
                break
            case 'n':
                break
            case _:
                continue

    # Clear temp folder
    shutil.rmtree('temp/')


if __name__ == "__main__":
    main()
