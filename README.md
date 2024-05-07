# What ❓

An automation tool to generate shorts (youtube shorts/tiktok/instagram reels)

# Download 📁

1. Clone the source code

```
git clone https://github.com/caffeinated01/ShortsGenerator
```

2. Once done go into the directory,

```
cd ShortsGenerator
```

3. for **first time running**, install all dependencies first,

```
pip install -r requirements.txt
```

4. and **install ImageMagick** from the [official website](https://imagemagick.org/script/download.php) **OR** use a package manager to do so

5. Make sure you have x264 and ffmpeg packages 

6. Setup your reddit app at https://reddit.com/prefs/apps

   1. Select Are you a developer? Create an app, or Create another app.
   2. Set up your application.
      1. Give your application an appropriate name under the 'name' field.
      2. Select 'script' under the radio menu
      3. You can leave the 'description' and 'about url' fields blank
      4. Under 'redirect uri', type in http://localhost:8000
      5. Complete the catcha
   3. Now, copy your Client ID (string of text found under the words 'personal use script' and the name of your app) and Client Secret (found under the 'secret' field)

7. When you run the code for the first time, a file called '.env' will show up. If you cannot see the file, enable your file explorer to show hidden files. Fill up the two fields with your Client ID and Client Secret you copied earlier.

# Running 🚀

In the source code directory,

```
python app.py
```

Follow the instructions and let the program run

# Credits ©️

[Tiktok TTS Module](https://github.com/Giooorgiooo/TikTok-Voice-TTS)
