#!/usr/bin/env bash
export SIMNATURE_PRJ_PATH=~/natureSim
PYVERSION=3.7

export PYTHONPATH=/usr/local/lib/python$PYVERSION:$SIMNATURE_PRJ_PATH/SunlightControl/script/python3
export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python$PYVERSION
source /usr/local/bin/virtualenvwrapper.sh

export WORKON_HOME=~/.virtualenvs

echo "switch to" $1
workon $1
pip install -r $SIMNATURE_PRJ_PATH/SunlightControl/requirements.txt

if [ -e $SIMNATURE_PRJ_PATH ]; then
  source $SIMNATURE_PRJ_PATH/.sunlight_control.env
  $SIMNATURE_PRJ_PATH/SunlightControl/script/python3/sunlight_control.py > $SIMNATURE_PRJ_PATH/log/SunLight.log 2>&1
else
  echo $SIMNATURE_PRJ_PATH ' Couldnt find a project location.'
fi

deactivate
