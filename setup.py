from setuptools import setup

import versioneer


def readme():
    with open('README.rst') as f:
        return f.read()


def requirements():
    with open('requirements.txt') as f:
        return f.readlines()


setup(
    name='woodpecker',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Lightweight Load Test and Analysis Tool',
    long_description=readme(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Information Technology',
        ' '.join(('License :: OSI Approved ::',
                  'GNU Lesser General Public License v3 (LGPLv3)')),
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
    package_data={'': ['*.sql']},
    install_requires=requirements(),
    include_package_data=True,
    zip_safe=False
)
