#bin/bash

cp resources/bash_profile ~/.bash_profile
cp resources/gitconfig ~/.gitconfig 

# Install automator script
mkdir -v -p "$HOME/Library/Services/"
cp -v -r resources/Services/* "$HOME/Library/Services/"

mkdir -v -p "$HOME/Library/KeyBindings/"
cp resources/DefaultKeyBinding.dict "$HOME/Library/KeyBindings/DefaultKeyBinding.dict"

mkdir -p "$HOME/bin"

echo 
echo 
echo "GOOD TO ADD AS FAVOURITES IN FINDER"
echo "$HOME/Library/MobileDevice/Provisioning Profiles/"