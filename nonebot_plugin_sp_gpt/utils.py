import openai  # 导入 openai 库
import re
import json
import nls
import os
import nonebot

from nonebot.log import logger


class Chatbot:
    def __init__(self):
        self.debug = False
        self.gpt_cfg_path = 'data/gpt/'
        self.gpt_cfg_name = 'gpt_cfg.json'
        self.ReadCfg()
        openai.api_key = self.cfg["apikey"]

    def generate_message(self, sessionId, prompt):
        msg = []
        if self.cfg["cfg"][sessionId]["UseRP"]:
            msg.append(self.cfg["cfg"][sessionId]["RPmessage"])
        msg.append({"role": "user", "content": prompt})
        return msg

    def generate_response(self, msg):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=msg,
            temperature=0.7,
            max_tokens=512,)
        return completion

    def analyze_chat_responses(self, resp):
        if self.cfg["debug"]:
            chatResp = str(resp)
        else:
            chatResp = str(resp.choices[0].message.content)
        chatResp = re.sub(r'\n\s*\n', '\n', chatResp)
        chatResp = chatResp.lstrip()
        print(chatResp)
        return chatResp

    def ReadCfg(self):
        try:
            with open(self.gpt_cfg_path+self.gpt_cfg_name, 'r', encoding='utf-8') as f:
                self.cfg = json.loads(f.read())
            return self.cfg
        except Exception as e:
            logger.warning(f'创建{self.gpt_cfg_path}{self.gpt_cfg_name}')
            self.cfg = {
                "apikey": "",
                "debug": False,
                "cfg": {
                    "default": {
                        "UseRP": False,
                        "RProle": "",
                        "RPprompt": "",
                        "RPmessage": {"": ""},
                        "Context": 0,
                        "ProcessHint": "处理中"}
                }
            }
            self.WriteCfg()
            return {}

    def WriteCfg(self):
        os.makedirs(self.gpt_cfg_path, mode=0o777, exist_ok=True)
        with open(self.gpt_cfg_path+self.gpt_cfg_name, 'w', encoding='utf-8') as f:
            print(self.cfg)
            f.write(json.dumps(self.cfg))

    def CheckCfg(self, sessionId):
        if sessionId not in self.cfg["cfg"]:
            self.cfg["cfg"][sessionId] = {"UseRP": False,
                                          "RProle": "",
                                          "RPprompt": "",
                                          "RPmessage": {"": ""},
                                          "Context": 0,
                                          "ProcessHint": "处理中"}
            self.WriteCfg()

    def SetDebug(self, d):
        self.cfg["debug"] = d
        self.WriteCfg()

    def AddRP(self, sessionId, rpr, rpp):
        self.cfg["cfg"][sessionId]["RProle"] = rpr
        self.cfg["cfg"][sessionId]["RPprompt"] = rpp
        self.cfg["cfg"][sessionId]["RPmessage"] = {
            "role": "system", "content": rpp}
        self.WriteCfg()

    def SetUseRp(self, sessionId, enable):
        self.cfg["cfg"][sessionId]["UseRP"] = enable
        self.WriteCfg()

    def SetHint(self, sessionId, hint):
        self.cfg["cfg"][sessionId]["ProcessHint"] = hint
        self.WriteCfg()
