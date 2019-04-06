from django.shortcuts import render
from upstox_api.api import *
import datetime
#import os
from . import settings
#import sqlite3
import multiprocessing.dummy as mp
import requests

global gainers

def home(request):
    return  render(request, 'home.html')

def session(request):
    return render(request,'session.html')



def get_url(request):
    s = Session ('rfFYsHqjVM8gl8DjbaWAs7lR1kPk5t969YHl6jlb')
    s.set_redirect_uri ('http://upstox.com:3000')
    s.set_api_secret ('u4dlbfsql9')
    url = s.get_login_url()
    return render(request, 'link.html',{'url':url})

def get_api(request):
    s = Session ('rfFYsHqjVM8gl8DjbaWAs7lR1kPk5t969YHl6jlb')
    s.set_redirect_uri ('http://upstox.com:3000')
    s.set_api_secret ('u4dlbfsql9')
    code = request.GET['code']
    s.set_code (code)
    access_token = s.retrieve_access_token()
    request.session['access_token'] = access_token
    return render(request,'getapi.html')



def gainers(request):

    gainers = []
    delta = datetime.timedelta(1,0,0)
    access_token = request.session.get('access_token')
    u = Upstox ('rfFYsHqjVM8gl8DjbaWAs7lR1kPk5t969YHl6jlb', access_token)
    u.get_master_contract('NSE_EQ')

    fopath = os.path.join(settings.BASE_DIR,'scanner','fo.csv')
    fo = open(fopath,"r")
    stocks = fo.read().splitlines()
    fo.close()

    def do_screen(stock):
        #global gainers
        y =u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', stock), OHLCInterval.Minute_1, datetime.datetime.now().date()-delta,datetime.datetime.now().date())
        gain = float(y[-1]['high']) - float(y[-10]['low'])
        gain_per = (gain/float(y[-1]['close']))*1000
        gain_per = round(gain_per,2)
        open1 = round(float(y[0]['open']),2)
        ltp = round(float(y[-1]['close']),2)

        if(gain_per > 8 or gain_per < -8):
            x = [stock, open1,ltp,gain_per]
            gainers.append(x)

    #global gainers

    p = mp.Pool(20)
    p.map(do_screen,stocks)
    p.close()
    p.join()
    gainers = sorted(gainers,key=lambda x:x[3])
    return render(request,'gainers.html',{'gainers':gainers})



def gainers1(request):

    gainers = []
    delta = datetime.timedelta(1,0,0)
    access_token = request.session.get('access_token')
    u = Upstox ('rfFYsHqjVM8gl8DjbaWAs7lR1kPk5t969YHl6jlb', access_token)
    u.get_master_contract('NSE_EQ')

    fopath = os.path.join(settings.BASE_DIR,'scanner','fo.csv')
    fo = open(fopath,"r")
    stocks = fo.read().splitlines()
    fo.close()

    def do_screen(stock):
        #global gainers
        y =u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', stock), OHLCInterval.Minute_5, datetime.datetime.now().date(),datetime.datetime.now().date())
        gain = float(y[-1]['high']) - float(y[-12]['low'])
        gain_per = (float(gain/y[-1]['close']))*1000
        gain_per = round(gain_per,2)
        open1 = round(float(y[0]['open']),2)
        ltp = round(float(y[-1]['close']),2)

        if(gain_per > 20 or gain_per < -20):
            x = [stock, open1,ltp,gain_per]
            gainers.append(x)

    #global gainers

    p = mp.Pool(20)
    p.map(do_screen,stocks)
    p.close()
    p.join()
    gainers = sorted(gainers,key=lambda x:x[3])
    return render(request,'gainers.html',{'gainers':gainers})
