from enum import IntEnum, unique


@unique
class ConfMtAddTypeNMS(IntEnum):
    """
    会议终端入会类型网管
    """

    @classmethod
    def get(cls, key):
        try:
            return cls(key)
        except Exception:
            return cls(255)

    NONE = 0  # 不接收也不发送
    SSMMCU = 2  # 简单下级级联会议
    MT = 3  # 普通终端
    MMMCU = 4  # 上级级联会议
    CSMMCU = 5  # 复杂下级级联会议
    PHONE = 6  # 电话终端
    SATD = 7  # 卫星终端
    VRSREC = 8  # vrs录像机
    AUDIOMT = 9  # 音频终端
    IPC = 21  # IPC监控前端
    Other = 255  # other:  only used for ops


ConfMtAddDesc = {
    "NONE": "NONE",
    "SSMMCU": "简单下级级联会议",
    "MT": "普通终端",
    "MMMCU": "上级级联会议",
    "CSMMCU": "复杂下级级联会议",
    "PHONE": "电话终端",
    "SATD": "卫星终端",
    "VRSREC": "vrs录像机",
    "AUDIOMT": "音频终端",
    "IPC": "IPC监控前端",
    "Other": "其它"
}


@unique
class ConfMtAddTypeRedis(IntEnum):
    """
    Redis会议终端入会类型
    """

    @classmethod
    def get(cls, key):
        try:
            return cls(key)
        except Exception:
            return cls(255)

    NONE = 0
    MT = 1
    PHONE = 3
    SATD = 5
    CSMMCU = 7
    MMMCU = 8
    SSMMCU = 9
    VRSREC = 10
    IPC = 21
    Other = 255


Redis2NMS = {
    0: 0,
    1: 3,
    7: 5,
    9: 2,
    8: 4,
    5: 7,
    3: 6,
    10: 8,
    21: 21,
    255: 255
}


def ConvertRedisTypeToNMS(redis_type):
    """
    将redis上终端入会类型转为网管入会类型
    :param redis_type:
    :return:
    """
    return Redis2NMS.get(redis_type, 0)


class MtProtocol(IntEnum):
    """
    redis 终端注册协议类型
    """

    @classmethod
    def get(cls, key):
        try:
            return cls(key)
        except Exception:
            return cls(255)

    H323 = 0
    SIP = 1
    Other = 255


class MtProtocolType(IntEnum):
    """
    终端协议类型 标准/非标
    """

    # @classmethod
    # def to_describe(cls, key):
    #     try:
    #         return cls(key)
    #     except Exception:
    #         return cls(255)

    NonStandard = 0  # 非标
    Standard = 1     # 标准
    Other = 255


class MtStatus(IntEnum):
    """
    终端状态
    """

    # @classmethod
    # def to_describe(cls, key):
    #     try:
    #         return cls(key)
    #     except Exception:
    #         return cls(255)

    Offline = 0     # 下线
    Online = 1      # 在线
    Meeting = 2     # 会议中
    Other = 255


class MtType(IntEnum):
    """
    终端类型
    """

    # @classmethod
    # def to_describe(cls, key):
    #     try:
    #         return cls(key)
    #     except Exception:
    #         return cls(255)

    Soft = 0        # 软终端
    Hard = 1        # 硬终端
    OtherProduct = 2     # 其它厂商
    Unknown = 255


@unique
class ConfEndTimeType(IntEnum):
    """
    会议结束时间类型
    """
    REALTIME = 0  # 实时会议
    MANUAL = 1  # 手动结束
    ABEND = 2  # 异常结束


@unique
class ConfMediaType(IntEnum):
    """
    会议资源类型
    """
    LOCAL = 0  # 本地会议
    CLOUD = 1  # 云会议


@unique
class ConfType(IntEnum):
    """
    会议类型
    """
    TRADITION = 0  # 传统会议
    PORT = 1  # 端口会议
    P2P = 2  # 点对点会议
    MULTI = 3  # 多点会议

    @classmethod
    def keys(cls):
        return [name for name, member in cls.__members__.items()]

    @classmethod
    def values(cls):
        return [member.value for name, member in cls.__members__.items()]


@unique
class ConfStat(IntEnum):
    """
    会议状态
    """
    HISTORY = 0  # 历史会议
    REALTIME = 1  # 实时会议

    @classmethod
    def keys(cls):
        return [name for name, member in cls.__members__.items()]

    @classmethod
    def values(cls):
        return [member.value for name, member in cls.__members__.items()]


class ConfVideoFormat(IntEnum):
    """
    会议视频格式
    """

    @classmethod
    def get(cls, key):
        try:
            return cls(key)
        except Exception:
            return cls(255)

    H264 = 106
    H265 = 108
    Other = 255


