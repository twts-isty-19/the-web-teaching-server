echo "Grab all python dependencies..."
pip3 install --user --upgrade pip >/dev/null
grep -v "psycopg2" webapp/requirements.txt > /tmp/requirements.txt
pip3 install --user  -r /tmp/requirements.txt > /dev/null
echo "Python deps grabbed!"

echo "Instianciate database, populating it..."
python3 webapp/create_chapters.py
python3 webapp/create_mock_users.py
echo "Database instanciated and populated!"