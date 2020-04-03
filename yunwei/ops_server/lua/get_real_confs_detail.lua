-- query real_conf list from redis
-- return conf_id informations

local domain_moid = ARGV[1]
local conf_type = ARGV[2]
local conf_e164s = redis.call("SMEMBERS", "confs")
local confs_info = {}

for count, conf_e164 in ipairs(conf_e164s)
    do
    if redis.call("EXISTS", string.format("conf/%s", conf_e164)) then
        local is_domain = true
        if domain_moid ~= "" then
            local moid = redis.call("hget", string.format("conf/%s", conf_e164), "moid")
            if moid ~= domain_moid then
                is_domain = false
            end
        end
        if conf_type ~= "" then
            local conftype = redis.call("hget", string.format("conf/%s", conf_e164), "conftype")
            if conftype ~= conf_type then
                is_domain = false
            end
        end

--      filter confs out which created by testing
        local confname = redis.call("hget", string.format("conf/%s", conf_e164), "confname")
        if string.match(confname, "test_%w+_createmeeting%d+") ~= nil then
            is_domain = false
        end

        if is_domain == true then
            local conf_info = redis.call("HGETALL", string.format("conf/%s", conf_e164))

            local mt_list = {}
            local mts = redis.call("SMEMBERS", string.format("conf/%s/mts", conf_e164))
            for ii, mtid in ipairs(mts)
                do
                    local mt_id = redis.call("hget",string.format("conf/%s/mt/%s", conf_e164, mtid), "e164")
                    local mt_type = redis.call("hget",string.format("conf/%s/mt/%s", conf_e164, mtid),"mtalias")
                    table.insert(mt_list, mt_id)
                    table.insert(mt_list, mt_type)
                end
            table.insert(conf_info, "mtlist")
            table.insert(conf_info, mt_list)

            table.insert(confs_info, conf_info)
        end
    end
    end
return confs_info