@classmethod
def get(cls, key):
    try:
        return cls(key)
    except Exception:
        return cls(255)


# 视频分辨率格式
ConfVideoResolution = {
    'CIF': 3,
    '4CIF': 5,
    'WCIF': 15,
    '4K': 62,
    'W4CIF': 31,
    'HD720': 32,
    'HD1080': 35,
    'Other': 255,
    'get': get
}
ConfVideoResolutionType = IntEnum('ConfVideoResolutionType', ConfVideoResolution)


class ConfEncryptionType(IntEnum):
    """
    会议加密类型
    """

    @classmethod
    def get(cls, key):
        try:
            return cls(key)
        except Exception:
            return cls(255)

    NONE = 0
    DES = 1
    AES = 2
    SM4 = 3
    SM1 = 4
    Other = 255


class MtVideoFormatNMS(IntEnum):
    """
    终端视频格式 网管上报数据
    """

    @classmethod
    def get(cls, key):
        try:
            return cls(key)
        except Exception:
            return cls(255)

    H261 = 0
    H262 = 1
    H263 = 2
    H263plus = 3
    H264 = 4
    MPEG4 = 5
    H265 = 6
    Other = 255


class MtVideoFormatRedis(IntEnum):
    """
    终端视频格式 Redis上报数据
    """

    @classmethod
    def get(cls, key):
        try:
            return cls(key)
        except Exception:
            return cls(255)

    H261 = 31
    H262 = 33
    H263 = 34
    MP4 = 97
    H263plus = 101
    H264ForHuaWei = 105
    H264 = 106
    FEC = 107
    H265 = 108
    Other = 255


class MtAudioFormatNMS(IntEnum):
    """
    终端音频格式 网管上报数据
    """

    @classmethod
    def get(cls, key):
        try:
            return cls(key)
        except Exception:
            return cls(255)

    G711a = 0
    G711u = 1
    G722 = 2
    G7231 = 3
    G728 = 4
    G729 = 5
    MP3 = 6
    G721 = 7
    G7221 = 8
    G719 = 9
    MpegAACLC = 10
    MpegAACLD = 11
    Opus = 12
    Other = 255


# 终端音频格式 Redis上报数据
MtAudioFormatRedis = {
    0: 'G711u',
    2: "G721",
    4: "G7231",
    5: "DVI4 ADPCM",
    8: "G711a",
    9: "G722",
    13: "G7221",
    15: "G728",
    18: "G729",
    96: "MP3",
    98: "G7221C",
    99: "G719",
    102: "AACLC",
    103: "AACLD",
    104: "ISAC_32",
    120: "OPUS",
    127: "OPUS"
}


class MtVideoResolutionTypeNMS(IntEnum):
    """
    终端分辨率格式
    """

    @classmethod
    def get(cls, key):
        try:
            return cls(key)
        except Exception:
            return cls(255)

    MtResAuto = 0  # 自适应
    MtSQCIF = 1  # SQCIF 128x96
    MtQCIF = 2  # QCIF 176x144
    MtCIF = 3  # CIF 352x288
    Mt2CIF = 4  # 2CIF 352x576
    Mt4CIF = 5  # 4CIF 704x576
    Mt16CIF = 6  # 16CIF 1408x1152
    MtVGA352x240 = 7  # 352x240 对应平台SIF
    Mt2SIF = 8  # 对应平台2SIF，具体不知道多少 * 多少
    MtVGA704x480 = 9  # 704x480 对应平台4SIF
    MtVGA640x480 = 10  # VGA 640x480
    MtVGA800x600 = 11  # SVGA 800x600
    MtVGA1024x768 = 12  # XGA 1024x768
    MtVWCIF = 13  # WCIF 512x288

    # 仅用于终端分辨率改变
    MtVSQCIF112x96 = 14  # SQCIF 112x96
    MtVSQCIF96x80 = 15  # SQCIF 96x80

    # 高清分辨率
    MtVW4CIF = 16  # Wide4CIF 1024x576
    MtHD720p1280x720 = 17  # 720p 1280x720
    MtVGA1280x1024 = 18  # SXGA 1280x1024
    MtVGA1600x1200 = 19  # UXGA 1600x1200
    MtHD1080i1920x1080 = 20  # 1080i 1920x1080
    MtHD1080p1920x1080 = 21  # 1080p 1920x1080
    MtVGA1280x800 = 22  # WXGA 1280x800
    MtVGA1440x900 = 23  # WSXGA 1440x900
    MtVGA1280x960 = 24  # XVGA 1280x960

    # 非标分辨率（1080p底图）用于终端分辨率改变
    MtV1440x816 = 25  # 1440×816(3/4)
    Mt1280x720 = 26  # 1280×720(2/3)
    MtV960x544 = 27  # 960×544(1/2)
    MtV640x368 = 28  # 640×368(1/3)
    MtV480x272 = 29  # 480×272(1/4)
    Mt384x272 = 30  # 384×272(1/5)
    Mt640x544 = 31  # 640x544
    Mt320x272 = 32  # 320x272

    # 非标分辨率（720p底图） 用于终端分辨率改变
    Mt_720_960x544 = 33  # 960×544(3/4)
    Mt_720_864x480 = 34  # 864×480(2/3)
    Mt_720_640x368 = 35  # 640×368(1/2)
    Mt_720_432x240 = 36  # 432×240(1/3)
    Mt_720_320x192 = 37  # 320×192(1/4)

    # 非标分辨率
    MtVGA480x352 = 38  # 480×352,iPad专用
    MtHD480i720x480 = 39  # 480i 720x480
    MtHD480p720x480 = 40  # 480p 720x480
    MtHD576i720x576 = 41  # 576i 720x576
    MtHD576p720x576 = 42  # 576p 720x576
    MtVGA1280x768 = 43  # WXGA 1280x768
    MtVGA1366x768 = 44  # WXGA 1366x768
    MtVGA1280x854 = 45  # WSXGA 1280x854
    MtVGA1680x1050 = 46  # WSXGA 1680x1050
    MtVGA1920x1200 = 47  # WUXGA 1920x1200
    MtV3840x2160 = 48  # 4Kx2K 3840x2160
    Mt1280x600 = 49  # 1280x600
    Mt1360x768 = 50  # 1360x768
    MtVRes3840x2160 = 51  # 3840x2160
    MtVRes4096x2048 = 52  # 4096x2048
    MtVRes4096x2160 = 53  # 4096x2160
    MtVRes4096x2304 = 54  # 4096x2304
    MtVResEnd = 100
    Other = 255


