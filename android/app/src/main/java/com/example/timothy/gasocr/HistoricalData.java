package com.example.timothy.gasocr;

import android.content.Intent;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.google.android.gms.maps.model.LatLng;
import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.GridLabelRenderer;
import com.jjoe64.graphview.series.DataPoint;
import com.jjoe64.graphview.series.DataPointInterface;
import com.jjoe64.graphview.series.LineGraphSeries;
import com.jjoe64.graphview.series.OnDataPointTapListener;
import com.jjoe64.graphview.series.Series;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.DateFormat;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import java.text.SimpleDateFormat;

public class HistoricalData extends AppCompatActivity {

    String url;
    RequestQueue queue;
    String location;
    String longitude;
    String latitude;
    Double price;
    String time;
    String company;
    GraphView graph;

    ArrayList<JSONObject> pointerDatas = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_historical_data);
        url = "http://ec2-18-191-6-17.us-east-2.compute.amazonaws.com/historical";
        graph = findViewById(R.id.graph);

        Intent intent = getIntent();
        location = intent.getStringExtra(MainActivity.EXTRA_MESSAGE);
        longitude = location.substring(location.indexOf(":")+1,location.indexOf(","));
        latitude = location.substring(location.indexOf(",")+1, location.indexOf("&"));
        company = location.substring(location.indexOf("&")+1);

        queue = Volley.newRequestQueue(this);
        sendGETRequest();
    }

    private void sendGETRequest(){
        Map<String,String> params = new HashMap();
        params.put("latitude", latitude);
        params.put("longitude",longitude);
        params.put("company", company);
        url = url + "?latitude="+latitude+"&longitude="+longitude+"&companyname="+company;
        JSONObject parameters = new JSONObject(params);
        JsonObjectRequest getRequest = new JsonObjectRequest(Request.Method.GET, url, parameters,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        pointerDatas = new ArrayList<>();
                        Iterator<String> keyItr = response.keys();
                        while (keyItr.hasNext()){
                            String key = keyItr.next();
                            try {
                                JSONArray responseObj = response.getJSONArray(key);
                                for (int i = 0; i < responseObj.length(); i++){
                                    JSONObject gaspoint = responseObj.getJSONObject(i);
                                    pointerDatas.add(gaspoint);
                                }
                            }catch (JSONException e) {
                                Log.d("error", e.toString());
                            }
                        }
                        DisplayGraph();
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

    private void DisplayGraph() {
        DataPoint[] priceData = new DataPoint[pointerDatas.size()];
        int index = 0;
        if (pointerDatas != null) {
            DateFormat df = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");
            double timeElapsed;
            Date dateNow = new Date();
            for (JSONObject pricePoint: pointerDatas) {
                try {
                    price = Double.parseDouble(pricePoint.getString("price"));
                    time = pricePoint.getString("timestamp");
                    if (time.indexOf("00:00") != -1) {
                        time = time.substring(0, 25) + "Z";
                    }
                    try{
                        timeElapsed = (double)-(dateNow.getTime() - df.parse(time).getTime())/86400000.0;
                        priceData[index] = new DataPoint(timeElapsed,price);
                        index++;
                    } catch (ParseException e){
                        Log.d("error",e.toString());
                    }
                } catch (JSONException e) {
                    Log.d("error", e.toString());
                }
            }

            LineGraphSeries<DataPoint> series = new LineGraphSeries<>(priceData);
            series.setOnDataPointTapListener(new OnDataPointTapListener() {
                @Override
                public void onTap(Series series, DataPointInterface dataPoint) {
                    Snackbar.make(findViewById(R.id.graph), "Price: " + dataPoint.getY(), Snackbar.LENGTH_LONG).setAction("Action", null).show();
                }
            });
            series.setThickness(10);
            graph.addSeries(series);
            graph.setTitle("Price at: "+ company);
            graph.getViewport().setMinX(-7);
            graph.getViewport().setMaxX(1);
            GridLabelRenderer renderer = graph.getGridLabelRenderer();
            renderer.setHorizontalAxisTitle("Days Ago");
            renderer.setVerticalAxisTitle("Price $");
        }
    }
}
