rm -rf /root/dist-packages/Gmetad
rm -rf /root/gmetad-python/build
rm /usr/local/lib64/ganglia/python_modules/gmetad/*
cd /root/gmetad-python
python setup.py build
python setup.py install
