-- get_conf_mts_info.lua

local conf_id = ARGV[1]
local mts_info = {}

local conf_mts = redis.call("SMEMBERS", string.format("conf/%s/mts", conf_id))
if redis.call("EXISTS", string.format("conf/%s", conf_id)) == 1 then
    local userdomainmoid = redis.call("HGET", string.format("conf/%s", conf_id), "moid")
    local userdomainname = redis.call("HGET", string.format("css/domain/%s/info", userdomainmoid), "domainname")
    for i, mt_num in ipairs(conf_mts) do
        if redis.call("EXISTS", string.format("conf/%s/mt/%s", conf_id, mt_num)) == 1 then
            local is_online = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "online")
            if is_online == '1' then
                local mt_info = {}
                local e164 = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "e164")
                local mtalias = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "mtalias")
                local mtip = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "mtip")
                local mttype = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "mttype")
                local bitrate = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "bitrate")
                local protocol = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "protocol")
                local productid = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "productid")
                table.insert(mt_info, 'e164')
                table.insert(mt_info, e164)
                table.insert(mt_info, 'user_domain_name')
                table.insert(mt_info, userdomainname)
                table.insert(mt_info, 'user_domain_moid')
                table.insert(mt_info, userdomainmoid)
                table.insert(mt_info, 'name')
                table.insert(mt_info, mtalias)
                table.insert(mt_info, 'mtip')
                table.insert(mt_info, mtip)
                table.insert(mt_info, 'mttype')
                table.insert(mt_info, mttype)
                table.insert(mt_info, 'bitrate')
                table.insert(mt_info, bitrate)
                table.insert(mt_info, 'protocol')
                table.insert(mt_info, protocol)
                table.insert(mt_info, 'productid')
                table.insert(mt_info, productid)
                table.insert(mts_info, mt_info)
            end
        end
    end
end
return mts_info
