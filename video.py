import os
import glob
import requests
from json import loads
from html import unescape
from random import randint, choice
from moviepy.editor import *
from moviepy.audio.fx.volumex import volumex
from moviepy.video.fx.resize import resize
from tts import tts

BACKGROUND_FILE_NAME = './assets/backgrounds/{}.mp4'.format(choice(['bg_minecraft']))
MUSIC_FILE_NAME = './assets/songs/{}.mp3'.format(choice(['bg_phonk']))
FONT_FILE_NAME = './assets/font.ttf'

class Question:
    def __init__(self, title: str, options: list[str], answer: str):
        self.title = title
        self.options = options
        self.answer = answer

def get_question(number: int):
    questions = []

    # Get token so we don't get repeat questions
    token = loads(requests.get('https://opentdb.com/api_token.php?command=request').text)['token']

    endpoint = f'https://opentdb.com/api.php?amount={number}'
    q = loads(requests.get(endpoint).text)['results']

    # Decode strings
    for i in q:
        title = unescape(i['question'])
        answer = unescape(i['correct_answer'])
        options = [unescape(v) for v in i['incorrect_answers']]
        options.insert(randint(0,3), answer)
        questions.append(Question(title, options, answer))

    # De-activate token
    requests.get(f'https://opentdb.com/api_token.php?command=reset&token={token}')
    
    return questions

def generate_video(background: str, music: str, font: str, questions: list[Question]):
    n_questions = len(questions)

    # Length of each part of video
    question_duration = 9
    reveal_duration = 3
    # Length of each question
    i_duration = question_duration + reveal_duration
    
    clips = []
    
    intro_text = f"{n_questions} trivia questions i bet you can't answer"
    outro_text = 'How many did you get correct?'
    tts(intro_text, 'en_us_006', 'temp/intro.mp3')
    intro_audio = volumex(AudioFileClip('temp/intro.mp3'), 2.0)
    intro_duration = intro_audio.duration
    intro_clip = (
        TextClip(
            intro_text, 
            fontsize=70,
            color='#bf55ec', 
            stroke_color='black', 
            stroke_width=4,
            method='caption',
            size=(1080, None),
            font=font
        )
        .set_audio(intro_audio)
        .margin(left=40, right=40, opacity=0)
        .set_start(0)
        .set_duration(intro_duration)
        .set_position(('center', 'center'), relative=True)
    )

    tts(outro_text, 'en_us_006', 'temp/outro.mp3')
    outro_audio = volumex(AudioFileClip('temp/outro.mp3'), 2.0)
    outro_duration = outro_audio.duration
    outro_clip = (
        TextClip(
            outro_text, 
            fontsize=70,
            color='#bf55ec', 
            stroke_color='black', 
            stroke_width=4,
            method='caption',
            size=(1080, None),
            font=font
        )
        .set_audio(outro_audio)
        .margin(left=40, right=40, opacity=0)
        .set_start(i_duration * n_questions + intro_duration)
        .set_duration(outro_duration)
        .set_position(('center', 'center'), relative=True)
    )
    
    # Loop through questions
    for idx, question in enumerate(questions):
        # Make text clip for title
        title = (
            TextClip(
                f'{idx+1}. {question.title}',
                fontsize=70,
                color='#a1daff',
                stroke_color='black',
                stroke_width=4,
                kerning=3,
                method='caption',
                size=(1080, None),
                font=font
            )
            .margin(left=40, right=40)
            .set_start(intro_duration + (idx * i_duration))
            .set_duration(question_duration)
            .set_position(('center', 0.08), relative=True)
        )

        clips.append(title)
        
        option_idxs = ['a','b','c','d']
        
        # Make text clip for options
        options = (
            TextClip(
                '\n\n'.join([f'{option_idxs[i]}. {question.options[i]}' for i in range(len(question.options))]),
                fontsize=80,
                color='white',
                stroke_color='black',
                stroke_width=4,
                method='caption',
                size=(1080, None),
                font=font
            )
            .margin(left=40, right=40, opacity=0)
            .set_start(intro_duration + (idx * i_duration))
            .set_duration(question_duration)
            .set_position(('center', 'center'), relative=True)
        )
        clips.append(options)

        # Make individual text clips for timer
        timer = [
            (
                TextClip(
                    str(question_duration-(i)), 
                    fontsize=150, 
                    color='yellow', 
                    stroke_color='black', 
                    stroke_width=4,
                    method='caption',
                    size=(1080, None),
                    font=font
                )
                .set_start(intro_duration + (idx * i_duration) + i)
                .set_duration(1)
                .set_position(('center', 0.87), relative=True)
            ) for i in range(question_duration)
        ]
        clips += timer
        
        answer_idx = question.options.index(question.answer)
        
        # Make text clip for answer
        answer = (
            TextClip(
                    f'{option_idxs[answer_idx]}. {question.answer}', 
                    fontsize=100,
                    color='#4cbb17', 
                    stroke_color='black', 
                    stroke_width=4,
                    method='caption',
                    size=(1080, None),
                    font=font
                )
                .margin(left=40, right=40, opacity=0)
                .set_start(intro_duration + (idx * i_duration) + question_duration)
                .set_duration(reveal_duration)
                .set_position(('center', 'center'), relative=True)
        )

        clips.append(answer)
        
    song_clip = volumex(AudioFileClip(music).set_duration(i_duration * n_questions + intro_duration + outro_duration), 0.7)
    
    background_clip = VideoFileClip(background)
    background_duration = background_clip.duration
    # Get a random part of background video, make sure background clip is in correct resolution
    background_clip = resize(
        (
            background_clip.cutout(0, randint(1, round(background_duration) - (i_duration * n_questions))).set_duration(i_duration * n_questions + intro_duration + outro_duration).set_position('center','center')
        ),
        height=1920,
    ).set_audio(song_clip)



    # Combine all components & render final video
    result = CompositeVideoClip(
        clips=[background_clip, intro_clip, *clips, outro_clip]
        ,
        size=(1080,1920)
    )
    
    result.write_videofile(
        'out/trivia.mp4',
        fps=24,
        bitrate=None,
        audio=True,
        audio_fps=44100,
        preset='medium',
        audio_nbytes=4,
        audio_bitrate=None,
        audio_bufsize=2000,
        temp_audiofile='temp/temp.mp3'
    )
    
    # Clear temp file
    temp = glob.glob('./temp/*')
    for f in temp:
        os.remove(f)

generate_video(BACKGROUND_FILE_NAME, MUSIC_FILE_NAME, FONT_FILE_NAME, get_question(1))