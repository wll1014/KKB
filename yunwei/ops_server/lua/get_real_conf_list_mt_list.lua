-- use room_moid query real_conf list and mt info of every conf from redis

local room_moid = ARGV[1]
local conf_e164s = redis.call("SMEMBERS", "confs")
local confs_info = {}
for count, conf_e164 in ipairs(conf_e164s) do
    if redis.call("EXISTS", string.format("confex/%s", conf_e164)) then
        local is_domain = true
        local confroommoid = redis.call("hget", string.format("confex/%s", conf_e164), "confroommoid")
        local realstarttime = redis.call("hget", string.format("confex/%s", conf_e164), "realstarttime")
        if room_moid ~= "" then
            if confroommoid ~= room_moid then
                is_domain = false
            end
        end

        if is_domain == true then
            if redis.call("EXISTS", string.format("conf/%s", conf_e164)) == 1 then
                local conf_mts = redis.call("SMEMBERS", string.format("conf/%s/mts", conf_e164))
                local mt_count = #conf_mts
                local mts_info = {}
                for i, mt_num in ipairs(conf_mts) do
                    if redis.call("EXISTS", string.format("conf/%s/mt/%s", conf_e164, mt_num)) == 1 then
                        local is_online = redis.call("HGET",string.format("conf/%s/mt/%s", conf_e164, mt_num), "online")
                        if is_online == '1' then
                            local mt_info = redis.call("HGETALL",string.format("conf/%s/mt/%s", conf_e164, mt_num))
                            table.insert(mts_info, mt_info)
                        end
                    end
                end
                local conf_info = {}
                local userdomainmoid = redis.call("HGET", string.format("confex/%s", conf_e164), "moid")
                local confname = redis.call("HGET", string.format("confex/%s", conf_e164), "name")
                local creatorname = redis.call("HGET", string.format("confex/%s", conf_e164), "creatorname")
                local userdomainname = redis.call("HGET", string.format("css/domain/%s/info", userdomainmoid), "domainname")
                table.insert(conf_info, 'e164')
                table.insert(conf_info, conf_e164)
                table.insert(conf_info, 'name')
                table.insert(conf_info, confname)
                table.insert(conf_info, 'creatorname')
                table.insert(conf_info, creatorname)
                table.insert(conf_info, 'machine_room_moid')
                table.insert(conf_info, confroommoid)
                table.insert(conf_info, 'user_domain_moid')
                table.insert(conf_info, userdomainmoid)
                table.insert(conf_info, 'user_domain_name')
                table.insert(conf_info, userdomainname)
                table.insert(conf_info, 'mt_count')
                table.insert(conf_info, mt_count)
                table.insert(conf_info, 'real_start_time')
                table.insert(conf_info, realstarttime)
                table.insert(conf_info, 'mts')
                table.insert(conf_info, mts_info)
                table.insert(confs_info, conf_info)
            end
        end
    end
end
return confs_info
