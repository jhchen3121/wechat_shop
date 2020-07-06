pip_ver=`pip -V|awk '{print $2}'|cut -d . -f 1`
if [ $pip_ver -lt 9 ];then
    pip install -U pip
fi
pip download -r requirements.txt -d packages
