rm -rf _build
python3 build.py
cd js_basic_game
git pull origin main
cp css/*.css ../_build/reDocs/css
mkdir ../_build/reDocs/js
cp js/*.js ../_build/reDocs/js
cd ..
cd _build/reDocs
python3 -m http.server
