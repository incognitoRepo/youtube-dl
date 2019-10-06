# $ python -m youtube_dl          (2.7+)

fd -d 1 'el[0-9]{3}' '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/' | xargs rm
fd -d 1 'hc[0-9]{3}' '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/' | xargs rm
fd -d 1 . '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/eventpickle' | xargs rm
rm /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/tb.log
rm /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/custom/auto_repr.log
rm /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/custom/attribute_err.log
rm /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/custom/type_err.log

# CFG="reference"
/Users/alberthan/VSCodeProjects/vytd/bin/python3 -m youtube_dl https://xhamster.com/videos/khloe-gets-fucked-doggystyle-11663353\#mlrelated
