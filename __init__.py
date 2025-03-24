import asyncio
import os
import zipfile
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata
from jmcomic import *

# 插件元信息
__plugin_meta__ = PluginMetadata(
    name="下载并压缩文件",
    description="识别群消息中的'/下载'命令（可带参数），下载文件夹并压缩后发送到群聊",
    usage="发送 '/下载' 或 '/下载xxx' 到群聊触发功能"
)


# 假设你已经有一个下载文件夹的方法，定义为 download_folder()
# 这里用一个占位符表示，你需要替换成实际的方法
async def download_folder(param: int = "") -> str:
    # 创建自定义配置，动态设置 base_dir
    option = JmOption.construct({
        'plugins': {
            'after_album': [  # 在专辑下载完成后执行
                {
                    'plugin': 'img2pdf',  # 使用 img2pdf 插件
                    'kwargs': {
                        'pdf_dir': 'C:\MahiroBot\Bot\zhenxun_bot-main\zhenxun\plugins\JmDownloader\kooks',  # PDF 保存目录
                        'filename_rule': 'Aid'  # 命名规则：专辑 ID（如 438696.pdf）
                    }
                }
            ]
        }
    })

    # 下载漫画
    album = download_album(str(param), option=option)

    print("==============================================")


    # 检查下载结果并返回路径
    album_path = os.path.join('C:\MahiroBot\Bot\zhenxun_bot-main\zhenxun\plugins\JmDownloader\kooks', str(param))
    print(album_path)
    if os.path.exists(album_path):
        return album_path
    else:
        return ""


# 定义正则处理器，匹配以 "/下载" 开头的消息
download_cmd = on_regex(r"^/jm(.*)$", priority=5, block=True)


@download_cmd.handle()
async def handle_download(bot: Bot, event: GroupMessageEvent):
    # 获取群号
    group_id = event.group_id

    # 从消息中提取参数（/下载后面的部分）
    raw_message = event.get_plaintext().strip()
    param = raw_message.replace("/jm", "", 1).strip()  # 提取 "111" 或 "asd"，无参数时为空字符串

    try:
        # 调用下载方法，传入参数，获取文件夹路径
        await download_cmd.send(f"正在下载{param}")
        await download_folder(param)
        base_dir = os.path.join(os.path.dirname(__file__), "kooks")
        pdf_filename = f"{param}.pdf"
        pdf_path = os.path.join(base_dir, pdf_filename)

        if not os.path.exists(pdf_path):
            return False

        # 压缩文件夹

        # 发送压缩文件到群聊
        await bot.upload_group_file(
            group_id=group_id,
            file=pdf_path,
            name=pdf_filename
        )


        # 发送成功提示
        await download_cmd.finish()

        # 可选：清理临时文件


    except Exception as e:
        # 异常处理
        await download_cmd.finish()
