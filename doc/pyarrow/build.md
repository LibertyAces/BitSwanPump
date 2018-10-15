lxc launch images:alpine/3.8 pyarrow-build
lxc exec pyarrow-build  -- /bin/ash

apk add gcc g++ git jemalloc boost-dev zlib flex bison libexecinfo python3-dev glib musl-dev cmake make py3-numpy py-numpy-dev

pip3 install six pandas cython pytest

mkdir -p /opt/repos/dist
cd /opt/repos
git clone https://github.com/apache/arrow.git

cd /opt/repos/arrow
git checkout tags/apache-arrow-0.11.0

export ARROW_BUILD_TYPE=debug
export ARROW_HOME=/opt/repos/dist
export PARQUET_HOME=/opt/repos/dist
export LD_LIBRARY_PATH=/opt/repos/dist/lib64:$LD_LIBRARY_PATH

mkdir /opt/repos/arrow/cpp/build

wget https://raw.githubusercontent.com/TeskaLabs/bspump/alpine-pyarrow-doc/doc/pyarrow/patch-0.11.0.diff
patch /opt/repos/arrow/cpp/src/arrow/util/logging.cc < patch-0.11.0.diff
rm patch-0.11.0.diff

rm /usr/bin/python
ln -s /usr/bin/python3 /usr/bin/python

cd /opt/repos/arrow/cpp/build
cmake -DCMAKE_BUILD_TYPE=$ARROW_BUILD_TYPE \
	  -DCMAKE_INSTALL_PREFIX=$ARROW_HOME \
	  -DARROW_PLASMA=on \
	  -DARROW_PYTHON=on \
	  -DARROW_BUILD_TESTS=OFF \
	  -DARROW_PARQUET=on \
	  ..

make -j4
make install

ln -s /opt/repos/dist/lib64/libarrow.so /opt/repos/dist/lib64/libarrow.so.
ln -s /opt/repos/dist/lib64/libarrow_python.so /opt/repos/dist/lib64/libarrow_python.so.
ln -s /opt/repos/dist/lib64 /opt/repos/dist/lib

cd /opt/repos/arrow/python
python3 setup.py build_ext --build-type=$ARROW_BUILD_TYPE --with-parquet --bundle-arrow-cpp --inplace

cd /opt/repos/arrow/python/pyarrow
ln -s libarrow_python.so libarrow_python.so.11
ln -s libarrow.so libarrow.so.11

cd /opt/repos/arrow/python
tar czvf pyarrow_0_11_0-36m-x86_64-alpine38.tar.gz pyarrow
