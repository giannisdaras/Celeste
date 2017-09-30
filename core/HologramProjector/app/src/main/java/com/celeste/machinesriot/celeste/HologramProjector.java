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


public class HologramProjector extends AppCompatActivity {
    private DatabaseReference mDatabase;
    private VideoView videoView;
    private MediaController mp;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        setContentView(R.layout.activity_hologram_projector);
        videoView = (VideoView)findViewById(R.id.videoView);

        mDatabase = FirebaseDatabase.getInstance().getReference("url");
        mDatabase.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                String url= (String) dataSnapshot.getValue();
                Toast.makeText(getApplicationContext(),url, Toast.LENGTH_SHORT).show();
                if (videoView.isPlaying()){
                    Toast.makeText(getApplicationContext(),"Playing already", Toast.LENGTH_SHORT).show();
                    videoView.stopPlayback();
                    mp.removeAllViews();
                }
                else{
                    Toast.makeText(getApplicationContext(),"WTF?", Toast.LENGTH_SHORT).show();

                }
                mp=new MediaController(getApplicationContext());
                videoView.setVideoURI(Uri.parse("android.resource://"+getPackageName()+"/raw/kid"));
                videoView.setMediaController(mp);
//                videoView.requestFocus();
                videoView.start();
                

            }

            @Override
            public void onCancelled(DatabaseError databaseError) {

            }
        });
    }


}
