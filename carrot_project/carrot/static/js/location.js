let regionSaveButton = document.getElementById('region-save-button');
let mapCreate = document.getElementById('map');

mapOption = {
  // 지도 중심좌표
  center : new kakao.maps.LatLng(33.450701, 126.570667), 
  // 지도 확대 레벨
  level : 6,
};

let map = new kakao.maps.Map(mapCreate, mapOption);


if(navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(function (position) {
    let lat = position.coords.Latitude; //위도
    let lon = position.coords.Longitude; //경도

    //표시되는 위치
    let locationPosition = new kakao.maps.LatLng(lat, lon);
    message = '<div style="padding:5px;">현재위치</div>'

    displayMarker(locationPosition, message);
    var geocoder = new kakao.maps.services.Geocoder();

    function getAddr(lat, lon) {
      let geocoder = new kakao.maps.services.geocoder();
      let coord = new kakao.maps.LatLng(lat, lon);

      let callback = function(result, status) {
        if(status === kakao.maps.services.status.OK) {
          console.log(result);
          let currentLoction = result[0].address.address_name;

          document.getElementById('region-info').innerText =
            "현재위치는 " + result[0].address.address_name + "입니다.";
          
          let regionSettingValue = document.querySelector('input[name="region-setting"]').value;
          let regionArray = regionSettingValue.split(" ");
          let lastRegionPart = regionArray[regionArray.length - 1];
          
          let currentLocationArray = currentLoction.split(" ");
          let regionJudgeText = document.getElementById("region-judge");

          if(currentLocationArray.includes(lastRegionPart)) {
            regionJudgeText.innerText = "현재 위치가 동네 설정과 같습니다.";
          } else {
            regionJudgeText.innerText = "현재 위치가 동네 설정과 다릅니다.";
            // 버튼 비활성화
            regionSaveButton.classList.toggle("button-disabled");
          }
        }
      };
      //좌표로 주소를 얻어내는 함수.
      geocoder.coord2Ade(coord.getLng(), coord.getLat(), callback);
    }
    getAddr(lat, lon);
  });
} else {
  //GeoLocation을 사용할 수 없을때 마커 표시와 infoWindow 내용 설정
  let locationPosition = new kakao.maps.LatLng(33.450701, 126.570667),
  message = "사용자 환경 문제로 위치 정보를 사용할 수 없습니다.";

  displayMarker(locationPosition, message);
}

// displayMarker함수
function displayMarker(locationPosition, message) {
  // 마커생성
  let marker = new kakao.maps.Marker({map:map, position:locationPosition});
  let iwContent = message;
  let iwRemoveable = true;

  // 인포윈도우를 생성하고 지도에 표시합니다
  var infowindow = new kakao.maps.InfoWindow({
    map: map, // 인포윈도우가 표시될 지도
    content : iwContent,
    removable : iwRemoveable
  });

  //infoWindow를 마커에 표시
  infowindow.open(map, marker);
  
  // 지도 중심 좌표로 위치 변경
  map.setCenter(locationPosition);
}

// 빈칸입력 확인 절차
document.getElementById("region-form").addEventListener("submit", function(e) {
  e.preventDefault();

  let region = document.querySelector('input[name="region-setting"]').value;

  if (region.trim()) {
    this.Submit();
  } else {
    alert("지역을 입력해주세요.");
  }
});

regionSaveButton.addEventListener("click", ()=>{
  alert("인증이 완료되었습니다.");
});