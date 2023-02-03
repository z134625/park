import openai
import functools

from typing import Union, Any

from ...utils import (
    base,
    api
)


class OpenAi(base.ParkLY):
    _name = 'openai'
    _inherit = ['intellect']

    @api.monitor(fields='check_init')
    def init_api(self,
                 path: str
                 ) -> None:
        self.env['setting'].open(path).give(self)
        openai.api_key = self.OPENAI_API_KEY

    def _request_openai(self, msg: str) -> Union[Any]:
        assert self.context.is_init
        self.update({
            '_error': False
        })
        paras = {
            'logprobs': 10,
            'top_p': 0,
            'model': 'text-davinci-003',
            'prompt': f"<|endoftext|>{msg}\n--\nLabel:",
            'temperature': float(self.TEMPERATURE) or 0.9,
        }
        if self.MAX_TOKENS:
            paras.update({
                'max_tokens': int(self.MAX_TOKENS)
            })
        # if isinstance(msg, str):
        response = openai.Completion.create(**paras)
        # else:
        #     tasks = [openai.Completion.acreate(**{**paras,
        #                                           **{'prompt': f"<|endoftext|>{m}\n--\nLabel:"}}) for m in msg]
        #     loop = asyncio.get_event_loop()
        #     loop.run_until_complete(asyncio.wait(tasks))
        text = response.choices[0].text
        # ts = re.split('\n', text)
        return text

    @functools.lru_cache()
    def test(self,
             msg: str,
             setting_path: str = None
             ) -> None:
        self.init_api(setting_path or self.context.setting_path)
        return self._request_openai(msg)
