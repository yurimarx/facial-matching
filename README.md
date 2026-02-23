 [![Gitter](https://img.shields.io/badge/Available%20on-Intersystems%20Open%20Exchange-00b2a9.svg)](https://openexchange.intersystems.com/package/facial-matching)
 [![Quality Gate Status](https://community.objectscriptquality.com/api/project_badges/measure?project=intersystems_iris_community%2Ffacial-matching&metric=alert_status)](https://community.objectscriptquality.com/dashboard?id=intersystems_iris_community%2Ffacial-matching)
 [![Reliability Rating](https://community.objectscriptquality.com/api/project_badges/measure?project=intersystems_iris_community%2Ffacial-matching&metric=reliability_rating)](https://community.objectscriptquality.com/dashboard?id=intersystems_iris_community%2Ffacial-matching)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat&logo=AdGuard)](LICENSE)

# facial-matching
Register and validate people using facial recognition


## Description

This full stack application uses DeepFace and InterSystems Vector Search to register and validate faces, allowing for biometric matching, age, ethnicity, and gender estimation. The features are:
* Register persons and your biometric faces 
* Match person using biometric face recognition
* Uses InterSystems Vector Search to store and compare faces
* Uses Deepface to index faces to store into Vector Search

## Prerequisites

Make sure you have [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker desktop](https://www.docker.com/products/docker-desktop) installed.

## Installation

Clone/git pull the repo into any local directory

```
$ git clone https://github.com/yurimarx/facial-matching.git
$ cd facial-matching
$ docker-compose build
$ docker-compose up -d
```

## Tutorial and details

1. https://community.intersystems.com/post/facial-recognition-intersystems-vector-search-and-deepface

2. https://community.intersystems.com/post/using-ai-calculate-family-resemblance

## What does it do

1. Open the App http://localhost:8501/.
2. Register some persons and faces into Register User.
3. Find people using a photo or your camera to find people already registered.

## Credits

1. Deepface: https://github.com/serengil/deepface
2. OEX Full stack template: https://openexchange.intersystems.com/package/iris-fullstack-template
3. Streamlit: https://streamlit.io/
4. InterSystems IRIS: https://www.intersystems.com/products/intersystems-iris/