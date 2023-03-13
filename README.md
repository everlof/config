# Setup a Mac


## Programs to install

- Macdown
- IP in menubar: https://www.monkeybreadsoftware.de/Software/IPinmenubar.shtml
- Paste: https://pasteapp.me
- https://imageoptim.com/mac


# Xcode

## Create file templates

Take templates from `/Applications/Xcode.app/Contents/Developer/Library/Xcode/Templates/File\ Templates`

Create a folder named `Custom` in `~/Library/Developer/Xcode/Templates/` then just find `.xctemplate`s in Xcode.app-subfolder and put in `Custom`.

## Key bindings

Put `David.idekeybindings` in:
`/Users/daveve/Library/Developer/Xcode/UserData/KeyBindings/`

# LLDB

command script import lldb.macosx.crashlog
save_crashlog /some/path/reason_why_crashed.crash

# Finder

**************************************
Terminal commands (paste the entire string)
**************************************
𝗙𝗮𝘀𝘁𝗲𝗿 𝗗𝗼𝗰𝗸 𝗛𝗶𝗱𝗶𝗻𝗴: defaults write com.apple.dock autohide-delay -float 0; defaults write com.apple.dock autohide-time-modifier -int 0;killall Dock
𝗙𝗮𝘀𝘁𝗲𝗿 𝗗𝗼𝗰𝗸 𝗛𝗶𝗱𝗶𝗻𝗴 𝗨𝗻𝗱𝗼: defaults write com.apple.dock autohide-delay -float 0.5; defaults write com.apple.dock autohide-time-modifier -int 0.5 ;killall Dock

𝗔𝗱𝗱 𝗗𝗼𝗰𝗸 𝗦𝗽𝗮𝗰𝗲𝗿 (paste for each spacer): defaults write com.apple.dock persistent-apps -array-add '{tile-data={}; tile-type="spacer-tile";}' && killall Dock
𝗔𝗱𝗱 𝗛𝗮𝗹𝗳-𝗛𝗲𝗶𝗴𝗵𝘁 𝗗𝗼𝗰𝗸 𝗦𝗽𝗮𝗰𝗲𝗿 (paste for each): defaults write com.apple.dock persistent-apps -array-add '{"tile-type"="small-spacer-tile";}' && killall Dock

𝗗𝗶𝘀𝗮𝗯𝗹𝗲 𝗔𝗻𝗻𝗼𝘆𝗶𝗻𝗴 𝗗𝗶𝘀𝗸 𝗪𝗮𝗿𝗻𝗶𝗻𝗴 (must restart Mac to take effect): sudo defaults write /Library/Preferences/SystemConfiguration/com.apple.DiskArbitration.diskarbitrationd.plist DADisableEjectNotification -bool YES && sudo pkill diskarbitrationd
𝗥𝗲-𝗘𝗻𝗮𝗯𝗹𝗲 𝗔𝗻𝗻𝗼𝘆𝗶𝗻𝗴 𝗗𝗶𝘀𝗸 𝗪𝗮𝗿𝗻𝗶𝗻𝗴: sudo defaults delete /Library/Preferences/SystemConfiguration/com.apple.DiskArbitration.diskarbitrationd.plist DADisableEjectNotification && sudo pkill diskarbitrationd
𝗔𝗹𝘁𝗲𝗿𝗻𝗮𝘁𝗲𝗹𝘆, 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗘𝗷𝗲𝗰𝘁𝗶𝗳𝘆: https://ejectify.app

𝗖𝗵𝗮𝗻𝗴𝗲 𝗦𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁 𝗗𝗲𝗳𝗮𝘂𝗹𝘁 𝘁𝗼 𝗝𝗣𝗚 (replace with png to undo): defaults write com.apple.screencapture type jpg

𝗠𝗮𝗸𝗲 𝗛𝗶𝗱𝗱𝗲𝗻 𝗔𝗽𝗽𝘀 𝗧𝗿𝗮𝗻𝘀𝗽𝗮𝗿𝗲𝗻𝘁: defaults write com.apple.Dock showhidden -bool TRUE && killall Dock
