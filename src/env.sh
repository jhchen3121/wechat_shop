#入口参数判断
if [ ! $1 ];then
    PROJ_DIR=`pwd`
else
    PROJ_DIR=$1
fi

VENV=${PROJ_DIR}/.env
PROJ_NAME=wechat_shop

if [ ! -e ${VENV} ];then
    virtualenv --never-download --prompt "(${PROJ_NAME})" ${VENV} -p $(type -p python2.7)
fi

source ${VENV}/bin/activate 

export PYTHONPATH=${PROJ_DIR}/server:${PROJ_DIR}/lib:${PROJ_DIR}
export LD_LIBRARY_PATH=${PROJ_DIR}/lib
export PROJ_NAME
export PROJ_DIR
