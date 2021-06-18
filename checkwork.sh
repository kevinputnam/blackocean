rm -rf _build
python3 build.py
cd _build/reDocs
python3 -m http.server
