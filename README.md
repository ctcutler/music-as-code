# Set up
```
brew install portmidi # will take a long time to build
python3.7 -m venv my_env
source my_env/bin/activate
pip install --upgrade pip
pip install mido
pip freeze > requirements.txt
pip install -r requirements.txt
deactivate
```

# Run
```
source my_env/bin/activate
python3 fh2-test.py
deactivate
```

# Philsophy
- plain text, no special/proprietary data format
- human readable, especially in a monospaced font
- intuitive: musically inclined readers can guess the basics without reading this
- code-able: composed of strings that can easily be generated/concatenated algorithmically
  - music is all patterns and variations on those patterns...
  - ... so is code
  - expressing music with code gives us a chance to make the patterns and variations clear
    even clearer than they are in conventional sheet music
  - ... and perhaps compose differently because we have the structural aspects at our
    fingertips

# ASCII Format
