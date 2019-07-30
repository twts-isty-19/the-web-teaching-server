echo "Grab all python dependencies..."
pip3 install --user --upgrade pip >/dev/null
pip3 install --user  -r webapp/requirements.txt > /dev/null
echo "Python deps grabbed!"

ELEPHANTSQL_KEY="a125754c-7551-482a-bd45-ab24c19ca9bd"


if [ -z "$DB_URI" ]
then
    export DB_URI=`curl -s -u :$ELEPHANTSQL_KEY \
    -d "name=test&plan=turtle&region=amazon-web-services::us-east-1" \
    https://customer.elephantsql.com/api/instances \
    | jq '.url' \
    | tr -d '"'`

    echo "DB_URI=$DB_URI">> .env
fi

# Waiting the DB is setted up
sleep 2

if [ -z "$SECREY_KEY" ]
then
    export SECREY_KEY=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-67};echo;`
    echo "SECREY_KEY=$SECREY_KEY" >> .env
fi

echo "Instianciate database, populating it..."
cd webapp
if ! python3 scripts/create_chapters.py; then
    exit;
fi
if ! python3 scripts/create_mock_users.py; then
    exit;
fi
cd -
echo "Database instanciated and populated!"

# Hack in order to discard auto-commit from glitch
echo '#!/bin/sh
if grep -q "Checkpoint$" "$1"; then
        echo "Skipping default commit" >> /tmp/message
        exit 1
fi' > /app/.git/hooks/prepare-commit-msg && chmod +x /app/.git/hooks/prepare-commit-msg

refresh
