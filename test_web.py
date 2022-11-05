from park.web.park import ParkWeb
from park.web.park.server import render
from park.conf.setting import RealTimeUpdate


app = ParkWeb()


@app.route('/')
def main(request):
    # print(request)
    body = '<h1>Hello, EE!</h1>'
    return body

# @app.route('/main', method={"POST", "GET"})
# def main1(request):
#     body = './template/plda.html'
#     return render(body)


def p():
    app.start()


if __name__ == '__main__':
    r = RealTimeUpdate(func=p)
    r.start()
