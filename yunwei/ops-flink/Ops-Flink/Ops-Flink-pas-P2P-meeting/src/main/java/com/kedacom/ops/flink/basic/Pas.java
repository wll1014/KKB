package com.kedacom.ops.flink.basic;

import com.alibaba.fastjson.JSON;

import java.util.ArrayList;
import java.util.List;

public class Pas {
    private String dev_moid;
    private List<PasMeeting> meetings = new ArrayList<PasMeeting>();

    public int getLength(){
        return meetings.size();
    }

    public void setDevMoid(String dev_moid){
        this.dev_moid=dev_moid;
    }
    public void addMeeting(PasMeeting meeting){
        meetings.add(meeting);
    }
    public void setMeetings(List<PasMeeting> meetings){
        this.meetings=meetings;
    }
    public List<PasMeeting> getMeetings(){
        return meetings;
    }
    public boolean deleteMeeting(){
        return true;
    }
    public String getDevMoid(){
        return this.dev_moid;
    }
    public boolean removeMeeting(PasMeeting meeting){
        for (PasMeeting pm:meetings) {
            if(pm.equals(meeting)) {
                System.out.println("delete meeting successfully:    "+JSON.toJSONString(pm));
                meetings.remove(pm);
                return true;
            }
        }
        System.out.println("no meeting to delete:   "+ JSON.toJSONString(meeting));
        return false;
    }
}
