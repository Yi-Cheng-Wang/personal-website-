#!/bin/bash
cp -r templates/ ../..
cp -r static/ ../..
cp mainsite/views.py ../../mainsite/
cp myweb/urls.py ../../myweb/
cp -r static/images/ ../../../staticfiles/
cp -r static/css/ ../../../staticfiles/
cp -r static/js/ ../../../staticfiles/
cp -r static/sass/ ../../../staticfiles/
cp -r static/webfonts/ ../../../staticfiles/
sudo systemctl restart apache2