MtVideoResolutionNMSDesc = {
    "MtResAuto": "自适应",
    "MtSQCIF": "SQCIF",
    "MtQCIF": "QCIF",
    "MtCIF": "CIF",
    "Mt2CIF": "2CIF",
    "Mt4CIF": "4CIF",
    "Mt16CIF": "16CIF",
    "MtVGA352x240": "VGA",
    "Mt2SIF": "2SIF",
    "MtVGA704x480": "VGA",
    "MtVGA640x480": "VGA",
    "MtVGA800x600": "SVGA",
    "MtVGA1024x768": "XGA",
    "MtVWCIF": "WCIF",

    "MtVSQCIF112x96": "SQCIF",
    "MtVSQCIF96x80": "SQCIF",

    "MtVW4CIF": "W4CIF",
    "MtHD720p1280x720": "720p",
    "MtVGA1280x1024": "SXGA",
    "MtVGA1600x1200": "UXGA",
    "MtHD1080i1920x1080": "1080i",
    "MtHD1080p1920x1080": "1080p",
    "MtVGA1280x800": "WXGA",
    "MtVGA1440x900": "WSXGA",
    "MtVGA1280x960": "XVGA",

    "MtV1440x816": "1440×816(3/4)",
    "Mt1280x720": "1280×720(2/3)",
    "MtV960x544": "960×544(1/2)",
    "MtV640x368": "640×368(1/3)",
    "MtV480x272": "480×272(1/4)",
    "Mt384x272": "384×272(1/5)",
    "Mt640x544": "640x544",
    "Mt320x272": "320x272",

    "Mt_720_960x544": "960×544(3/4)",
    "Mt_720_864x480": "864×480(2/3)",
    "Mt_720_640x368": "640×368(1/2)",
    "Mt_720_432x240": "432×240(1/3)",
    "Mt_720_320x192": "320×192(1/4)",

    "MtVGA480x352": "480x352",
    "MtHD480i720x480": "480i",
    "MtHD480p720x480": "480p",
    "MtHD576i720x576": "576i",
    "MtHD576p720x576": "576p",
    "MtVGA1280x768": "WXGA",
    "MtVGA1366x768": "WXGA",
    "MtVGA1280x854": "WSXGA",
    "MtVGA1680x1050": "WSXGA+",
    "MtVGA1920x1200": "WUXGA",
    "MtV3840x2160": "4K",
    "Mt1280x600": "1280x600",
    "Mt1360x768": "1360x768",
    "MtVRes3840x2160": "3840x2160",
    "MtVRes4096x2048": "4096x2048",
    "MtVRes4096x2160": "4096x2160",
    "MtVRes4096x2304": "4096x2304",
    "MtVResEnd": "",
    "Other": "Other"
}

