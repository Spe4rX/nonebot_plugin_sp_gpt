import asyncio
import os

from nonebot import get_driver
from nonebot import on_command, on_regex
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    Message,
    MessageSegment,
    PrivateMessageEvent,
    GroupMessageEvent)
from nonebot.typing import T_State


from .utils import *
from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

bot = Chatbot()
chat = on_regex(r"^/(?:chat|gpt)\s(?:(tts)\s(?:(sk|qy|gg)\s)?)?(.*)")
chatcfg = on_regex(r"^/chatcfg\s(debug|rp|RP|hint)\s(\S*)(?:\s(.*))?")


@chat.handle()
async def _(event: MessageEvent, state: T_State):
    if isinstance(event, PrivateMessageEvent):
        sessionId = 'user_' + str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        sessionId = 'group_' + str(event.group_id)

    bot.CheckCfg(sessionId=sessionId)
    args = list(state["_matched_groups"])

    prompt = args[2]
    if prompt == "" or prompt == None or prompt.isspace():
        await chat.finish("无内容")
    await chat.send(bot.cfg["cfg"][sessionId]["ProcessHint"])
    msg = bot.generate_message(sessionId=sessionId, prompt=prompt)
    if bot.cfg["debug"]:
        await chat.send(str(msg))
    loop = asyncio.get_event_loop()
    try:
        res = await loop.run_in_executor(None, bot.generate_response, msg)
    except Exception as e:
        await chat.finish(str(e))

    t = bot.analyze_chat_responses(res)
    await chat.send(t)


@chatcfg.handle()
async def _(event: MessageEvent, state: T_State):
    if isinstance(event, PrivateMessageEvent):
        sessionId = 'user_' + str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        sessionId = 'group_' + str(event.group_id)
    bot.CheckCfg(sessionId=sessionId)
    args = list(state["_matched_groups"])
    if args[0] == "debug":
        if args[1] == "enable":
            bot.SetDebug(True)
            await chatcfg.finish("已启用Debug")
        elif args[1] == "disable":
            bot.SetDebug(False)
            await chatcfg.finish("已禁用Debug")
    elif args[0] == "rp" or args[0] == "RP":
        if args[1] == "enable":
            bot.SetUseRp(sessionId=sessionId, enable=True)
            await chatcfg.finish("已启用RP")
        elif args[1] == "disable":
            bot.SetUseRp(sessionId=sessionId, enable=False)
            await chatcfg.finish("已禁用RP")
        elif args[2] != "" and args[2] != None:
            bot.AddRP(sessionId=sessionId, rpr=args[1], rpp=args[2])
            await chatcfg.finish("添加完成")
        else:
            await chatcfg.finish("添加失败")
    elif args[0] == "hint":
        if args[1] != "" and args[1] != None:
            bot.SetHint(sessionId=sessionId, hint=args[1])
            await chatcfg.finish("添加提示词完成")
