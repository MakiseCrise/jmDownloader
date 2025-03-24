import asyncio
import os
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata
from jmcomic import *

__plugin_meta__ = PluginMetadata(
    name="漫画下载器",
    description="通过 '/jm<漫画ID>' 下载漫画并生成 PDF 发送到群聊",
    usage="发送 '/jm123' 到群聊触发功能"
)


async def download_folder(param: str = "") -> str:
    if not param:
        return ""

    base_dir = os.path.join(os.path.dirname(__file__), "kooks")
    option = JmOption.construct({
        'plugins': {
            'after_album': [{
                'plugin': 'img2pdf',
                'kwargs': {
                    'pdf_dir': base_dir,
                    'filename_rule': 'Aid'
                }
            }]
        }
    })

    download_album(param, option=option)
    pdf_path = os.path.join(base_dir, f"{param}.pdf")
    return pdf_path if os.path.exists(pdf_path) else ""


download_cmd = on_regex(r"^/jm(.*)$", priority=5, block=True)


@download_cmd.handle()
async def handle_download(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    raw_message = event.get_plaintext().strip()
    param = raw_message.replace("/jm", "", 1).strip()

    if not param or not param.isdigit():
        await download_cmd.finish("请提供有效的漫画 ID，例如 /jm123")

    try:
        await download_cmd.send(f"正在下载漫画 {param}")
        pdf_path = await download_folder(param)
        if not pdf_path:
            await download_cmd.finish(f"下载 {param} 失败，请检查 ID 是否正确")

        # 定义新的文件名格式：元梦之星改pdf{param}.zip
        new_filename = f"元梦之星改pdf{param}.zip"

        # 直接使用原始 PDF 文件路径，但上传时使用新文件名
        await bot.upload_group_file(
            group_id=group_id,
            file=pdf_path,  # 文件路径保持不变，仍为 PDF
            name=new_filename  # 文件名改为指定格式
        )
        await download_cmd.finish(f"已发送 {new_filename}")
        os.remove(pdf_path)  # 清理临时文件

    except Exception as e:
        await download_cmd.finish(f"发生错误：{str(e)}")