MtVideoResolutionRedisDesc = {
    1: "SQCIF",
    2: "QCIF",
    3: "CIF",
    4: "2CIF",
    5: "4CIF",
    6: "16CIF",
    7: "自适应",
    8: "SIF",
    9: "2SIF",
    10: "4SIF",
    11: "VGA",
    12: "SVGA",
    13: "XGA",
    14: "WXGA",
    15: "WCIF",
    21: "SQCIF_112x96",
    22: "SQCIF_96x80",
    31: "W4CIF",
    32: "HD720",
    33: "SXGA",
    34: "UXGA",
    35: "HD1080",
    37: "WSXGA",
    38: "XVGA",
    39: "WSXGA_P",

    41: "1440×816(3/4)",
    42: "1280×720(2/3)",
    43: "960×544(1/2)",
    44: "640×368(1/3)",
    45: "480×272(1/4)",
    46: "384×272(1/5)",

    51: "960×544(3/4)",
    52: "864×480(2/3)",
    53: "640×368(1/2)",
    54: "432×240(1/3)",
    55: "320×192(1/4)",

    56: "480x352",
    57: "320x272",
    58: "640x480",

    61: "480x352",
    62: "4K",
    63: "1536×864",
    64: "1536×1080",
    65: "2304×1296",
    66: "2560×1440",
    67: "2880×1620"
}


