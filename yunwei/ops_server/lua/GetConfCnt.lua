--local cjson=require("cjson")

local room_id = KEYS[1]
local conf_cap = KEYS[2]
local mt_cnt = tonumber(KEYS[3])
--local mw_type=KEYS[4]
--redis.log(redis.LOG_WARNING, "room_id:"..room_id.." conf_cap:"..conf_cap.." mt_cnt:"..mt_cnt.." mw_type:"..mw_type)

local all_rack = redis.call("smembers", "media/Racks")

--- mps算法 入参类型：table
local function get_mps_left_conf_cnt(json_content, idle_val)
    --	redis.log(redis.LOG_WARNING,"json_content type:"..type(json_content).." idle_val type-->"..type(idle_val))
    --	redis.log(redis.LOG_WARNING,"input param:"..idle_val.." string type:"..type(conf_cap).."-->"..conf_cap.." type:"..type(mt_cnt).."-->"..mt_cnt)
    local subval = 0

    for mps_idx = 1, #json_content, 1 do
        local subcap = json_content[mps_idx]["Res"]
        local submtcnt = json_content[mps_idx]["MtCnt"]
        if subcap == conf_cap and submtcnt == mt_cnt then
            subval = tonumber(json_content[mps_idx]["Value"])
            --			redis.log(redis.LOG_WARNING,"MPS match mwinfo:"..subcap.." "..submtcnt.." type:"..type(subval).."-->"..subval)
            break;
        end
    end

    if subval == 0 then
        return 0
    end

    local ret_v = idle_val / subval
    redis.log(redis.LOG_WARNING, "MPS idleval:" .. idle_val .. " subval:" .. subval .. "ret val:" .. ret_v)
    return ret_v
end

--- jd1w 算法
local function get_jd_left_conf_cnt(json_content)
    local vmp_info = json_content["Vmp"]
    local mixer_info = json_content["Mix"]

    local vmp_idle_cnt = 0
    for vmp_idx = 1, #vmp_info, 1 do
        vmp_idle_cnt = vmp_idle_cnt + vmp_info[vmp_idx]["Free"]
    end

    local mix_idle_cnt = 0
    for mix_idx = 1, #mixer_info, 1 do
        if mt_cnt == 8 and mixer_info[mix_idx]["Res"] == "Small" then
            mix_idle_cnt = mix_idle_cnt + mixer_info[mix_idx]["Free"]
        elseif mt_cnt == 192 and mixer_info[mix_idx]["Res"] == "Big" then
            mix_idle_cnt = mix_idle_cnt + mixer_info[mix_idx]["Free"]
        end
    end
    redis.log(redis.LOG_WARNING, "JD idle vmp cnt:" .. vmp_idle_cnt .. " mixer cnt:" .. mix_idle_cnt)
    if vmp_idle_cnt > mix_idle_cnt then
        return mix_idle_cnt
    else
        return vmp_idle_cnt
    end
end

------ 8ka算法
local function get_8ka_left_conf_cnt(json_content)
    local vmp_info = json_content["Vmp"]
    local mixer_info = json_content["Mix"]

    local vmp_idle_cnt = 0
    for vmp_idx = 1, #vmp_info, 1 do
        if vmp_info[vmp_idx]["MediaType"] == "H264" then
            vmp_idle_cnt = vmp_idle_cnt + vmp_info[vmp_idx]["Free"]
        end
    end

    local mix_idle_cnt = 0
    for mix_idx = 1, #mixer_info, 1 do
        if mixer_info[mix_idx]["Res"] == "Big" then
            mix_idle_cnt = mix_idle_cnt + mixer_info[mix_idx]["Free"]
        end
    end
    redis.log(redis.LOG_WARNING, "8KA idle vmp cnt:" .. vmp_idle_cnt .. " mixer cnt:" .. mix_idle_cnt)
    if vmp_idle_cnt > mix_idle_cnt then
        return mix_idle_cnt
    else
        return vmp_idle_cnt
    end
end

--- -主函数
local ret_total_conf_cnt = 0
local content_string = {}
local content_table = {}
local supp_conf_type = {}
for idx, rack_id in pairs(all_rack) do
    redis.log(redis.LOG_WARNING, "rack[" .. idx .. "]: " .. rack_id)
    local rack_key = "media/Rack/" .. rack_id

    local add_cnt = 0
    local rack_room_id = redis.call("hget", rack_key, "RoomId")
    if rack_room_id ~= nil and rack_room_id ~= false then
        redis.log(redis.LOG_WARNING, "rack_room_id type:" .. type(rack_room_id) .. "-->")
        local rack_type = redis.call("hget", rack_key, "RackType")
        if rack_room_id == room_id then
            redis.log(redis.LOG_WARNING, "rack_type type:" .. type(rack_type) .. "-->" .. rack_type)
            --		if rack_type == mw_type then
            if rack_type == "MPS" then
                content_string = redis.call("hget", rack_key, "Confcapvalue")
                supp_conf_type = redis.call("hget", rack_key, "Conftype")
                redis.log(redis.LOG_WARNING, "[GetConfCnt.lua]MPS Conftype type:" .. type(supp_conf_type) .. "-->" .. supp_conf_type)
                if supp_conf_type == "ALL" or supp_conf_type == "Tradi" then
                    local idle_val = redis.call("hget", rack_key, "Value")
                    content_table = cjson.decode(content_string)
                    add_cnt = get_mps_left_conf_cnt(content_table, tonumber(idle_val))
                end
            elseif rack_type == "JD" then
                content_string = redis.call("hget", rack_key, "ResourceInfo")
                --				redis.log(redis.LOG_WARNING,"[GetConfCnt.lua]JD content_string type:"..type(content_string).."-->"..content_string)
                content_table = cjson.decode(content_string)
                add_cnt = get_jd_left_conf_cnt(content_table)
            else
                content_string = redis.call("hget", rack_key, "ResourceInfo")
                --				redis.log(redis.LOG_WARNING,"[GetConfCnt.lua]8KA content_string type:"..type(content_string).."-->"..content_string)
                content_table = cjson.decode(content_string)
                add_cnt = get_8ka_left_conf_cnt(content_table)
            end
            --		end
        end
        redis.log(redis.LOG_WARNING, "[GetConfCnt.lua] check mw:" .. rack_key .. " rack_type:" .. rack_type .. " add_cnt:" .. add_cnt)
    end
    ret_total_conf_cnt = ret_total_conf_cnt + add_cnt
end
redis.log(redis.LOG_WARNING, "[GetConfCnt.lua]return conf cnt:" .. ret_total_conf_cnt)

return ret_total_conf_cnt
