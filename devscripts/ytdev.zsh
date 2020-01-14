v_ytd_path='/Users/alberthan/VSCodeProjects/vytd/' # virtualenv for youtube-dl home path

# GOTCHA: can't put quotes around paths for zsh expansion
rm -f /Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/logs/*.log

print $(whence -p youtube-dl)
print $(whence -p python3)

py_path='/Users/alberthan/VSCodeProjects/vytd/bin/python3'
ytdl_path='/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl'
video_url='https://www.youtube.com/watch?v=vN9y4umE300'

hunter_log() {
  PYTHONHUNTER='~Q(kind="line"),~Q(module_in=["six","pkg_resources"]),Q(filename_contains="youtube"),stdlib=True' python3 -m youtube_dl $video_url &> /Users/alberthan/VSCodeProjects/HDLogger/youtube-dl/logs/hunter.log
}
hunter_long_log() {
  PYTHONHUNTER='~Q(module_in=["six","pkg_resources"]),Q(filename_contains="youtube"),stdlib=True' python3 -m youtube_dl $video_url &> /Users/alberthan/VSCodeProjects/HDLogger/youtube-dl/logs/hunter.long.log
}

if [[ "$pwd" != $ytdl_path ]]; then
  cd $ytdl_path # TODO: do i really need to cd to $ytdl_path here?
  # python3 -m pdb -m youtube_dl $video_url
  python3 -m youtube_dl $video_url
  # hunter_log
  # hunter_long_log
  cd -
else
  python3 -m youtube_dl $video_url
  # hunter_log
  # hunter_long_log
fi

