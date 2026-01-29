ymaps.ready(init);
function init(){
    var map = new ymaps.Map("map", {
        center: [55.76, 37.64],
        controls: [
            'geolocationControl',
            'typeSelector'
        ],
        zoom: 10,
    });
    var userCity, userAddress, userX, userY
    var pmAddress, pmCity, pmX, pmY
    var block = document.getElementById('map');
    var placemark
    map.events.add('click', onMapClick)
    function onMapClick(e) {
        document.getElementById('choiceTable').style.cssText = "width: 30rem;"
        var coords = e.get('coords')
        if (placemark) {
            placemark.geometry.setCoordinates(coords);
        }
        else {
            placemark = createPlacemark(coords);
            map.geoObjects.add(placemark);
            placemark.events.add('dragend', function () {
                getAddress(placemark.geometry.getCoordinates());
            });
        }
        getAddress(coords);
    };
    function createPlacemark(coords) {
        return new ymaps.Placemark(coords, {
                iconCaption: 'поиск...'
            },
            {
                iconLayout: 'default#image',
                iconImageHref: '/static/images/geo_point.png',
                iconImageSize: [48, 64],
                iconImageOffset: [-22, -50],
                draggable: true,
                hideIconOnBalloonOpen: false
            });
    }
    function getAddress(coords) {
        placemark.properties.set('iconCaption', 'поиск...');
        ymaps.geocode(coords).then(function (res) {
            var geo_point = res.geoObjects.get(0);
            pmAddress = String(geo_point.properties.get('text'))
            pmCity = String(geo_point.properties.get('name'))
            pmX = String(geo_point.geometry.getCoordinates()[0])
            pmY = String(geo_point.geometry.getCoordinates()[1])
            data = {

                'user_x': userX,
                'user_y': userY,
                'user_address': userAddress,
                'user_city': userCity,
                'pm_x': pmX,
                'pm_y': pmY,
                'pm_address': pmAddress,
                'pm_city': pmCity
            }
            $.ajax({
                type: 'GET',
                url: "/articles/add",
                data: data,
                success: function(response){ console.log("SUCCESS") },
                error: function(response) {console.log("ERROR")}
            })
            document.getElementById('address_choice').innerHTML = pmAddress
            document.getElementById('city_choice').innerHTML = pmCity
            document.getElementById('x_choice').innerHTML = pmX
            document.getElementById('y_choice').innerHTML = pmY
            placemark.properties
                .set({
                    iconCaption: [
                    geo_point.getLocalities().length ? geo_point.getLocalities() : geo_point.getAdministrativeAreas(),
                    geo_point.getThoroughfare() || geo_point.getPremise()
                    ].filter(Boolean).join(', '),
                    balloonContent: geo_point.getAddressLine()
            });
        });
    }
    var location = ymaps.geolocation.get({provider: 'browser'});
    location.then(
        function(result) {
            map.geoObjects.add(result.geoObjects)
            var userCoordinates = result.geoObjects.get(0).geometry.getCoordinates();
            userX = String(userCoordinates[0])
            userY = String(userCoordinates[1])
            userCity = String(result.geoObjects.get(0).properties.get('name'))
            userAddress = String(result.geoObjects.get(0).properties.get('text'))

            document.getElementById('address_loc').innerHTML = userAddress
            document.getElementById('city_loc').innerHTML = userCity
            document.getElementById('x_loc').innerHTML = userCoordinates[0]
            document.getElementById('y_loc').innerHTML = userCoordinates[1]
        },
        function(err) {
            console.log('Ошибка: ' + err)
        }
    );
}
