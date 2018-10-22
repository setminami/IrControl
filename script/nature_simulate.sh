#!/usr/bin/env bash
RUNNABLE_PREFIX=/usr/local
SIMNATURE_PRJ_PATH=~/Simnature
PRJ_NAME=SunlightControl
PYVERSION=3.7
PRJ_PATH=${SIMNATURE_PRJ_PATH}/${PRJ_NAME}
DEFAULT_VENV_NAME=SIM_Nature
LOG_DIR=${SIMNATURE_PRJ_PATH}/log
LOG_FILE=${LOG_DIR}/SunLight.txt
LOG_JSON=${LOG_DIR}/SunLight.json
BOOT_LOG_FILE=${LOG_DIR}/boot.txt

# save previous sessions like rotate
DATE_STR=`date "+%Y%m%d-%H%M%S%Z"`
if [ -s ${LOG_FILE} ]; then
  mv ${LOG_FILE} ${LOG_DIR}/${DATE_STR}.sunlight.log
fi

if [ -s ${BOOT_LOG_FILE} ]; then
  # see also. environment/crontab_sample.txt
  mv ${BOOT_LOG_FILE} ${LOG_DIR}/${DATE_STR}.boot.log
  echo `date "+%Y/%m/%d %H:%M:%S"`: start bootup. > ${BOOT_LOG_FILE}
fi

# check & run virtualenv
if [ $# -eq 1 ]; then
  WORK_ENV=$1
else
  echo -e 'usage:' $0 'virtualenvname\nThis Session use' ${DEFAULT_VENV_NAME} 'as default.' >> ${BOOT_LOG_FILE}
  export WORK_ENV=${DEFAULT_VENV_NAME}
fi

export WORKON_HOME=~/.virtualenvs

# start virtualenv with wrapper
source ${WORKON_HOME}/${WORK_ENV}/bin/activate
if [ $? -eq 0 ]; then
    echo "Success activate" ${WORK_ENV} >> ${BOOT_LOG_FILE}
else
    echo "Failure activate" ${WORK_ENV} >> ${BOOT_LOG_FILE}
fi

date "+%Y/%m/%d %H:%M:%S" >> ${BOOT_LOG_FILE}
export PYTHONPATH=${RUNNABLE_PREFIX}/lib/python${PYVERSION}:${PRJ_PATH}/script/python3

# Darwin is develop environment, else is full wired IoT machine
if [ `uname -s` == 'Darwin' ]; then
  echo on `sw_vers -productName` `sw_vers -productVersion` >> ${BOOT_LOG_FILE}
  REQUIRE=DEVELOP.txt
elif [ `uname -s` == 'Linux' ]; then
  # uname -m is ZeroW = 'armv6l', B =...
  echo on `egrep 'PRETTY_NAME=' /etc/os-release` >> ${BOOT_LOG_FILE}
  REQUIRE=ACTUAL.txt
fi

pip list --outdated >> ${BOOT_LOG_FILE}
echo `date "+%Y/%m/%d %H:%M:%S"`: OK startup ${PRJ_NAME}. >> ${BOOT_LOG_FILE}

if [ -e ${PRJ_PATH} ]; then
  echo `date "+%Y/%m/%d %H:%M:%S"`: OK startup ${PRJ_NAME}. >> ${LOG_FILE}
  source ${SIMNATURE_PRJ_PATH}/.sunlight_control.env
  echo `date "+%Y/%m/%d %H:%M:%S"`: env file read done. \(${SIMNATURE_PRJ_PATH}/.sunlight_control.env\) >> ${LOG_FILE}
  ${PRJ_PATH}/script/python3/sunlight_control.py >> ${LOG_FILE} 2>&1
else
  echo ${PRJ_PATH} Couldnt find a project location. >> ${BOOT_LOG_FILE}
fi

deactivate
