--
-- Created by IntelliJ IDEA.
-- User: wanglei_sxcpx@kedacom.com
-- Date: 2020/2/18
-- Time: 16:02

-- query real_conf mt status(
-- 静音 silence 哑音 mute 双流 dual 混音 mix 轮询 poll 电视墙 tvwall 合成 vmp
-- 自主多画面 mtvmp 选看 select 是否在上传	upload 录像	rec 是否多流终端 multistream
-- ) from redis
--


local conf_id = ARGV[1]
local mt_id = ARGV[2]

local status_items = {"silence", "mute", "dual", "mix", "poll", "tvwall", "vmp", "mtvmp", "select", "upload", "rec", "multistream"}

local status_result = {}

if redis.call("EXISTS", string.format("conf/%s", conf_id)) == 1 then
    local conf_mts = redis.call("SMEMBERS", string.format("conf/%s/mts", conf_id))
    for i, mt_num in ipairs(conf_mts) do
        if redis.call("EXISTS", string.format("conf/%s/mt/%s", conf_id, mt_num)) == 1 then
            local e164 = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "e164")
            if e164 == mt_id then
                for i, status_item in ipairs(status_items) do
                    local status = redis.call("HGET", string.format("conf/%s/mt/%s", conf_id, mt_num), status_item)
                    table.insert(status_result, status_item)
                    table.insert(status_result, status)
                end
            end
        end
    end
end

return status_result
