# rhythmiq-backend
## 1. Introduction

This is the readme from the django backend of the rhythmiq application.

## 2. Installation
To launch the project, you need to retrieve the media available via the following link and store them in the root of the project in the media/ folder.

https://www.swisstransfer.com/d/8a32e5a7-bbd5-4291-9751-feaee5a2aea2

```
├── manage.py
├── media
│   ├── profiles
│   │   ├── 55460864-8c3f-45a8-a06b-dd8113eb5a38.jpeg
│   │   ├── 800a3f55-6c12-4831-be51-095e6c259328.jpg
│   │   └── default_profile_picture.png
│   └── songs
│       ├── 0542059f-27e4-4d4b-bb61-3f460154ab5e.mp3
│       ├── 185a291e-094e-488c-9316-821cd5eac502.mp3
│       ├── 1bf438b2-fb01-442d-a7a3-190b2360aa61.mp3
│       ├── 1c01cf3c-076a-45f4-a069-56e8efde672b.mp3
│       ├── 7d1521e9-a731-472a-be93-b6f5b1cd4fc4.mp3
│       ├── 8584c244-3ed5-45a5-b241-f25515e7a0a1.mp3
│       ├── 8e846a61-0817-432e-a520-38dc3298eee9.mp3
│       ├── bf4b798f-df91-4341-8665-d508d3f7326f.mp3
│       ├── covers
│       │   ├── 040a0b8b-ac00-4bcf-9261-d5bb40400b3a.jpg
│       │   ├── 28805b78-bb5c-4c15-b3d8-e4533337c3d0.jpg
│       │   ├── 2fbbe667-ead1-4a15-a28b-3d15ad759fe6.jpg
│       │   ├── 508c2383-9b8a-4989-a004-36fc0cfd4d0d.jpg
│       │   ├── 771a6986-69a5-4182-b1fc-2a0a3d74cc54.jpg
│       │   ├── 94b3ecee-b0c6-41a5-9c17-eb6cd4e2e037.jpg
│       │   ├── b80b1bc9-b6f2-43ba-93ad-52ee460c302c.jpg
│       │   ├── cb7f59a9-414c-4a56-9758-15d90bc8296b.jpg
│       │   ├── cbd2a077-0fc3-4eaa-88c9-494b8957a4db.jpg
│       │   ├── cfee7f8f-555d-4b3a-aa3e-9dd3454dcd10.jpg
│       │   └── dab43a1f-edb0-4377-9ad5-d561bbeb4925.jpg
│       ├── e90ab666-beda-452f-9867-7f5db9011fa9.mp3
│       ├── f4012655-96de-4d8f-8d37-b6c52710d0b8.mp3
│       └── f46808e4-6377-43f9-bc5b-939802bdcc88.mp3

```

Here are the commands needed to run the project: 
```
sudo apt install ffmpeg

python3 -m venv .venv

source .venv/bin/activate

pip install poetry

poetry install

python3 manage.py migrate

python3 load_fixtures.py

python3 manage.py runserver

```

If you want to save the fixtures here is the command :

```
source .venv/bin/activate
python3 dump_fixtures.py
```

For loading, you need to specify the order of creation in the load_fixtures.py file. (already done)

## 3. Tools used
- Programming language: Python 3.12.3
- Operating System: Ubuntu
- Browser used: FireFox
- Swagger is available when the application is launched

## 4. Developer
Yerly Sevan