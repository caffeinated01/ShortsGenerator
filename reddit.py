import os
import random
import shutil
import threading
import time
from dotenv import load_dotenv
from tts import tts
from moviepy.editor import *
from moviepy.audio.fx.volumex import volumex
from moviepy.video.fx.resize import resize
import praw
import praw.models.reddit.submission
import praw.models.listing.generator
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


load_dotenv()

class Comment:
    def __init__(self, idx: int, body: str, id: str):
        self.idx = idx
        self.body = body
        self.id = id

class Post:
    def __init__(self, id: str, link: str, title: str, body: str, comments: list[Comment]):
        self.id = id
        self.link = link
        self.title = title
        self.body = body
        self.comments = comments

def get_posts(reddit: praw.Reddit, subreddit: str, n_comments: int):

    submissions: list[praw.models.reddit.submission.Submission] = list(reddit.subreddit(subreddit).top(time_filter='day', limit=None))

    post = None
    
    while post == None:
        submission = random.choice(submissions)
        
        if submission.over_18:
            continue

        if submission.over_18:
            continue
    
        if len(submission.comments.list()) < n_comments:
            continue
        
        post = submission
    
    temp = get_details_from_post(post, n_comments)
    
    post = temp
    
    return post
    
def get_details_from_post(post: praw.models.reddit.submission.Submission, n_comments: int):
    id = post.id
    link = 'https://reddit.com' + post.permalink
    title = post.title
    body = post.selftext
    comments = []
    
    post.comments.replace_more(limit=None)

    i = 1
    for comment in post.comments.list():
        i += 1

        if comment.parent_id[0:2] == 't1_':
            continue
        
        if (len(comment.body.split()) > 100):
            continue

        comments.append(Comment(i, comment.body, comment.id))

    comments = comments[:n_comments]

    return Post(id, link, title, body, comments)

def screenshot_title(driver, post: Post):
    title = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#t3_{post.id}')))
    title.screenshot(f'{post.id}.png')
    shutil.move(f'{post.id}.png', f'./temp/{post.id}.png')

def screenshot_comments(driver, post: Post):
    comments = post.comments

    for c in comments:
        comment = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#comment-tree > shreddit-comment:nth-child({c.idx})')))
        
        while True:
            actions = ActionChains(driver)
            actions.move_to_element(comment).perform()
            time.sleep(1)
            if comment.is_displayed:
                comment.screenshot(f'{post.id}_{c.id}.png')
                break

        shutil.move(f'{post.id}_{c.id}.png', f'./temp/{post.id}_{c.id}.png')

def initialise_all(subreddit, n_comments):
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent="script by u/caffeinated01",
    )  

    post = get_posts(reddit, subreddit=subreddit, n_comments=n_comments)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


    driver.get(post.link)
    screenshot_title(driver, post)
    screenshot_comments(driver, post)
    driver.quit()

    return post

class RedditShort:
    def __init__(self, background: str, music: str, font: str, subreddit: str, n_comments: int, output: str, job_id: str, iteration: int):
        self.background = background
        self.music = music
        self.font = font
        self.post: Post = initialise_all(subreddit, n_comments)
        self.output = output
        self.job_id = job_id
        self.iteration = iteration
        self.running = True
        self.thread = None

    def generate_video(self):
        clips = []
        duration = 0

        post_id = self.post.id

        path_to_title_screenshot = f'temp/{post_id}.png'

        if not os.path.exists(f'temp/{self.iteration}'):
            os.mkdir(f'temp/{self.iteration}')

        # Generate intro and outro text clips
        intro_text = self.post.title


        tts(intro_text, 'en_us_006', f'temp/{self.iteration}/intro.mp3')
        intro_audio = volumex(AudioFileClip(f'temp/{self.iteration}/intro.mp3'), 3.0)
        intro_duration = intro_audio.duration
        intro_clip = resize(
            (ImageClip(
                path_to_title_screenshot
            )
            .set_audio(intro_audio)
            .margin(left=40, right=40, opacity=0)
            .set_start(0)
            .set_duration(intro_duration)
            .set_position(('center', 'center'), relative=True)),
            1.7
        )

        duration+=intro_duration

        for comment in self.post.comments:
            path_to_comment_screenshot = f'temp/{post_id}_{comment.id}.png'

            tts(comment.body, 'en_us_006', f'temp/{self.iteration}/{post_id}_{comment.id}.mp3')
            comment_audio = volumex(AudioFileClip(f'temp/{self.iteration}/{post_id}_{comment.id}.mp3'), 3.0)
            comment_duration = comment_audio.duration
            comment_clip = resize(
                (ImageClip(
                    path_to_comment_screenshot
                ))
                .set_audio(comment_audio)
                .margin(left=40, right=40, opacity=0)
                .set_start(duration)
                .set_duration(comment_duration)
                .set_position(('center', 'center'), relative=True),
                1.7
            )
            clips.append(comment_clip)

            duration+=comment_duration
            
        
        song_clip = volumex(AudioFileClip(self.music).set_duration(duration), 0.3)
        
        background_clip = VideoFileClip(self.background)
        background_duration = background_clip.duration
        # Get a random part of background video, make sure background clip is in correct resolution
        background_clip = resize(
            (
                background_clip.cutout(0, random.randint(1, round(background_duration - (duration)))).set_duration(duration).set_position('center','center')
            ),
            height=1920,
        ).set_audio(song_clip)

        # Combine all components & render final video
        result = CompositeVideoClip(
            clips=[background_clip, intro_clip, *clips] # Unpack clips because CompositeVideoClip does not accept nested list
            ,
            size=(1080,1920)
        )   

        print(f"File 'out/{self.job_id}/{self.output}.mp4' has started generating.")

        result.write_videofile(
            f'out/{self.job_id}/{self.output}.mp4',
            verbose= False,
            logger = None,
            fps=24,
            bitrate=None,
            audio=True,
            audio_fps=44100,
            preset='medium',
            audio_nbytes=4,
            audio_bitrate=None,
            audio_bufsize=2000,
            temp_audiofile=f'temp/{self.iteration}/temp.mp3'
        )

    def start_thread(self):
        self.thread = threading.Thread(target=self.generate_video)
        self.thread.start()
