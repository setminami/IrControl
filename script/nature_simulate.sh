#!/usr/bin/env bash
PREFIX=/usr/local
SIMNATURE_PRJ_PATH=~/natureSim
PRJ_NAME=SunlightControl
PYVERSION=3.7
PRJ_PATH=${SIMNATURE_PRJ_PATH}/${PRJ_NAME}
DEFAULT_VENV_NAME=SIM_Nature
LOG_DIR=${SIMNATURE_PRJ_PATH}/log
LOG_FILE=${LOG_DIR}/SunLight.log

if [ -s $LOGFILE ]; then
  mv ${LOG_FILE} ${LOG_DIR}/`date "+%Y%m%d-%H%M%S%Z"`.sunlight.log
fi

if [ $# -eq 1 ]; then
  WORK_ENV=$1
else
  echo -e 'usage:' $0 'virtualenvname\nThis Session use' ${DEFAULT_VENV_NAME} 'as default.'
  export WORK_ENV=${DEFAULT_VENV_NAME}
fi

export WORKON_HOME=~/.virtualenvs
export PYTHONPATH=${PREFIX}/lib/python${PYVERSION}:${PRJ_PATH}/script/python3
export VIRTUALENVWRAPPER_PYTHON=${PREFIX}/bin/python${PYVERSION}
until source ${PREFIX}/bin/virtualenvwrapper.sh; do
  echo fail virtualenv setup
  sleep 10
done

echo OK switch to ${WORK_ENV}
workon ${WORK_ENV}

# Darwin is develop, else is full wired IoT machine
if [ `uname -s` == 'Darwin' ]; then
  echo on `sw_vers -productName` `sw_vers -productVersion`
  REQUIRE=DEVELOP.txt
elif [ `uname -s` == 'Linux' ]; then
  # uname -m is ZeroW = 'armv6l', B =...
  echo on `egrep 'PRETTY_NAME=' /etc/os-release`
  REQUIRE=ACTUAL.txt
fi

pip install -r ${PRJ_PATH}/requirements/$REQUIRE

if [ -e ${PRJ_PATH} ]; then
  source ${SIMNATURE_PRJ_PATH}/.sunlight_control.env
  ${PRJ_PATH}/script/python3/sunlight_control.py > ${SIMNATURE_PRJ_PATH}/log/SunLight.log 2>&1
else
  echo ${PRJ_PATH} Couldnt find a project location.
fi

deactivate
