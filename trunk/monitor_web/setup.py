from setuptools import setup, find_packages
setup(
    name = "MonitorWeb",
    version = "0.1",
    packages = find_packages(),
    include_package_data = True,
    install_requires = ['django','djangorestframework','MySQL-python>=1.2.3'],
    #scripts = ['manage.py'],
    # installed or upgraded on the target machine
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.conf','*.wsgi'],
        'monitor_web': ['*.conf','*.wsgi'],
        # And include any *.msg files found in the 'hello' package, too:
    },
    # metadata for upload to PyPI
    # platform = 'monitor_web',
    author = "cci",
    author_email = "cci_iaas@citycloud.com.cn",
    description = "This is an cloud monitor web apis",
    url = "http://xxx.com",   # project home page, if any
    # could also include long_description, download_url, classifiers, etc.
    #data_files = [('/etc/apache2/sites-available', ['monitor_web.conf']),
    #              ('/etc',['monitor_web.wsgi']),
    #             ]
)

