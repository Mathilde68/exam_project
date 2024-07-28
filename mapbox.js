function mapbox(properties){
    var properties = JSON.parse(properties);
        console.log(properties);
        mapboxgl.accessToken = "{{mapbox_token}}"
        var map = new mapboxgl.Map({
          container: 'map',
          style: 'mapbox://styles/mapbox/streets-v11',
          center: [12.4083, 55.7361],
          zoom: 8.5
        });
        properties.forEach(property => {
          let marker = new mapboxgl.Marker()
            .setLngLat([property.property_lon, property.property_lat]) // Marker coordinates
            .addTo(map);
        })}