@unique
class ConfMTMediaInfo(IntEnum):
    Mt_bond_in = 1  # 网口带宽  接收
    Mt_bond_out = 2  # 网口带宽  发送

    MtMedianet_recv_privideo_loss_rate = 3  # 终端_主视频_丢包率  接收
    MtMedianet_recv_assvideo_loss_rate = 4  # 终端_辅视频_丢包率  接收

    MtMedianet_recv_video_rebuffer = 5  # 终端_主视频_卡顿次数  接收
    MtMedianet_recv_dualvideo_rebuffer = 6  # 终端_辅视频_卡顿次数  接收

    MtMedianet_recv_video_rtt = 7  # 终端_主视频_时延  接收
    MtMedianet_recv_dualvideo_rtt = 8  # 终端_辅视频_时延  接收

    MtMedianet_recv_video_shake = 9  # 终端_主视频_抖动  接收
    MtMedianet_recv_dualvideo_shake = 10  # 终端_辅视频_抖动  接收

    MtMedia_recv_privideo_bitrate = 11  # 终端_主视频_码率  接收
    MtMedia_recv_assvideo_bitrate = 12  # 终端_辅视频_码率  接收
    MtMedia_recv_audio_bitrate = 95  # 终端_音频_码率  接收

    MtMedia_recv_privideo_framerate = 13  # 终端_主视频_帧率  接收
    MtMedia_recv_assvideo_framerate = 14  # 终端_辅视频_帧率  接收
    MtMedia_recv_audio_framerate = 99  # 终端_音频_帧率  接收

    MtMedia_recv_video_medianet_lost = 15  # 终端_主视频_网络丢帧  接收
    MtMedia_recv_dualvideo_medianet_lost = 16  # 终端_辅视频_网络丢帧  接收
    MtMedia_recv_audio_medianet_lost = 17  # 终端_音频_网络丢帧  接收

    MtMedia_recv_video_media_lost = 18  # 终端_主视频_媒体丢帧  接收
    MtMedia_recv_dualvideo_media_lost = 19  # 终端_辅视频_媒体丢帧  接收
    MtMedia_recv_audio_media_lost = 20  # 终端_音频_媒体丢帧  接收

    MtMedia_recv_video_max_size = 21  # 终端_主视频_最大帧大小  接收
    MtMedia_recv_dualvideo_max_size = 22  # 终端_辅视频_最大帧大小  接收
    MtMedia_recv_audio_max_size = 23  # 终端_音频_最大帧大小  接收

    MtMedia_recv_video_fps = 24  # 终端_主视频_关键帧频率  接收
    MtMedia_recv_dualvideo_fps = 25  # 终端_辅视频_关键帧频率  接收

    MtMedia_recv_privideo_width = 27  # 终端_主视频_宽  接收
    MtMedia_recv_assvideo_width = 28  # 终端_辅视频_宽  接收
    MtMedia_recv_privideo_height = 29  # 终端_主视频_高  接收
    MtMedia_recv_assvideo_height = 30  # 终端_辅视频_高  接收

    MtMedia_recv_video_last_error = 31  # 终端_主视频_媒体错误  接收
    MtMedia_recv_dualvideo_last_error = 32  # 终端_辅视频_媒体错误  接收
    MtMedia_recv_audio_last_error = 33  # 终端_音频_媒体错误  接收

    MtMedia_recv_video_total_frames = 81  # 终端_主视频_帧总数  接收
    MtMedia_recv_dualvideo_total_frames = 82  # 终端_辅视频_帧总数  接收
    MtMedia_recv_audio_total_frames = 83  # 终端_音频_帧总数  接收

    # MtMedianet_send_privideo_loss_rate = 87  # 终端_主视频_丢包率  发送
    # MtMedianet_send_assvideo_loss_rate = 88  # 终端_辅视频_丢包率  发送
    #
    # MtMedianet_send_video_rebuffer = 89  # 终端_主视频_卡顿次数  发送
    # MtMedianet_send_dualvideo_rebuffer = 90  # 终端_辅视频_卡顿次数  发送
    #
    # MtMedianet_send_video_rtt = 91  # 终端_主视频_时延  发送
    # MtMedianet_send_dualvideo_rtt = 92  # 终端_辅视频_时延  发送
    #
    # MtMedianet_send_video_shake = 93  # 终端_主视频_抖动  发送
    # MtMedianet_send_dualvideo_shake = 94  # 终端_辅视频_抖动  发送

    MtMedia_send_privideo_bitrate = 96  # 终端_主视频_码率  发送
    MtMedia_send_assvideo_bitrate = 97  # 终端_辅视频_码率  发送
    MtMedia_send_audio_bitrate = 98  # 终端_音频_码率  发送

    MtMedia_send_privideo_framerate = 100  # 终端_主视频_帧率  发送
    MtMedia_send_assvideo_framerate = 101  # 终端_辅视频_帧率  发送
    MtMedia_send_audio_framerate = 102  # 终端_音频_帧率  发送

    MtMedia_send_video_medianet_lost = 103  # 终端_主视频_网络丢帧  发送
    MtMedia_send_dualvideo_medianet_lost = 104  # 终端_辅视频_网络丢帧  发送
    MtMedia_send_audio_medianet_lost = 105  # 终端_音频_网络丢帧  发送

    MtMedia_send_video_media_lost = 106  # 终端_主视频_媒体丢帧  发送
    MtMedia_send_dualvideo_media_lost = 107  # 终端_辅视频_媒体丢帧  发送
    MtMedia_send_audio_media_lost = 108  # 终端_音频_媒体丢帧  发送

    MtMedia_send_video_max_size = 109  # 终端_主视频_最大帧大小  发送
    MtMedia_send_dualvideo_max_size = 110  # 终端_辅视频_最大帧大小  发送
    MtMedia_send_audio_max_size = 111  # 终端_音频_最大帧大小  发送

    MtMedia_send_video_fps = 112  # 终端_主视频_关键帧频率  发送
    MtMedia_send_dualvideo_fps = 113  # 终端_辅视频_关键帧频率  发送

    MtMedia_send_privideo_width = 114  # 终端_主视频_宽  发送
    MtMedia_send_assvideo_width = 115  # 终端_辅视频_宽  发送
    MtMedia_send_privideo_height = 116  # 终端_主视频_高  发送
    MtMedia_send_assvideo_height = 117  # 终端_辅视频_高  发送

    MtMedia_send_video_last_error = 118  # 终端_主视频_媒体错误  发送
    MtMedia_send_dualvideo_last_error = 119  # 终端_辅视频_媒体错误  发送
    MtMedia_send_audio_last_error = 120  # 终端_音频_媒体错误  发送

    MtMedia_send_video_total_frames = 121  # 终端_主视频_帧总数  发送
    MtMedia_send_dualvideo_total_frames = 122  # 终端_辅视频_帧总数  发送
    MtMedia_send_audio_total_frames = 123  # 终端_音频_帧总数  发送

    Dss_send_video_loss_rate = 34  # 转发_主视频_丢包率  发送
    Dss_send_dualvideo_loss_rate = 35  # 转发_辅视频_丢包率  发送
    Dss_send_audio_loss_rate = 36  # 转发_音频_丢包率    发送
    Dss_recv_video_loss_rate = 37  # 转发_主视频_丢包率  接收
    Dss_recv_dualvideo_loss_rate = 38  # 转发_辅视频_丢包率  接收
    Dss_recv_audio_loss_rate = 39  # 转发_音频_丢包率    接收

    Dss_send_video_bitrate = 40  # 转发_主视频_码率  发送
    Dss_send_dualvideo_bitrate = 41  # 转发_辅视频_码率  发送
    Dss_send_audio_bitrate = 42  # 转发_音频_码率    发送
    Dss_recv_video_bitrate = 43  # 转发_主视频_码率  接收
    Dss_recv_dualvideo_bitrate = 44  # 转发_辅视频_码率  接收
    Dss_recv_audio_bitrate = 45  # 转发_音频_码率    接收

    PlfmMedianet_recv_privideo_loss_rate = 46  # 平台媒体_主视频_丢包率  接收
    PlfmMedianet_recv_assvideo_loss_rate = 47  # 平台媒体_辅视频_丢包率  接收

    PlfmMedianet_recv_privideo_rebuffer = 48  # 平台媒体_主视频_卡顿次数  接收
    PlfmMedianet_recv_assvideo_rebuffer = 49  # 平台媒体_辅视频_卡顿次数  接收

    PlfmMedianet_recv_privideo_rtt = 50  # 平台媒体_主视频_时延   接收
    PlfmMedianet_recv_assvideo_rtt = 51  # 平台媒体_辅视频_时延   接收

    PlfmMedianet_recv_video_shake = 52  # 平台媒体_主视频_抖动  接收
    PlfmMedianet_recv_dualvideo_shake = 53  # 平台媒体_辅视频_抖动  接收

    PlfmMedia_recv_privideo_bitrate = 54  # 平台媒体_主视频_码率  接收
    PlfmMedia_recv_assvideo_bitrate = 55  # 平台媒体_辅视频_码率  接收
    PlfmMedia_recv_audio_bitrate = 56  # 平台媒体_音频_码率  接收

    PlfmMedia_recv_privideo_framerate = 57  # 平台媒体_主视频_帧率  接收
    PlfmMedia_recv_assvideo_framerate = 58  # 平台媒体_辅视频_帧率  接收
    PlfmMedia_recv_audio_framerate = 59  # 平台媒体_音频_帧率  接收

    PlfmMedia_recv_privideo_medianet_lost = 60  # 平台媒体_主视频_网络丢帧  接收
    PlfmMedia_recv_assvideo_medianet_lost = 61  # 平台媒体_辅视频_网络丢帧  接收
    PlfmMedia_recv_audio_medianet_lost = 62  # 平台媒体_音频_网络丢帧  接收

    PlfmMedia_recv_privideo_media_lost = 63  # 平台媒体_主视频_媒体丢帧  接收
    PlfmMedia_recv_assvideo_media_lost = 64  # 平台媒体_辅视频_媒体丢帧  接收
    PlfmMedia_recv_audio_media_lost = 65  # 平台媒体_音频_媒体丢帧  接收

    PlfmMedia_recv_privideo_max_size = 66  # 平台媒体_主视频_最大帧大小  接收
    PlfmMedia_recv_assvideo_max_size = 67  # 平台媒体_辅视频_最大帧大小  接收
    PlfmMedia_recv_audio_max_size = 68  # 平台媒体_音频_最大帧大小  接收

    PlfmMedia_recv_privideo_fps = 69  # 平台媒体_主视频_关键帧频率  接收
    PlfmMedia_recv_assvideo_fps = 70  # 平台媒体_辅视频_关键帧频率  接收

    PlfmMedia_recv_privideo_width = 71  # 平台媒体_主视频_宽  接收
    PlfmMedia_recv_assvideo_width = 72  # 平台媒体_辅视频_宽  接收
    PlfmMedia_recv_privideo_height = 73  # 平台媒体_主视频_高   接收
    PlfmMedia_recv_assvideo_height = 74  # 平台媒体_辅视频_高   接收

    PlfmMedia_recv_privideo_last_error = 75  # 平台媒体_主视频_媒体错误  接收
    PlfmMedia_recv_assvideo_last_error = 76  # 平台媒体_辅视频_媒体错误  接收
    PlfmMedia_recv_audio_last_error = 77  # 平台媒体_音频_媒体错误  接收

    PlfmMedia_recv_privideo_total_frames = 84  # 平台媒体_主视频_帧总数  接收
    PlfmMedia_recv_assvideo_total_frames = 85  # 平台媒体_辅视频_帧总数  接收
    PlfmMedia_recv_audio_total_frames = 86  # 平台媒体_音频_帧总数  接收

    # PlfmMedianet_send_privideo_loss_rate = 124  # 平台媒体_主视频_丢包率  发送
    # PlfmMedianet_send_assvideo_loss_rate = 125  # 平台媒体_辅视频_丢包率  发送
    #
    # PlfmMedianet_send_privideo_rebuffer = 126  # 平台媒体_主视频_卡顿次数  发送
    # PlfmMedianet_send_assvideo_rebuffer = 127  # 平台媒体_辅视频_卡顿次数  发送
    #
    # PlfmMedianet_send_privideo_rtt = 128  # 平台媒体_主视频_时延   发送
    # PlfmMedianet_send_assvideo_rtt = 129  # 平台媒体_辅视频_时延   发送
    #
    # PlfmMedianet_send_video_shake = 130  # 平台媒体_主视频_抖动  发送
    # PlfmMedianet_send_dualvideo_shake = 131  # 平台媒体_辅视频_抖动  发送

    PlfmMedia_send_privideo_bitrate = 132  # 平台媒体_主视频_码率  发送
    PlfmMedia_send_assvideo_bitrate = 133  # 平台媒体_辅视频_码率  发送
    PlfmMedia_send_audio_bitrate = 134  # 平台媒体_音频_码率  发送

    PlfmMedia_send_privideo_framerate = 135  # 平台媒体_主视频_帧率  发送
    PlfmMedia_send_assvideo_framerate = 136  # 平台媒体_辅视频_帧率  发送
    PlfmMedia_send_audio_framerate = 137  # 平台媒体_音频_帧率  发送

    PlfmMedia_send_privideo_medianet_lost = 138  # 平台媒体_主视频_网络丢帧  发送
    PlfmMedia_send_assvideo_medianet_lost = 139  # 平台媒体_辅视频_网络丢帧  发送
    PlfmMedia_send_audio_medianet_lost = 140  # 平台媒体_音频_网络丢帧  发送

    PlfmMedia_send_privideo_media_lost = 141  # 平台媒体_主视频_媒体丢帧  发送
    PlfmMedia_send_assvideo_media_lost = 142  # 平台媒体_辅视频_媒体丢帧  发送
    PlfmMedia_send_audio_media_lost = 143  # 平台媒体_音频_媒体丢帧  发送

    PlfmMedia_send_privideo_max_size = 144  # 平台媒体_主视频_最大帧大小  发送
    PlfmMedia_send_assvideo_max_size = 145  # 平台媒体_辅视频_最大帧大小  发送
    PlfmMedia_send_audio_max_size = 146  # 平台媒体_音频_最大帧大小  发送

    PlfmMedia_send_privideo_fps = 147  # 平台媒体_主视频_关键帧频率  发送
    PlfmMedia_send_assvideo_fps = 148  # 平台媒体_辅视频_关键帧频率  发送

    PlfmMedia_send_privideo_width = 149  # 平台媒体_主视频_宽  发送
    PlfmMedia_send_assvideo_width = 150  # 平台媒体_辅视频_宽  发送
    PlfmMedia_send_privideo_height = 151  # 平台媒体_主视频_高   发送
    PlfmMedia_send_assvideo_height = 152  # 平台媒体_辅视频_高   发送

    PlfmMedia_send_privideo_last_error = 78  # 平台媒体_主视频_媒体错误  发送
    PlfmMedia_send_assvideo_last_error = 79  # 平台媒体_辅视频_媒体错误  发送
    PlfmMedia_send_audio_last_error = 80  # 平台媒体_音频_媒体错误  发送

    PlfmMedia_send_privideo_total_frames = 153  # 平台媒体_主视频_帧总数  发送
    PlfmMedia_send_assvideo_total_frames = 154  # 平台媒体_辅视频_帧总数  发送
    PlfmMedia_send_audio_total_frames = 155  # 平台媒体_音频_帧总数  发送


