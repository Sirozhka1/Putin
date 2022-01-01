

from .. import loader, utils

import logging
import datetime
import time

from telethon import functions, types

logger = logging.getLogger(__name__)


@loader.tds
class PM_Mod(loader.Module):
    """
    PM (PM MOD) :
    -> Предотвращает отправку людьми нежелательных личных сообщений.
    -> Предотвращает беспокойство, когда вы недоступны.\n
    Commands :
     
    """
    strings = {"name": "PM_MOD",
               "afk": "<b>Я сейчас afk (since</b> <i>{}</i> <b>ago).</b>",
               "afk_back": "<b>AFK back !</b>",
               "afk_gone": "<b>Я собираюсь AFK !</b>",
               "afk_no_group_off": "<b>Статусное сообщение AFK включено для групповых чатов.</b>",
               "afk_no_group_on": "<b>Сообщение о статусе AFK отключено для групповых чатов.</b>",
               "afk_no_pm_off": "<b>Сообщение о статусе AFK отключено для PM.</b>",
               "afk_no_pm_on": "<b>Статусное сообщение AFK включено для PM.</b>",
               "afk_notif_off": "<b>Уведомления теперь отключены во время AFK.</b>",
               "afk_notif_on": "<b>Уведомления теперь включены во время AFK.</b>",
               "afk_rate_limit_off": "<b>Ограничение количества сообщений о статусе AFK отключено.</b>",
               "afk_rate_limit_on": ("<b>Ограничение скорости сообщений о статусе AFK включено.</b>"
                                     "\n\n<b>Максимальное количество сообщений о статусе AFK будет отправлено на чат</b>"),
               "afk_reason": ("<b>Я сейчас AFK (since {} ago).</b>"
                              "\n\n<b>Причина :</b> <i>{}</i>"),
               "arg_on_off": "<b>Аргумент должен быть 'off' или 'on'! </b>",
               "pm_off": ("<b>Автоматический ответ для отклоненных сообщений в личном кабинете отключен."
                          "\n\nПользователи теперь свободны от PM!</b>"),
               "pm_on": "<b>На отклоненные сообщения теперь отправляется автоматический ответ.</b>",
               "pm_allowed": "<b>Я разрешил</b> <a href='tg://user?id={}'>you</a> <b>писать в лс.</b>",
               "pm_blocked": ("<b>Я не хочу получать сообщения от</b> <a href='tg://user?id={}'>you</a>, "
                              "<b>Вы заблокированы!</b>"),
               "pm_denied": "<b>Я отказал </b> <a href='tg://user?id={}'>you</a> <b>писать личные сообщения мне.</b>",
               "pm_go_away": ("Привет! К сожалению, я не принимаю личные сообщения от незнакомцев."
                              "\n\nПожалуйста, свяжитесь со мной в группе или <b>wait</b> пока я отвечу."),
               "pm_reported": "<b>Я отправил репорт!</b>",
               "pm_limit_arg": "<b>Аргумент должен быть 'off', 'on' или числом от 5 до 1000!</b>",
               "pm_limit_off": "<b>Запрещенные пользователи теперь могут свободно посещать личку без автоматической блокировки.</b>",
               "pm_limit_on": "<b>Запрещенные пользователи теперь блокируются {} PMs.</b>",
               "pm_limit_current": "<b>Текущий лимит {}.</b>",
               "pm_limit_current_no": "<b>Автоматическая блокировка пользователей в настоящее время отключена.</b>",
               "pm_limit_reset": "<b>Лимит сброшен до {}.</b>",
               "pm_limit_set": "<b>Лимит установлен на {}.</b>",
               "pm_notif_off": "<b>Уведомления от запрещенных личных сообщений отключены.</b>",
               "pm_notif_on": "<b>Уведомления от запрещенных PM теперь включены.</b>",
               "pm_triggered": ("Эй! Мне не нравится, что ты так часто пишешь мне!"
                                "\nВы даже просили меня утвердить вас в личку? Нет?"
                                "\nТогда до свидания."
                                "\n\nPS: о вас сообщили как о спаме."),
               "pm_unblocked": ("<b>Хорошо! На этот раз я прощаю их. PM разблокирован для </b> "
                                "<a href='tg://user?id={}'>this user</a>."),
               "unknow": ("Произошла ошибка!"),
               "who_to_allow": "<b>Кому разрешить писать в личку?</b>",
               "who_to_block": "<b>Укажите, кого заблокировать.</b>",
               "who_to_deny": "<b>Кому мне отказать в личке?</b>",
               "who_to_report": "<b>Кого мне репортить?</b>",
               "who_to_unblock": "<b>Укажите, кого разблокировать.</b>"}

    def __init__(self):
        self._me = None
        self.default_pm_limit = 50

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me(True)

    async def unafkcmd(self, message):
        """Remove the AFK status.\n """
        self._db.set(__name__, "afk", False)
        self._db.set(__name__, "afk_gone", None)
        self._db.set(__name__, "afk_rate", [])
        await utils.answer(message, self.strings("afk_back", message))

    async def afkcmd(self, message):
        """
        .afk : Enable AFK status.
        .afk [message] : Enable AFK status and add a reason.
         
        """
        if utils.get_args_raw(message):
            self._db.set(__name__, "afk", utils.get_args_raw(message))
        else:
            self._db.set(__name__, "afk", True)
        self._db.set(__name__, "afk_gone", time.time())
        self._db.set(__name__, "afk_rate", [])
        await utils.answer(message, self.strings("afk_gone", message))

    async def afknogroupcmd(self, message):
        """
        .afknogroup : Disable/Enable AFK status message for group chats.
        .afknogroup off : Enable AFK status message for group chats.
        .afknogroup on : Disable AFK status message for group chats.
         
        """
        if utils.get_args_raw(message):
            afknogroup_arg = utils.get_args_raw(message)
            if afknogroup_arg == "off":
                self._db.set(__name__, "afk_no_group", False)
                await utils.answer(message, self.strings("afk_no_group_off"))
            elif afknogroup_arg == "on":
                self._db.set(__name__, "afk_no_group", True)
                await utils.answer(message, self.strings("afk_no_group_on", message))
            else:
                await utils.answer(message, self.strings("arg_on_off", message))
        else:
            afknogroup_current = self._db.get(__name__, "afk_no_group")
            if afknogroup_current is None or afknogroup_current is False:
                self._db.set(__name__, "afk_no_group", True)
                await utils.answer(message, self.strings("afk_no_group_on", message))
            elif afknogroup_current is True:
                self._db.set(__name__, "afk_no_group", False)
                await utils.answer(message, self.strings("afk_no_group_off", message))
            else:
                await utils.answer(message, self.strings("unknow", message))

    async def afknopmcmd(self, message):
        """
        .afknopm : Disable/Enable AFK status message for PMs.
        .afknopm off : Enable AFK status message for PMs.
        .afknopm on : Disable AFK status message for PMs.
         
        """
        if utils.get_args_raw(message):
            afknopm_arg = utils.get_args_raw(message)
            if afknopm_arg == "off":
                self._db.set(__name__, "afk_no_pm", False)
                await utils.answer(message, self.strings("afk_no_pm_off", message))
            elif afknopm_arg == "on":
                self._db.set(__name__, "afk_no_pm", True)
                await utils.answer(message, self.strings("afk_no_pm_on", message))
            else:
                await utils.answer(message, self.strings("arg_on_off", message))
        else:
            afknopm_current = self._db.get(__name__, "afk_no_pm")
            if afknopm_current is None or afknopm_current is False:
                self._db.set(__name__, "afk_no_pm", True)
                await utils.answer(message, self.strings("afk_no_pm_on", message))
            elif afknopm_current is True:
                self._db.set(__name__, "afk_no_pm", False)
                await utils.answer(message, self.strings("afk_no_pm_off", message))
            else:
                await utils.answer(message, self.strings("unknow", message))

    async def afknotifcmd(self, message):
        """
        .afknotif : Disable/Enable the notifications during AFK time.
        .afknotif off : Disable the notifications during AFK time.
        .afknotif on : Enable the notifications during AFK time.
         
        """
        if utils.get_args_raw(message):
            afknotif_arg = utils.get_args_raw(message)
            if afknotif_arg == "off":
                self._db.set(__name__, "afk_notif", False)
                await utils.answer(message, self.strings("afk_notif_off", message))
            elif afknotif_arg == "on":
                self._db.set(__name__, "afk_notif", True)
                await utils.answer(message, self.strings("afk_notif_on", message))
            else:
                await utils.answer(message, self.strings("arg_on_off", message))
        else:
            afknotif_current = self._db.get(__name__, "afk_notif")
            if afknotif_current is None or afknotif_current is False:
                self._db.set(__name__, "afk_notif", True)
                await utils.answer(message, self.strings("afk_notif_on", message))
            elif afknotif_current is True:
                self._db.set(__name__, "afk_notif", False)
                await utils.answer(message, self.strings("afk_notif_off", message))
            else:
                await utils.answer(message, self.strings("unknow", message))

    async def afkratecmd(self, message):
        """
        .afkrate : Disable/Enable AFK rate limit.
        .afkrate off : Disable AFK rate limit.
        .afkrate on : Enable AFK rate limit. One AFK status message max will be sent per chat.
         
        """
        if utils.get_args_raw(message):
            afkrate_arg = utils.get_args_raw(message)
            if afkrate_arg == "off":
                self._db.set(__name__, "afk_rate_limit", False)
                await utils.answer(message, self.strings("afk_rate_limit_off", message))
            elif afkrate_arg == "on":
                self._db.set(__name__, "afk_rate_limit", True)
                await utils.answer(message, self.strings("afk_rate_limit_on", message))
            else:
                await utils.answer(message, self.strings("arg_on_off", message))
        else:
            afkrate_current = self._db.get(__name__, "afk_rate_limit")
            if afkrate_current is None or afkrate_current is False:
                self._db.set(__name__, "afk_rate_limit", True)
                await utils.answer(message, self.strings("afk_rate_limit_on", message))
            elif afkrate_current is True:
                self._db.set(__name__, "afk_rate_limit", False)
                await utils.answer(message, self.strings("afk_rate_limit_off", message))
            else:
                await utils.answer(message, self.strings("unknow", message))

    async def allowcmd(self, message):
        """Allow this user to PM.\n """
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_allow", message))
            return
        self._db.set(__name__, "allow", list(set(self._db.get(__name__, "allow", [])).union({user})))
        await utils.answer(message, self.strings("pm_allowed", message).format(user))

    async def blockcmd(self, message):
        """Block this user to PM without being warned.\n """
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_block", message))
            return
        await message.client(functions.contacts.BlockRequest(user))
        await utils.answer(message, self.strings("pm_blocked", message).format(user))

    async def denycmd(self, message):
        """Deny this user to PM without being warned.\n """
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_deny", message))
            return
        self._db.set(__name__, "allow", list(set(self._db.get(__name__, "allow", [])).difference({user})))
        await utils.answer(message, self.strings("pm_denied", message).format(user))

    async def pmcmd(self, message):
        """
        .pm : Disable/Enable automatic answer for denied PMs.
        .pm off : Disable automatic answer for denied PMs.
        .pm on : Enable automatic answer for denied PMs.
         
        """
        if utils.get_args_raw(message):
            pm_arg = utils.get_args_raw(message)
            if pm_arg == "off":
                self._db.set(__name__, "pm", True)
                await utils.answer(message, self.strings("pm_off", message))
            elif pm_arg == "on":
                self._db.set(__name__, "pm", False)
                await utils.answer(message, self.strings("pm_on", message))
            else:
                await utils.answer(message, self.strings("arg_on_off", message))
        else:
            pm_current = self._db.get(__name__, "pm")
            if pm_current is None or pm_current is False:
                self._db.set(__name__, "pm", True)
                await utils.answer(message, self.strings("pm_off", message))
            elif pm_current is True:
                self._db.set(__name__, "pm", False)
                await utils.answer(message, self.strings("pm_on", message))
            else:
                await utils.answer(message, self.strings("unknow", message))

    async def pmlimitcmd(self, message):
        """
        .pmlimit : Get current max number of PMs before automatically block not allowed user.
        .pmlimit off : Disable automatic user blocking.
        .pmlimit on : Enable automatic user blocking.
        .pmlimit reset : Reset max number of PMs before automatically block not allowed user.
        .pmlimit [number] : Modify max number of PMs before automatically block not allowed user.
         
        """
        if utils.get_args_raw(message):
            pmlimit_arg = utils.get_args_raw(message)
            if pmlimit_arg == "off":
                self._db.set(__name__, "pm_limit", False)
                await utils.answer(message, self.strings("pm_limit_off", message))
                return
            elif pmlimit_arg == "on":
                self._db.set(__name__, "pm_limit", True)
                pmlimit_on = self.strings("pm_limit_on", message).format(self.get_current_pm_limit())
                await utils.answer(message, pmlimit_on)
                return
            elif pmlimit_arg == "reset":
                self._db.set(__name__, "pm_limit_max", self.default_pm_limit)
                pmlimit_reset = self.strings("pm_limit_reset", message).format(self.get_current_pm_limit())
                await utils.answer(message, pmlimit_reset)
                return
            else:
                try:
                    pmlimit_number = int(pmlimit_arg)
                    if pmlimit_number >= 5 and pmlimit_number <= 1000:
                        self._db.set(__name__, "pm_limit_max", pmlimit_number)
                        pmlimit_new = self.strings("pm_limit_set", message).format(self.get_current_pm_limit())
                        await utils.answer(message, pmlimit_new)
                        return
                    else:
                        await utils.answer(message, self.strings("pm_limit_arg", message))
                        return
                except ValueError:
                    await utils.answer(message, self.strings("pm_limit_arg", message))
                    return
            await utils.answer(message, self.strings("limit_arg", message))
        else:
            pmlimit = self._db.get(__name__, "pm_limit")
            if pmlimit is None or pmlimit is False:
                pmlimit_current = self.strings("pm_limit_current_no", message)
            elif pmlimit is True:
                pmlimit_current = self.strings("pm_limit_current", message).format(self.get_current_pm_limit())
            else:
                await utils.answer(message, self.strings("unknow", message))
                return
            await utils.answer(message, pmlimit_current)

    async def pmnotifcmd(self, message):
        """
        .pmnotif : Disable/Enable the notifications from denied PMs.
        .pmnotif off : Disable the notifications from denied PMs.
        .pmnotif on : Enable the notifications from denied PMs.
         
        """
        if utils.get_args_raw(message):
            pmnotif_arg = utils.get_args_raw(message)
            if pmnotif_arg == "off":
                self._db.set(__name__, "pm_notif", False)
                await utils.answer(message, self.strings("pm_notif_off", message))
            elif pmnotif_arg == "on":
                self._db.set(__name__, "pm_notif", True)
                await utils.answer(message, self.strings("pm_notif_on", message))
            else:
                await utils.answer(message, self.strings("arg_on_off", message))
        else:
            pmnotif_current = self._db.get(__name__, "pm_notif")
            if pmnotif_current is None or pmnotif_current is False:
                self._db.set(__name__, "pm_notif", True)
                await utils.answer(message, self.strings("pm_notif_on", message))
            elif pmnotif_current is True:
                self._db.set(__name__, "pm_notif", False)
                await utils.answer(message, self.strings("pm_notif_off", message))
            else:
                await utils.answer(message, self.strings("unknow", message))

    async def reportcmd(self, message):
        """Report the user to spam. Use only in PM.\n """
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_report", message))
            return
        self._db.set(__name__, "allow", list(set(self._db.get(__name__, "allow", [])).difference({user})))
        if message.is_reply and isinstance(message.to_id, types.PeerChannel):
            await message.client(functions.messages.ReportRequest(peer=message.chat_id,
                                                                  id=[message.reply_to_msg_id],
                                                                  reason=types.InputReportReasonSpam()))
        else:
            await message.client(functions.messages.ReportSpamRequest(peer=message.to_id))
        await utils.answer(message, self.strings("pm_reported", message))

    async def unblockcmd(self, message):
        """Unblock this user to PM."""
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_unblock"))
            return
        await message.client(functions.contacts.UnblockRequest(user))
        await utils.answer(message, self.strings("pm_unblocked", message).format(user))

    async def watcher(self, message):
        user = await utils.get_user(message)
        pm = self._db.get(__name__, "pm")
        if getattr(message.to_id, "user_id", None) == self._me.user_id and (pm is None or pm is False):
            if not user.is_self and not user.bot and not user.verified and not self.get_allowed(message.from_id):
                await utils.answer(message, self.strings("pm_go_away",message))
                if self._db.get(__name__, "pm_limit") is True:
                    pms = self._db.get(__name__, "pms", {})
                    pm_limit = self._db.get(__name__, "pm_limit_max")
                    pm_user = pms.get(message.from_id, 0)
                    if isinstance(pm_limit, int) and pm_limit >= 5 and pm_limit <= 1000 and pm_user >= pm_limit:
                        await utils.answer(message, self.strings("pm_triggered", message))
                        await message.client(functions.contacts.BlockRequest(message.from_id))
                        await message.client(functions.messages.ReportSpamRequest(peer=message.from_id))
                        del pms[message.from_id]
                        self._db.set(__name__, "pms", pms)
                    else:
                        self._db.set(__name__, "pms", {**pms, message.from_id: pms.get(message.from_id, 0) + 1})
                pm_notif = self._db.get(__name__, "pm_notif")
                if pm_notif is None or pm_notif is False:
                    await message.client.send_read_acknowledge(message.chat_id)
                return
        if message.mentioned or getattr(message.to_id, "user_id", None) == self._me.user_id:
            afk_status = self._db.get(__name__, "afk")
            if user.is_self or user.bot or user.verified or afk_status is False:
                return
            if message.mentioned and self._db.get(__name__, "afk_no_group") is True:
                return
            afk_no_pm = self._db.get(__name__, "afk_no_pm")
            if getattr(message.to_id, "user_id", None) == self._me.user_id and afk_no_pm is True:
                return
            if self._db.get(__name__, "afk_rate_limit") is True:
                afk_rate = self._db.get(__name__, "afk_rate", [])
                if utils.get_chat_id(message) in afk_rate:
                    return
                else:
                    self._db.setdefault(__name__, {}).setdefault("afk_rate", []).append(utils.get_chat_id(message))
                    self._db.save()
            now = datetime.datetime.now().replace(microsecond=0)
            gone = datetime.datetime.fromtimestamp(self._db.get(__name__, "afk_gone")).replace(microsecond=0)
            diff = now - gone
            if afk_status is True:
                afk_message = self.strings("afk", message).format(diff)
            elif afk_status is not False:
                afk_message = self.strings("afk_reason", message).format(diff, afk_status)
            await utils.answer(message, afk_message)
            afk_notif = self._db.get(__name__, "afk_notif")
            if afk_notif is None or afk_notif is False:
                await message.client.send_read_acknowledge(message.chat_id)

    def get_allowed(self, id):
        return id in self._db.get(__name__, "allow", [])

    def get_current_pm_limit(self):
        pm_limit = self._db.get(__name__, "pm_limit_max")
        if not isinstance(pm_limit, int) or pm_limit < 5 or pm_limit > 1000:
            pm_limit = self.default_pm_limit
            self._db.set(__name__, "pm_limit_max", pm_limit)
        return pm_limit
