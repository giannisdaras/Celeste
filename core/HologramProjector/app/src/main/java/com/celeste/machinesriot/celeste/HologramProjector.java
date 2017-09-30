package com.celeste.machinesriot.celeste;

import android.content.Intent;
import android.net.Uri;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.io.File;


public class HologramProjector extends AppCompatActivity {
    private DatabaseReference mDatabase;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_hologram_projector);
        mDatabase = FirebaseDatabase.getInstance().getReference("url");
        mDatabase.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                String url= (String) dataSnapshot.getValue();
                Toast.makeText(getApplicationContext(),url, Toast.LENGTH_SHORT).show();
                
            }

            @Override
            public void onCancelled(DatabaseError databaseError) {

            }
        });
    }
}