ConfMTMediaInfoDesc = {
    1: "网口进口带宽",
    2: "网口出口带宽",
    3: "主视频(接收)",
    4: "辅视频(接收)",
    5: "主视频(接收)",
    6: "辅视频(接收)",
    7: "主视频(接收)",
    8: "辅视频(接收)",
    9: "主视频(接收)",
    10: "辅视频(接收)",
    11: "主视频(接收)",
    12: "辅视频(接收)",
    95: "音频(接收)",
    13: "主视频(接收)",
    14: "辅视频(接收)",
    99: "音频(接收)",
    15: "主视频(接收)",
    16: "辅视频(接收)",
    17: "音频(接收)",
    18: "主视频(接收)",
    19: "辅视频(接收)",
    20: "音频(接收)",
    21: "主视频(接收)",
    22: "辅视频(接收)",
    23: "音频(接收)",
    24: "主视频(接收)",
    25: "辅视频(接收)",
    27: "主视频_宽(接收)",
    28: "辅视频_宽(接收)",
    29: "主视频_高(接收)",
    30: "辅视频_高(接收)",
    31: "主视频(接收)",
    32: "辅视频(接收)",
    33: "音频(接收)",
    34: "主视频(发送)",
    35: "辅视频(发送)",
    36: "音频(发送)",
    37: "主视频(接收)",
    38: "辅视频(接收)",
    39: "音频(接收)",
    40: "主视频(发送)",
    41: "辅视频(发送)",
    42: "音频(发送)",
    43: "主视频(接收)",
    44: "辅视频(接收)",
    45: "音频(接收)",
    46: "主视频(接收)",
    47: "辅视频(接收)",
    48: "主视频(接收)",
    49: "辅视频(接收)",
    50: "主视频(接收)",
    51: "辅视频(接收)",
    52: "主视频(接收)",
    53: "辅视频(接收)",
    54: "主视频(接收)",
    55: "辅视频(接收)",
    56: "音频(接收)",
    57: "主视频(接收)",
    58: "辅视频(接收)",
    59: "音频(接收)",
    60: "主视频(接收)",
    61: "辅视频(接收)",
    62: "音频(接收)",
    63: "主视频(接收)",
    64: "辅视频(接收)",
    65: "音频(接收)",
    66: "主视频(接收)",
    67: "辅视频(接收)",
    68: "音频(接收)",
    69: "主视频(接收)",
    70: "辅视频(接收)",
    71: "主视频_宽(接收)",
    72: "辅视频_宽(接收)",
    73: "主视频_高(接收)",
    74: "辅视频_高(接收)",
    75: "主视频(接收)",
    76: "辅视频(接收)",
    77: "音频(接收)",
    78: "主视频(发送)",
    79: "辅视频(发送)",
    80: "音频(发送)",
    81: "主视频(接收)",
    82: "辅视频(接收)",
    83: "音频(接收)",
    84: "主视频(接收)",
    85: "辅视频(接收)",
    86: "音频(接收)",
    # 87: "主视频(发送)",
    # 88: "辅视频(发送)",
    # 89: "主视频(发送)",
    # 90: "辅视频(发送)",
    # 91: "主视频(发送)",
    # 92: "辅视频(发送)",
    # 93: "主视频(发送)",
    # 94: "辅视频(发送)",
    96: "主视频(发送)",
    97: "辅视频(发送)",
    98: "音频(发送)",
    100: "主视频(发送)",
    101: "辅视频(发送)",
    102: "音频(发送)",
    103: "主视频(发送)",
    104: "辅视频(发送)",
    105: "音频(发送)",
    106: "主视频(发送)",
    107: "辅视频(发送)",
    108: "音频(发送)",
    109: "主视频(发送)",
    110: "辅视频(发送)",
    111: "音频(发送)",
    112: "主视频(发送)",
    113: "辅视频(发送)",
    114: "主视频(发送)",
    115: "辅视频(发送)",
    116: "主视频(发送)",
    117: "辅视频(发送)",
    118: "主视频(发送)",
    119: "辅视频(发送)",
    120: "音频(发送)",
    121: "主视频(发送)",
    122: "辅视频(发送)",
    123: "音频(发送)",
    # 124: "主视频(发送)",
    # 125: "辅视频(发送)",
    # 126: "主视频(发送)",
    # 127: "辅视频(发送)",
    # 128: "主视频(发送)",
    # 129: "辅视频(发送)",
    # 130: "主视频(发送)",
    # 131: "辅视频(发送)",
    132: "主视频(发送)",
    133: "辅视频(发送)",
    134: "音频(发送)",
    135: "主视频(发送)",
    136: "辅视频(发送)",
    137: "音频(发送)",
    138: "主视频(发送)",
    139: "辅视频(发送)",
    140: "音频(发送)",
    141: "主视频(发送)",
    142: "辅视频(发送)",
    143: "音频(发送)",
    144: "主视频(发送)",
    145: "辅视频(发送)",
    146: "音频(发送)",
    147: "主视频(发送)",
    148: "辅视频(发送)",
    149: "主视频_宽(发送)",
    150: "辅视频_宽(发送)",
    151: "主视频_高(发送)",
    152: "辅视频_高(发送)",
    153: "主视频(发送)",
    154: "辅视频(发送)",
    155: "音频(发送)",
}

