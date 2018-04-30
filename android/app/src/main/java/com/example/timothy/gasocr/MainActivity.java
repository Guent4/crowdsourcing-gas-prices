package com.example.timothy.gasocr;

import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.ColorMatrix;
import android.graphics.ColorMatrixColorFilter;
import android.graphics.Paint;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.hardware.Camera;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONObject;

import android.support.design.widget.Snackbar;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;

public class MainActivity extends AppCompatActivity {
    public static final String EXTRA_MESSAGE = "com.example.timothy.gasocr.MESSAGE";
    Button captureButton;
    Button mapButton;
    EditText priceRegularText;
    EditText pricePremiumText;
    EditText priceDieselText;
    EditText companyName;
    Camera camera;
    FrameLayout frameLayout;
    LocationManager locationManager;
    ShowCamera showCamera;
    RequestQueue queue;
    String url;

    String imageRepresentation;
    String timestamp;
    String location;
    String longitude;
    String latitude;
    String prices;
    String company;
    String postPrice;
    String historyCompany;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        url = "http://ec2-18-191-6-17.us-east-2.compute.amazonaws.com/upload_gas_price";

        queue = Volley.newRequestQueue(this);

        frameLayout = findViewById(R.id.frameLayout);
        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        priceRegularText = findViewById(R.id.editText);
       // pricePremiumText = findViewById(R.id.editText2);
       // priceDieselText = findViewById(R.id.editText3);
        companyName = findViewById(R.id.editText4);

        obtainLocation();
        camera = Camera.open();
        showCamera = new ShowCamera(this, camera);
        frameLayout.addView(showCamera);

        captureButton = findViewById(R.id.button);
        captureButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                camera.takePicture(null, null, mPicture);
                Snackbar.make(findViewById(R.id.frameLayout), "Submitted Image!", Snackbar.LENGTH_LONG).setAction("Action", null).show();
            }
        });

        mapButton = findViewById(R.id.button2);
        mapButton.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                openMap(v);
            }
        });

    }

    //data contains the image data
    Camera.PictureCallback mPicture;

    {
        mPicture = new Camera.PictureCallback() {
            @Override
            public void onPictureTaken(byte[] data, Camera camera) {

                if (location == null) {
                    try {
                        Location loc = locationManager.getLastKnownLocation(locationManager.GPS_PROVIDER);
                        location = "loc:" + loc.getLongitude() + "," + loc.getLatitude();
                        longitude = loc.getLongitude() + "";
                        latitude = loc.getLatitude() + "";
                    } catch (SecurityException se) {
                        se.printStackTrace();
                    }
                }
                    Bitmap bitmap = BitmapFactory.decodeStream(new ByteArrayInputStream(data));
                    Bitmap grayscaled = Bitmap.createBitmap(bitmap.getWidth(), bitmap.getHeight(), Bitmap.Config.ARGB_8888);
                    Canvas c = new Canvas(grayscaled);
                    ColorMatrix cm = new ColorMatrix();
                    Paint paint = new Paint();
                    cm.setSaturation(0);
                    paint.setColorFilter(new ColorMatrixColorFilter(cm));
                    c.drawBitmap(bitmap, 0, 0, paint);
                    ByteArrayOutputStream stream = new ByteArrayOutputStream();
                    grayscaled.compress(Bitmap.CompressFormat.JPEG, 80, stream);

                    TimeZone tz = TimeZone.getTimeZone("UTC");
                    DateFormat df = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");
                    df.setTimeZone(tz);
                    timestamp = df.format(new Date());
                    String regularPrice = priceRegularText.getText().toString();
                    String premiumPrice = pricePremiumText.getText().toString();
                    String dieselPrice = priceDieselText.getText().toString();
                    prices = "Reg: " + regularPrice + "Pre: " + premiumPrice + "Dies: " + dieselPrice;
                    postPrice = priceRegularText.getText().toString();
                    company = companyName.getText().toString();
                    //TODO: change url
                   // url = "https://"+ companyName.getText().toString() + ".localtunnel.me/upload_gas_price";
                    byte[] imageRep = stream.toByteArray();
                    imageRepresentation = Base64.encodeToString(imageRep, Base64.DEFAULT);
                    sendPOSTRequest();
            }
        };
    }

    private void sendPOSTRequest(){
        Map<String,String> params = new HashMap();
        params.put("latitude", latitude);
        params.put("longitude",longitude);
        params.put("price", postPrice);
        params.put("timestamp",timestamp);
        params.put("companyname",company);
        params.put("image",imageRepresentation);

        JSONObject parameters = new JSONObject(params);
        JsonObjectRequest postRequest = new JsonObjectRequest(Request.Method.POST,url,parameters,
                new Response.Listener<JSONObject>(){
                    @Override
                    public void onResponse(JSONObject response){
                        Log.d("Response",response.toString());
                    }
                },
                new Response.ErrorListener(){
                    @Override
                    public void onErrorResponse(VolleyError error){
                        Log.d("Error.Response", error.toString());
                    }
                });
        queue.add(postRequest);
    }

    /**
     * Obtain GPS location to be used on user photograph capture
     */
    private void obtainLocation(){
        List<String> providers = locationManager.getProviders(true);
        try {
            for (String provider : providers) {
                locationManager.requestLocationUpdates(provider, 1000, 0,
                        new LocationListener() {
                            public void onLocationChanged(Location loc) {
                                location = "loc:" + loc.getLongitude() + "," + loc.getLatitude();
                                longitude = loc.getLongitude() + "";
                                latitude = loc.getLatitude() + "";
                            }

                            public void onProviderDisabled(String provider) {
                            }

                            public void onProviderEnabled(String provider) {
                            }

                            public void onStatusChanged(String provider, int status, Bundle extras) {
                            }
                        });
            }
        }catch(SecurityException se){
            se.printStackTrace();
        }
    }

    public void openMap(View view){
        obtainLocation();
        if (location == null) {
            try {
                Location loc = locationManager.getLastKnownLocation(locationManager.GPS_PROVIDER);
                location = "loc:" + loc.getLongitude() + "," + loc.getLatitude();
                longitude = loc.getLongitude() + "";
                latitude = loc.getLatitude() + "";
            } catch (SecurityException se) {
                se.printStackTrace();
            }
        }
        Intent intent = new Intent(this,DisplayMapActivity.class).putExtra(EXTRA_MESSAGE,location);
        startActivity(intent);
    }

    public void openHistory(View view){
        obtainLocation();
        if (location == null) {
            try {
                Location loc = locationManager.getLastKnownLocation(locationManager.GPS_PROVIDER);
                location = "loc:" + loc.getLongitude() + "," + loc.getLatitude();
                longitude = loc.getLongitude() + "";
                latitude = loc.getLatitude() + "";
            } catch (SecurityException se) {
                se.printStackTrace();
            }
        }
        Intent intent = new Intent(this,HistoricalData.class).putExtra(EXTRA_MESSAGE,location + "&" + historyCompany);
        startActivity(intent);
    }
}

