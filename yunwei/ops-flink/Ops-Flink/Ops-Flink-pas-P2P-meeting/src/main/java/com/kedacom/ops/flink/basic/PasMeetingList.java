package com.kedacom.ops.flink.basic;

import com.alibaba.fastjson.JSON;

import java.util.ArrayList;
import java.util.List;

public class PasMeetingList {
    private List<Pas> paslist=new ArrayList<Pas>();

    public int getMeetingCount(){
        int totalcount=0;
        for(Pas p:paslist){
            totalcount+=p.getLength();
        }
        return totalcount;
    }
    public void setPaslist(List<Pas> paslist) {
        this.paslist = paslist;
    }
    public List<Pas> getPaslist(){
        return paslist;
    }
    public int getLength(){
        return paslist.size();
    }
    public int getMeetingLength(String dev_moid){
        int index=getPas(dev_moid);
        int meetingcount=paslist.get(index).getLength();
        return meetingcount;
    }
    public int getPas(String dev_moid){
        for(Pas p:paslist){
            if(p.getDevMoid().equals(dev_moid))
                return paslist.indexOf(p);
        }
        Pas p=new Pas();
        p.setDevMoid(dev_moid);
        paslist.add(p);
        return paslist.indexOf(p);
    }
    public boolean addPas(String dev_moid){
        for(Pas p:paslist){
            if(p.getDevMoid().equals(dev_moid))
                return false;
        }
        Pas p=new Pas();
        p.setDevMoid(dev_moid);
        paslist.add(p);
        return true;
    }
    public boolean deletePas(String dev_moid){
        for(Pas p:paslist){
            if(p.getDevMoid().equals(dev_moid)){
                paslist.remove(p);
                return true;
            }
        }
        return false;
    }
    public void addMeeting(String dev_moid, Long createtime, String caller, String callee){
        int index=getPas(dev_moid);
        Pas p=paslist.get(index);
        PasMeeting pasmeeting=new PasMeeting(caller,callee,createtime);
        //System.out.println("before add: "+JSON.toJSONString(paslist));
        p.addMeeting(pasmeeting);
        //System.out.println("after add: "+JSON.toJSONString(paslist));
        paslist.set(index,p);
    }
    public boolean destroyMeeting(String dev_moid, String caller, String callee){
        int index=getPas(dev_moid);
        Pas p=paslist.get(index);
        PasMeeting meeting=new PasMeeting(caller, callee, 0L);
        //System.out.println("before destroy: "+JSON.toJSONString(paslist));
        if(p.removeMeeting(meeting)) {
            //System.out.println("after destroy:  " + JSON.toJSONString(paslist));
            return true;
        }
        else
            return false;
    }
    public static void main(String[] args) throws Exception {
        PasMeetingList plist=new PasMeetingList();
        Long t1=1577346371056L/1000;
        Long t2=1577346371057L/1000;
        plist.addMeeting("aaa",t1,"a","b");
        plist.addMeeting("bbb",t2,"c","d");
        System.out.println(plist.getLength());
        String jsonString = JSON.toJSONString(plist);
        System.out.println(jsonString);
    }
}
