#!/bin/bash

echo "Start production deployment..."
OLD_VERSION=$(git describe --abbrev=0 --tags) 
echo "Saving old version: $OLD_VERSION"
git checkout master &> /dev/null
git pull  &> /dev/null
NEW_VERSION=$(git describe --abbrev=0 --tags) 
echo "Pull last version available: $NEW_VERSION"
if [ "$OLD_VERSION" != "$NEW_VERSION" ]; then
    echo "New version available, deploying..."
    git checkout $NEW_VERSION &> /dev/null
    echo "Installing dependencies..."
    pipenv install &> /dev/null
    echo "Migrating database..."
    pipenv run python manage.py migrate  &> /dev/null
    echo "Deployment done!"
    echo "Restarting gunicorn..."
    sudo -S <<< $1 systemctl restart gunicorn
    echo -e "\033[1;32mDeployment done!\033[1;32m"
else
    echo -e "\033[0;31mNo new version available, nothing to do.\033[0;31m"
    
fi