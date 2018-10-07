#!/usr/bin/env bash
export NATURESIM_PRJ_PATH=/home/pi/natureSim
if [ -e $NATURESIM_PRJ_PATH ]; then
  source $NATURESIM_PRJ_PATH/.sunlight_control.env
  $NATURESIM_PRJ_PATH/SunlightControl/script/python3/sunlight_control.py > $NATURESIM_PRJ_PATH/log/SunLight.log 2>&1
else
  echo 'Couldnt find a project location.'
fi
