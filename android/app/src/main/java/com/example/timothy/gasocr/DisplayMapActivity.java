package com.example.timothy.gasocr;

import android.content.Intent;
import android.hardware.Camera;
import android.location.Location;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.CameraPosition;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.VisibleRegion;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;


public class DisplayMapActivity extends AppCompatActivity implements GoogleMap.OnInfoWindowClickListener, OnMapReadyCallback {

    private GoogleMap mMap;
    String url;
    RequestQueue queue;
    String location;
    String longitude;
    String latitude;
    HashMap<String, ArrayList<JSONObject>> pointerDatas = new HashMap<>();
    float previousZoomLevel = -1;
    boolean isZooming = false;
    double lastTime;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_display_map);
        url = "http://ec2-18-191-6-17.us-east-2.compute.amazonaws.com/map";
        Intent intent = getIntent();
        location = intent.getStringExtra(MainActivity.EXTRA_MESSAGE);
        longitude = location.substring(location.indexOf(":")+1,location.indexOf(","));
        latitude = location.substring(location.indexOf(",")+1);
        lastTime = (double) new Date().getTime();

        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager().findFragmentById(R.id.map);

        mapFragment.getMapAsync(this);

        queue = Volley.newRequestQueue(this);
        sendGETRequest(30);
        addMarkers();
    }

    /**
     *
     */
    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;
        LatLng yourPosition = new LatLng(Double.parseDouble(latitude), Double.parseDouble(longitude));
        mMap.moveCamera(CameraUpdateFactory.newLatLng(yourPosition));
        mMap.addMarker(new MarkerOptions().position(yourPosition).title("Your Position"));
        mMap.moveCamera(CameraUpdateFactory.zoomTo(12));
        mMap.setOnCameraChangeListener(getCameraChangeListener());
    }

    @Override
    public void onInfoWindowClick(Marker marker) {
        String title = marker.getTitle();
        LatLng pos = marker.getPosition();
        String markerLoc = "loc:" + pos.longitude + "," + pos.latitude;
        String markerCompany = title.substring(title.indexOf("at")+3);
        Intent intent = new Intent(this,HistoricalData.class).putExtra(MainActivity.EXTRA_MESSAGE,markerLoc + "&" + markerCompany);
        startActivity(intent);
    }

    public com.google.android.gms.maps.GoogleMap.OnCameraChangeListener getCameraChangeListener(){
        return new GoogleMap.OnCameraChangeListener(){
            @Override
            public void onCameraChange(CameraPosition position) {

                if(previousZoomLevel != position.zoom && previousZoomLevel < position.zoom && ((double) new Date().getTime()- lastTime > 1500 )) {
                    VisibleRegion vr = mMap.getProjection().getVisibleRegion();
                    double top = vr.latLngBounds.northeast.latitude;
                    double bottom = vr.latLngBounds.southwest.latitude;
                    double distance = (top-bottom)*111;
                    lastTime = (double) new Date().getTime();
                    sendGETRequest(distance);
                }
                previousZoomLevel = position.zoom;
            }
        };
    }

    private void sendGETRequest(double distance){
        Map<String,String> params = new HashMap();
        pointerDatas = new HashMap<>();
        String range = distance+"";
        params.put("latitude", latitude);
        params.put("longitude",longitude);
        params.put("range", range);

        String newUrl = url + "?latitude="+latitude+"&longitude="+longitude+"&range="+range;
        JSONObject parameters = new JSONObject(params);
        JsonObjectRequest getRequest = new JsonObjectRequest(Request.Method.GET, newUrl, parameters,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Iterator<String> keyItr = response.keys();
                        while (keyItr.hasNext()){
                            String key = keyItr.next();
                            try {
                                JSONArray responseObj = response.getJSONArray(key);
                                for (int i = 0; i < responseObj.length(); i++){
                                    try {
                                        JSONObject gaspoint = responseObj.getJSONObject(i);
                                        String pointerkey = gaspoint.getString("latitude")+gaspoint.getString("longitude");
                                        if(!pointerDatas.containsKey(pointerkey)){
                                            pointerDatas.put(pointerkey, new ArrayList<JSONObject>());
                                        }
                                        pointerDatas.get(pointerkey).add(gaspoint);
                                    }catch (JSONException e){
                                        Log.d("error", e.toString());
                                    }
                                }
                            }catch (JSONException e) {
                                Log.d("error", e.toString());
                            }
                            addMarkers();
                        }
                        Log.d("Response", response.toString());
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.d("Error.Response", error.toString());
                    }
                });
        queue.add(getRequest);
    }

    private void addMarkers() {
        if (pointerDatas != null) {
            for (String key : pointerDatas.keySet()) {
                try {
                    ArrayList<JSONObject> points = pointerDatas.get(key);
                    JSONObject firstPoint = points.get(0);
                    Double lat = Double.parseDouble(firstPoint.getString("latitude"));
                    Double lon = Double.parseDouble(firstPoint.getString("longitude"));
                    String price = firstPoint.getString("price");
                    String time = firstPoint.getString("timestamp").substring(0,11);
                    String company = firstPoint.getString("companyname");
                    LatLng pos = new LatLng(lat, lon);

                    mMap.addMarker(new MarkerOptions().position(pos).title("$" + price + " on " + time + " at " + company).icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_AZURE)));
                    mMap.setOnInfoWindowClickListener(this);
                } catch (JSONException e) {
                    Log.d("error", e.toString());
                }
            }
        }
    }
}
