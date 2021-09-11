const express = require('express');
const path = require('path');
const fs = require('fs');
const { v4 } = require('uuid');
const { spawn } = require('child_process');

const app = express();

app.use(express.static(__dirname+'/public'));

let uidmap = {};
battlehandler = spawn('python3', ['on_disk_organism.py']);
battlehandler.stdout.on('data',function(data){
  console.log(data.toString());
})

app.post("/newbattle",function(req,res){
  fs.readFile(__dirname+"/public/dump/zhewarudo.json",function(err,jsonString){
    if(err){
      console.log(`File read failed at ${new Date}`);
      console.log(err);
      res.send('err');
      return
    }
    const worldDump = JSON.parse(jsonString);
    f1 = worldDump.living_filenames.splice(Math.floor(Math.random()*worldDump.living_filenames.length),1);
    f2 = worldDump.living_filenames.splice(Math.floor(Math.random()*worldDump.living_filenames.length),1);
    uid = v4();
    uidmap[uid] = {
      f1: f1,
      f2: f2,
      timeofreq: new Date()
    }
    res.send(`dump/${f1} dump/${f2} ${uid}`);
    return
  })
})

app.post("/battleresult",function(req,res){
  console.log(req.query);
  if(uidmap[req.query.uid] != null){
    console.log("processing ig");
    battleobj = uidmap[req.query.uid]
    cmd = `${battleobj.f1} ${battleobj.f2} ${req.query.winner} 2\r\n`;
    console.log(cmd);
    battlehandler.stdin.write(cmd);
  }
  else{
    console.log("not processing ig");
  }
  res.send("j");
  return;
})

app.listen(7989);
