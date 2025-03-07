window.onload = function () {
  var mapContainer = document.getElementById("subMap");
  var rvContainer = document.getElementById("roadview");

  var options = {
    center: new kakao.maps.LatLng(37.5518927, 126.9917822),
    level: 4,
  };

  var subMap = new kakao.maps.Map(mapContainer, options);
  var roadview = new kakao.maps.Roadview(rvContainer);
  var roadviewClient = new kakao.maps.RoadviewClient();

  // 부모로부터 메시지를 받을 이벤트리스너 생성
  window.addEventListener("message", function (e) {
    if ("polygons" in e.data) {
      display_polygon(e.data);
    } else if ("position" in e.data) {
      showRoadMap(e.data);
    }
  });

  let existingPolygons = []; // 기존 폴리곤들을 저장할 배열

  function clearExistingPolygons() {
    // 기존 폴리곤들 제거
    existingPolygons.forEach((polygon) => {
      polygon.setMap(null);
    });
    existingPolygons = []; // 배열 초기화
  }

  function display_polygon(data) {
    $(".roadview").css("visibility", "hidden");
    var bounds = new kakao.maps.LatLngBounds();

    clearExistingPolygons(); // 기존 폴리곤을 지운다

    for (var i = 0; i < data.polygons.length; i++) {
      for (var j = 0; j < data.polygons[i].length; j++) {
        var path = new Array();
        for (var k = 0; k < data.polygons[i][j].length; k++) {
          var polygonLatlng = new kakao.maps.LatLng(
            data.polygons[i][j][k][1],
            data.polygons[i][j][k][0]
          );
          path.push(polygonLatlng);
          bounds.extend(polygonLatlng);
        }

        const polygon = new kakao.maps.Polygon({
          path,
          strokeWeight: 2,
          strokeColor: "#004c80", // 기존 색상 사용 (혹은 다른 색상)
          strokeOpacity: 0.8,
          strokeStyle: "solid",
          fillColor: "#fff", // 기존 색상 사용 (혹은 다른 색상)
          fillOpacity: 0.7,
        });

        polygon.setMap(subMap); // 지도에 폴리곤 추가
        existingPolygons.push(polygon); // 새로 생성된 폴리곤을 배열에 추가
      }
    }

    subMap.setBounds(bounds); // 지도 범위 설정
  }

  function showRoadMap(data) {
    if (data["isOpen"]) {
      var position = new kakao.maps.LatLng(
        data["position"]["lat"],
        data["position"]["lng"]
      );

      roadviewClient.getNearestPanoId(position, 50, function (panoId) {
        if (panoId == null) {
          const errorMessage = {
            type: "error",
            message: "가장 가까운 지역의 로드뷰가 존재하지 않습니다.",
          };

          // 프론트로 메시지 전송
          window.parent.postMessage(errorMessage, "*");

          return;
        }

        roadview.setPanoId(panoId, position); // panoId와 중심좌표를 통해 로드뷰 실행
        $(".roadview").css("visibility", "visible");
      });
    } else {
      $(".roadview").css("visibility", "hidden");
    }
  }
};
