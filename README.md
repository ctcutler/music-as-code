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

# Use environment
```
source my_env/bin/activate
python3 fh2-test.py
deactivate
```
