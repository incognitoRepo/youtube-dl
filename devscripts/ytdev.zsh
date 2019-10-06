# $ python -m youtube_dl          (2.7+)

fd -d 1 'el[0-9]{3}' '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/' | xargs rm
fd -d 1 'hc[0-9]{3}' '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/' | xargs rm
fd -d 1 . '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/eventpickle' | xargs rm
rm /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/tb.log
rm /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/custom/auto_repr.log
rm /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/custom/attribute_err.log
rm /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/custom/type_err.log

CFG="reference"
/Users/alberthan/VSCodeProjects/vytd/bin/ipython3 -im youtube_dl https://www.pornhub.com/view_video.php\?viewkey\=ph565440318d245
