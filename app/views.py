from datetime import datetime

from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from app.cal_returns import get_returns
from app.models import Hs300StockList


class Login(APIView):
    renderer_classes = [JSONRenderer]  # 指定JSON渲染器

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        try:
            user_obj = User.objects.get(email=email)

            if not user_obj.check_password(password):
                return Response({'error': '密码错误，如忘记密码，请修改密码'})
            else:
                token, created = Token.objects.get_or_create(user=user_obj)
                user = {
                    'username': user_obj.username,
                    'email': user_obj.email,
                }
                return Response({'success': '登陆成功！', 'token': token.key, 'user': user})
        except:
            return Response({'error': '用户不存在，请先注册'})


class CheckToken(APIView):
    renderer_classes = [JSONRenderer]  # 指定JSON渲染器

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, reqeust):
        token = reqeust.data['token']
        if Token.objects.filter(key=token).exists():
            token = Token.objects.get(key=token)
            user_obj = token.user
            user = {
                'username': user_obj.username,
                'email': user_obj.email,
            }
            return Response({'success': '登录成功', 'user': user})

        else:
            return Response({'error': 'token失效，请重新登陆'})


class Register(APIView):
    renderer_classes = [JSONRenderer]  # 指定JSON渲染器

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        email = request.data['email']
        try:
            user_obj = User.objects.get(email=email)
        except:
            user_obj = None
        if user_obj is not None:
            return Response({'error': '用户已存在！'})
        else:
            user_obj = User.objects.create_user(username=username, password=password, email=email)
            user_obj.save()
            return Response({'success': '注册成功'})


class Forget(APIView):
    renderer_classes = [JSONRenderer]  # 指定JSON渲染器

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user_obj = User.objects.get(email=email)
        user_obj.set_password(password)
        user_obj.save()
        return Response({'success': '密码修改成功！'})


class Calculate(APIView):
    renderer_classes = [JSONRenderer]  # 指定JSON渲染器
    now_stocks = {}
    # 策略组合和仓位
    strategy_stocks = {}
    # 累计收益率
    cum_returns = []

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        print(request)
        # 当前投资组合和仓位

        now_date = datetime(year=2015, month=4, day=3)
        # 获取股票池数据
        stock_list = Hs300StockList.objects.all()
        stock_list = [i.stock_code for i in stock_list]
        cum_returns = get_returns()

        return Response({'success': "计算完成", 'returns': cum_returns})
