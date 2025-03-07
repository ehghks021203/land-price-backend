from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os
from app.config import APP_DIR
from app.config.key import KAKAO_JAVASCRIPT_API_KEY

# router
map_router = APIRouter(prefix='/map')

@map_router.get('/kakaomap', response_class=HTMLResponse)
async def render_kakaomap():
  html_content = f'''
  <!DOCTYPE html>
  <html style="width: 100%; height: 100%;">
  <head>
    <meta charset="utf-8" />
    <script type="text/javascript"
      src="//dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JAVASCRIPT_API_KEY}&libraries=services"></script>
    <script type="text/javascript"
      src="https://sgisapi.kostat.go.kr/OpenAPI3/auth/javascriptAuth.json?consumer_key=fb1faab8b89b4382ba3d"></script>
    <script src="https://code.jquery.com/jquery-3.6.4.min.js"
      integrity="sha256-oP6HI9z1XaZNBrJURtCoUT5SUnxFr8s3BzRl+cbzUq8=" crossorigin="anonymous"></script>
    <link href="/static/css/style.css" rel="stylesheet">
  </head>

  <body style="width: 100%; height: 100%;">
    <div id="subMap" style="position:absolute;width:100%;height:100%;"></div>
    <div id="roadview" class="roadview" style="position:absolute;width:100%;height:100%;z-index:10;visibility:hidden;"></div>
    <script src="/static/js/kakaomap.js" defer></script>
  </body>
  </html>
  '''
  return HTMLResponse(content=html_content)