#!/bin/bash
set -x
set -e
VIRTUALENV_CMD=${VIRTUALENV_CMD:-virtualenv}
export PYTHON=${PYTHON:-python}

$VIRTUALENV_CMD ./ENV
ENV/bin/pip install -r ./dependencies.dbus.txt || :
cd ENV/build/dbus-python
chmod +x ./configure
PYTHON=../../bin/python ./configure --prefix=`pwd`/../../
make
make install
cd ../../..
ENV/bin/pip install -r ./dependencies.txt
for name in glib gobject; do
  dir="$($PYTHON -c "import os; import site; print([ os.path.join(x, '$name') for x in site.getsitepackages() + [site.getusersitepackages()] if os.path.isdir(os.path.join(x, '$name'))][0])")"
  ln -s $dir "ENV/lib/$(ls -1 ENV/lib|grep python)/site-packages/"
done
