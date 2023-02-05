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

    def init_api(self,
                 ) -> Any:
        openai.api_key = self.OPENAI_API_KEY
        return self

    def _request_openai(self,
                        msg: str
                        ) -> Union[Any]:
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
             ) -> Union[Any, bool]:
        if self.check_init():
            return self._request_openai(msg)
        return False