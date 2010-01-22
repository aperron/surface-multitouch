#!/bin/sh
 
if [ "$#" = "0" ]; then
    echo ""
    echo "./record-cam.sh -h pour voir l'utilisation"
    echo ""
fi
if [ "$#" = "1" ]; then
  if [ "$1" = "-h" ] ;then
    echo ""
    echo " example d utilisation : record-video.sh camera.avi 2 30"
    echo " enregistre la webcam sur le fichier camera.avi pendant 2min 30sec"
    echo ""
  else
    streamer -c /dev/video0 -f rgb24 -r 15 -t 00:00:20 -o $1-temp.avi
    mencoder $1-temp.avi -ovc raw -vf format=i420 -o $1.avi
    exec "rm -f $(cd -P -- "$(dirname -- "$0")" && pwd -P)/$1.avi"
    echo "done"
  fi
fi
if [ "$#" = "3" ] ;then
  streamer -c /dev/video0 -f rgb24 -r 15 -t 00:$2:$3 -o $1-temp.avi
  mencoder $1-temp.avi -ovc raw -vf format=i420 -o $1.avi
  exec "rm -f $(cd -P -- "$(dirname -- "$0")" && pwd -P)/$1.avi"
  echo "done"
fi