ConfDevDelReasonDesc = {
    1: "网络、接入或转发异常",
    2: "正常挂断",
    3: "RTD超时",
    4: "DRQ",
    5: "类型不匹配",
    6: "终端忙",
    7: "终端主动挂断",
    8: "终端不可达",
    9: "终端本地挂断",
    10: "终端忙",
    11: "本端行政级别低，由远端自动发起重连",
    12: "呼叫下级MCU失败，该MCU正在召开其它会议",
    13: "呼叫下级MCU失败，该MCU已经被其它高级别MCU呼叫",
    16: "电话终端未接通",
    17: "终端入会加密模式和会议不符合",
    18: "终端入会超过会议最大终端数",
    19: "终端入会超过会议最大终端数",
    20: "会议为免打扰模式",
    21: "主席挂断",
    22: "会控挂断",
    23: "级联上级会议挂断",
    24: "会议结束挂断",
    25: "无终端，自动结会-1min",
    26: "无在线终端，自动结会-5min",
    27: "在线终端仅一个，自动结会-10min",
    28: "mp掉线",
    29: "申请解码资源失败",
    30: "mtadp掉线",
    31: "mpadp侧处理超时",
    255: "未知错误"
}


# 获取终端离会原因
def getConfDevDelReason(reason):
    if reason in ConfDevDelReasonDesc.keys():
        return ConfDevDelReasonDesc.get(reason)
    else:
        return ConfDevDelReasonDesc.get(255)
