from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import time
@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.muted_user = dict()

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    def parse_duration(self,duration: str) -> int:
        if not duration:
            return 0
        try:
            num = int(duration[:-1])
        except ValueError:
            return -1
        time_dic = {'s':1,'m':60,'h':3600,'d':86400}
        if duration[-1].lower() not in time_dic:
            return -1
        if num<=0:
            return -2
        return num*time_dic[duration[-1].lower()]
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("mute_user")
    async def mute_user(self, event: AstrMessageEvent,user_id :str,mute_time:str):
        """这是一个 mute_user 指令，用于指定用户id进行禁言，使其无法于机器人交互""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        state_num = self.parse_duration(mute_time)
        if state_num == 0:
            yield event.plain_result(f"格式错误，请使用 /mute_user + 用户id + 时间 的格式禁言用户，示例：/mute_user 123456 60s")
        if state_num == -1:
            yield event.plain_result(f"格式错误，请以数字+s/m/h/d的格式设置禁言时间")
            return
        if state_num == -2:
            yield event.plain_result(f"禁言时间不能为负数！")
            return
        self.muted_user[user_id] = time.time() + state_num
        logger.info(f"当前禁言名单：{self.muted_user}")

        '''user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)'''
        yield event.plain_result(f"Mute user:{user_id} success!") # 发送一条纯文本消息

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("unmute_user")
    async def unmute_user(self, event: AstrMessageEvent,user_id :str):
        if not self.remove_mute(user_id):
            yield event.plain_result(f"该用户未被禁言")
            return
        yield event.plain_result(f"Unmute user:{user_id} success!")
        logger.info(f"解除禁言用户：{user_id}")

    def remove_mute(self,user_id:str):
        if user_id not in self.muted_user:
            return False
        del self.muted_user[user_id]
        return True

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def check_message(self,event:AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id not in self.muted_user:
            return
        end_time = self.muted_user[user_id]
        if end_time <= time.time():
            self.remove_mute(user_id)
            logger.info(f"User {user_id} unmute for time")
            return
        logger.info(f"User {user_id} is still be muted")
        event.stop_event()


    async def terminate(self):
        pass
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
