from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='woodpecker',
    version='0.0.1',
    description='Lightweight Load Test and Analysis Tool',
    long_description=readme(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing :: Traffic Generation',
        'Topic :: System :: Networking'
    ],
    keywords='load test http analysis loadrunner jmeter transaction',
    url='https://github.com/steromano87/Woodpecker',
    author='Stefano Romano\'',
    author_email='rumix87@gmail.com',
    license='LGPLv3',
    packages=['woodpecker'],
    install_requires=[
        'python-dateutil',
        'colorama',
        'click',
        'psutil',
        'requests'
    ],
    include_package_data=True,
    zip_safe=False
)
