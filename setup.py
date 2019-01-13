#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="streamscrobbler",
    packages=["streamscrobbler"],
    version="0.0.2",
    description="A python class used on Dirble.com to get titles and bitrates on shoutcast and icecast streams",
    author="Håkan Nylén",
    author_email="confacted@gmail.com",
    url="https://github.com/Dirble/streamscrobbler-python",
    keywords=["shoutcast", "icecast", "stream", "ICY"],
    install_requires=["httplib2"],
    classifiers=[],
    include_package_data=True
)
