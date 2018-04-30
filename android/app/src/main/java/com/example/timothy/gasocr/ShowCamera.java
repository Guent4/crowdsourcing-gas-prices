package com.example.timothy.gasocr;

import android.content.Context;
import android.content.res.Configuration;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.hardware.Camera;

import java.io.IOException;
import java.util.LinkedList;
import java.util.List;

public class ShowCamera extends SurfaceView implements SurfaceHolder.Callback{

    Camera camera;
    SurfaceHolder holder;

    public ShowCamera(Context context, Camera camera) {
        super(context);
        this.camera = camera;
        holder = getHolder();
        holder.addCallback(this);
    }

    @Override
    public void surfaceChanged(SurfaceHolder surfaceHolder, int i, int i1, int i2) {

    }

    @Override
    public void surfaceDestroyed(SurfaceHolder surfaceHolder) {
        camera.stopPreview();
        camera.release();
    }

    @Override
    public void surfaceCreated(SurfaceHolder surfaceHolder) {
        Camera.Parameters params = camera.getParameters();
        List<Camera.Size> sizes = params.getSupportedPictureSizes();
        Camera.Size camSize = sizes.iterator().next();


        params.set("orientation","portrait");
        camera.setDisplayOrientation(90);
        params.setRotation(90);
        params.setPictureSize(3840, 2160);
        camera.setParameters(params);

        try{
            camera.setPreviewDisplay(holder);
            camera.startPreview();
        }catch(IOException e){
            e.printStackTrace();
        }
    }
}
