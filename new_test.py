import re

from parkPro.utils.env import env
from parkPro.utils import api, base


class Test(base.ParkLY):
    _inherit = 'flask'

    @api.flask_route('/',
                     methods=['GET', 'POST']
                     )
    def main_web(self):
        if self.context.request.method == 'POST':
            openai = self.env['openai']
            msg = self.context.request.form["msg"]
            response = openai.test(msg, './conf.py')
            return self.render(result=response)
        return self.render("""<!DOCTYPE html>
<head>
  <title>ChatGPT 测试</title>
  <style>
  @font-face {
  font-family: "ColfaxAI";
  src: url(https://cdn.openai.com/API/fonts/ColfaxAIRegular.woff2)
      format("woff2"),
    url(https://cdn.openai.com/API/fonts/ColfaxAIRegular.woff) format("woff");
  font-weight: normal;
  font-style: normal;
}
@font-face {
  font-family: "ColfaxAI";
  src: url(https://cdn.openai.com/API/fonts/ColfaxAIBold.woff2) format("woff2"),
    url(https://cdn.openai.com/API/fonts/ColfaxAIBold.woff) format("woff");
  font-weight: bold;
  font-style: normal;
}
body,
input {
  font-size: 16px;
  line-height: 24px;
  color: #353740;
  font-family: "ColfaxAI", Helvetica, sans-serif;
}
body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 60px;
}
.icon {
  width: 34px;
}
h3 {
  font-size: 32px;
  line-height: 40px;
  font-weight: bold;
  color: #202123;
  margin: 16px 0 40px;
}
form {
  display: flex;
  flex-direction: column;
  width: 320px;
}
input[type="text"] {
  padding: 12px 16px;
  border: 1px solid #10a37f;
  border-radius: 4px;
  margin-bottom: 24px;
}
::placeholder {
  color: #8e8ea0;
  opacity: 1;
}
input[type="submit"] {
  padding: 12px 0;
  color: #fff;
  background-color: #10a37f;
  border: none;
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
}
.result {
  font-weight: bold;
  margin-top: 40px;
}

  </style>
</head>

<body>
  <h3>Park ZLY </h3>
  <form action="/" method="post">
    <input type="text" name="msg" placeholder="输入询问的问题" required />
    <input type="submit" value="提交" />
  </form>
{% if result %}
  <div class="result">{{ result }}</div>
{% endif %}
</body>
""", result=None)


if __name__ == '__main__':
    env.load()
    p = env['flask']
    p.main(['--start'], delay=0.2, epoch_show=False)

