-- query real_conf mt channel information from redis
-- return mt informations

local conf_id = ARGV[1]
local start_time = ARGV[2]
local mt_id = ARGV[3]

local channel = {}
local media_types = {"vsendchns", "vrcvchns", "dsendchns", "drcvchns", "asendchns", "arcvchns"}
local media_path = {"vsendchn", "vrcvchn", "dsendchn", "drcvchn", "asendchn", "arcvchn"}

if redis.call("EXISTS", string.format("conf/%s", conf_id)) == 1 then
    local st = redis.call("HGET", string.format("conf/%s", conf_id), "starttime")
    if st ~= start_time then
        return channel
    end

    local conf_mts = redis.call("SMEMBERS", string.format("conf/%s/mts", conf_id))
    for i, mt_num in ipairs(conf_mts) do
        if redis.call("EXISTS", string.format("conf/%s/mt/%s", conf_id, mt_num)) == 1 then
            local e164 = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "e164")
            if e164 == mt_id then
                -- channel information
                -- vsend
                for medai_count, media_type in ipairs(media_types) do
                    local media_info = {}
                    if redis.call("EXISTS", string.format("conf/%s/mt/%s/%s", conf_id, mt_num, media_type)) == 1 then
                        local channel_id = redis.call("SMEMBERS", string.format("conf/%s/mt/%s/%s", conf_id, mt_num, media_type))[1]
                            if redis.call("EXISTS", string.format("conf/%s/mt/%s/%s/%s", conf_id, mt_num, media_path[medai_count], channel_id)) == 1 then
                                if (media_type == "asendchns" or media_type == "arcvchns") then
                                    local audiotype = redis.call("HGET",string.format("conf/%s/mt/%s/%s/%s", conf_id, mt_num, media_path[medai_count], channel_id), "audiotype")
                                    table.insert(media_info, "")           -- bitrate
                                    table.insert(media_info, audiotype)    -- format
                                else
                                    local rate = redis.call("HGET",string.format("conf/%s/mt/%s/%s/%s", conf_id, mt_num, media_path[medai_count], channel_id), "rate")
                                    local mediares = redis.call("HGET",string.format("conf/%s/mt/%s/%s/%s", conf_id, mt_num, media_path[medai_count], channel_id), "mediares")
                                    local mediatype = redis.call("HGET",string.format("conf/%s/mt/%s/%s/%s", conf_id, mt_num, media_path[medai_count], channel_id), "mediatype")
                                    if mediatype ~= "255" then
                                        table.insert(media_info, rate)    -- bitrate
                                        table.insert(media_info, "")      -- frame
                                        table.insert(media_info, mediares)    -- res
                                        table.insert(media_info, mediatype)    -- format
                                    end
                                end
                            end
                    end
                    table.insert(channel, media_info)
                end
                return channel
            end
        end
    end
end
return channel


