function addMarker(properties){
    //console.log(properties)
    properties = JSON.parse(properties)
    console.log(properties)
    properties.forEach( property => {
        let marker = new mapboxgl.Marker()
        .setLngLat([property.property_lon, property.property_lat]) // Marker coordinates
        .addTo(map);        
    })
}

