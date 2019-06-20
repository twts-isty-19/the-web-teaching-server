echo "Grab all python dependencies..."
pip3 install --user --upgrade pip >/dev/null
pip3 install --user  -r requirements.txt > /dev/null
echo "Python deps grabbed!"
