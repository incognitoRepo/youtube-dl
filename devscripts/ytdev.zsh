

fd -d 1 'el[0-9]{3}' '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/' | xargs rm
fd -d 1 'hc[0-9]{3}' '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/' | xargs rm
fd -d 1 . '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/eventpickle' | xargs rm
rm -f /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/tb.log
rm -f /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/custom/auto_repr.log
rm -f /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/custom/attribute_err.log
rm -f /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/custom/type_err.log
print $(whence -p youtube-dl)
print $(whence -p python3)

# CFG="reference"
python3 -m youtube_dl 'https://xhamster.com/videos/khloe-gets-fucked-doggystyle-11663353#mlrelated'
# youtube-dl 'https://xhamster.com/videos/khloe-gets-fucked-doggystyle-11663353#mlrelated' --ignore-config
