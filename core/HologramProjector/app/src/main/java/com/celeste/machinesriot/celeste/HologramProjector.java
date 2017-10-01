package com.celeste.machinesriot.celeste;

import android.content.Intent;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.MediaController;
import android.widget.Toast;
import android.widget.VideoView;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import android.view.Window;
import android.view.WindowManager;

import java.io.File;
import java.text.MessageFormat;


public class HologramProjector extends AppCompatActivity {
    private DatabaseReference mDatabase;
    private VideoView videoView;
    private MediaController mp;
    private String url;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        setContentView(R.layout.activity_hologram_projector);
        videoView = (VideoView)findViewById(R.id.videoView);
        mDatabase = FirebaseDatabase.getInstance().getReference("url/current");
        mDatabase.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {

                if (videoView.isPlaying()){
                    Toast.makeText(getApplicationContext(),"Still playing", Toast.LENGTH_SHORT).show();
                    videoView.stopPlayback();
                }
                url=(String)dataSnapshot.getValue();
                videoView.setVideoURI(Uri.parse("android.resource://"+getPackageName()+(String) MessageFormat.format("/raw/{}",url)));
                videoView.start();



                

            }

            @Override
            public void onCancelled(DatabaseError databaseError) {

            }
        });
    }


}
