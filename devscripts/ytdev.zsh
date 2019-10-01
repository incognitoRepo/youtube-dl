# $ python -m youtube_dl          (2.7+)

fd -d 1 'el[0-9]{3}' '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/' | xargs rm

CFG="reference"
/Users/alberthan/VSCodeProjects/vytd/bin/python3 -m youtube_dl --verbose https://www.pornhub.com/view_video.php\?viewkey\=ph5d5270a4e3bca
