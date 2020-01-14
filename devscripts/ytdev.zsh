v_ytd_path='/Users/alberthan/VSCodeProjects/vytd/'

# fd -d 1 'el[0-9]{3}' $v_ytd_path | xargs rm
# fd -d 1 'hc[0-9]{3}' '/Users/alberthan/VSCodeProjects/vytd/' | xargs rm
# fd -d 1 'ydl[0-9]{3}' '/Users/alberthan/VSCodeProjects/vytd/' | xargs rm
# fd -d 1 . '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/eventpickle' | xargs rm
rm -f '/Users/alberthan/VSCodeProjects/vytd/tb.log'
rm -f '/Users/alberthan/VSCodeProjects/vytd/bfs.log'
rm -f '/Users/alberthan/VSCodeProjects/vytd/auto_repr_err.log'
# GOTCHA: can't put quotes around paths for zsh expansion
rm -f /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/logs/*.log

print $(whence -p youtube-dl)
print $(whence -p python3)

py_path='/Users/alberthan/VSCodeProjects/vytd/bin/python3'
ytdl_path='/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl'
video_url='https://www.youtube.com/watch?v=vN9y4umE300'
# CFG="reference"
if [[ "$pwd" != $ytdl_path ]]; then
  cd $ytdl_path
  # python3 -m pdb -m youtube_dl $video_url
  python3 -m youtube_dl $video_url
  # PYTHONHUNTER='~Q(kind="line"),~Q(module_in=["six","pkg_resources"]),Q(filename_contains="youtube"),stdlib=True' python3 -m youtube_dl $video_url &> hunter.log
  # PYTHONHUNTER='~Q(module_in=["six","pkg_resources"]),Q(filename_contains="youtube"),stdlib=True' python3 -m youtube_dl $video_url &> hunter.long.log
  cd -
else
  python3 -m youtube_dl $video_url
  # PYTHONHUNTER='~Q(kind="line"),~Q(module_in=["six","pkg_resources"]),Q(filename_contains="youtube"),stdlib=True' python3 -m youtube_dl $video_url &> hunter.log
  # PYTHONHUNTER='~Q(module_in=["six","pkg_resources"]),Q(filename_contains="youtube"),stdlib=True' python3 -m youtube_dl $video_url &> hunter.long.log
fi

srm() {
  arg=${1}
  find $arg
  vared -p 'Delete these files? [Y|n] ' -c tmp # ???
}
