import threading
import logging
import requests
import os
import time
from PIL import Image
from io import BytesIO
from telegram.ext import Updater, CommandHandler
from urllib import request, parse
from user import settings, rt_plots
from academy import queues
from academy.utils import utils
from academy.camera import cam1, cam2, cam3
try:
    from user.rt_plots import fig
except:
    fig = None


# Set up logging
logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text('Hi! Use /status <hours> to see the status.')

def alarm_mice(area):
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: 2 rats in box, area ' + str(int(area))
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))

        # Call cam function here
        cam_2()

    #   Capture and send images from cam_1
    #   image_streams = cam_2()
    #
    #     if image_streams:
    #         url = 'https://api.telegram.org/bot%s/sendPhoto' % settings.TELEGRAM_TOKEN
    #         for stream in image_streams:
    #             files = {'photo': stream}
    #             data = {'chat_id': settings.TELEGRAM_CHAT}
    #             response = requests.post(url, data=data, files=files)
    #             response.raise_for_status()
    #         logger.info("Camera images sent to Telegram chat")
    #     else:
    #         logger.warning("No images captured from cam_1")
    #
    except Exception as e:
        logger.error(f"Error in alarm_mice function: {e}")

def alarm_mice_floor(subject_name):
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: Animal in the floor' + ', subject: ' + str(subject_name)
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))
    except:
        pass

def alarm_temperature(temperature):
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: high temperature ' + temperature
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))
    except:
        pass


def alarm_session_time(seconds, subject_name):
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: rat has been more than ' + str(int(seconds)) + ' seconds in the box' + ', subject: ' + str(subject_name)
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))
    except:
        pass


def alarm_mouse(my_list):
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: check weight and water: ' + ','.join(my_list)
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))
    except:
        pass


def alarm_bpod(text):
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: bpod communication error: ' + text
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))
    except:
        pass


def alarm_softcodes():
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: bpod not sending softcodes'
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))
    except:
        pass


def alarm_serials():
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: bpod not sending serials'
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))
    except:
        pass

def alarm_overdetections(text):
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: overdetections in: ' + text
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))
    except:
        pass


def alarm_subject_trapped():
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: subject is trapped in the corridor'
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))
    except:
        pass

def alarm_few_trials(n_trials, subject_name):
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: few trials: ' + str(n_trials) + ', subject: ' + str(subject_name)
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})
        request.urlopen(url, data.encode('utf-8'))
    except:
        pass

def alarm_touchscreen(subject_name):
    try:
        url = 'https://api.telegram.org/bot%s/sendMessage' % settings.TELEGRAM_TOKEN
        message = 'ALARM: touchscreen is not working for subject: ' + str(subject_name)
        utils.alarms.add_new_item({'message': message})
        data = parse.urlencode({'chat_id': settings.TELEGRAM_CHAT, 'text': message})

        request.urlopen(url, data.encode('utf-8'))


    except:
        pass


def status(update, context):
    try:
        hours = int(context.args[0])
        if hours < 1:
            hours = 24
    except:
        hours = 24

    try:
        user_id = str(update.effective_user.id)

        if user_id not in settings.TELEGRAM_USERS.values():
            print('WARNING: New Telegram User ID:', user_id)

        elif hours < 0:
            update.message.reply_text('Sorry we can not go back to future!')

        else:
            data, error_mice_list = rt_plots.telegram_data(hours=hours)
            update.message.reply_text(data)
    except:
        pass


def cam(update, context):

    try:
        user_id = str(update.effective_user.id)

        if user_id not in settings.TELEGRAM_USERS.values():
            print('WARNING: New Telegram User ID:', user_id)

        else:

            try:
                frame1 = cam1.image_queue.get(timeout=1)
                img1 = Image.fromarray(frame1)
                stream1 = BytesIO()
                img1.save(stream1, format="JPEG")
                stream1.seek(0)
                update.message.reply_photo(photo=stream1)
            except:
                pass

            try:
                frame2 = cam2.image_queue.get(timeout=1)
                img2 = Image.fromarray(frame2)
                stream2 = BytesIO()
                img2.save(stream2, format="JPEG")
                stream2.seek(0)
                update.message.reply_photo(photo=stream2)
            except:
                pass

            try:
                frame3 = cam3.image_queue.get(timeout=1)
                img3 = Image.fromarray(frame3)
                stream3 = BytesIO()
                img3.save(stream3, format="JPEG")
                stream3.seek(0)
                update.message.reply_photo(photo=stream3)
            except:
                pass
    except:
        pass


# def cam_1():
#     streams = []
#
#     try:
#         frame1 = cam1.image_queue.get(timeout=1)
#         img1 = Image.fromarray(frame1)
#         stream1 = BytesIO()
#         img1.save(stream1, format="JPEG")
#         stream1.seek(0)
#         streams.append(stream1)
#     except Exception as e:
#         print(f"Error capturing image from cam1: {e}")
#
#     try:
#         frame2 = cam2.image_queue.get(timeout=1)
#         img2 = Image.fromarray(frame2)
#         stream2 = BytesIO()
#         img2.save(stream2, format="JPEG")
#         stream2.seek(0)
#         streams.append(stream2)
#     except Exception as e:
#         print(f"Error capturing image from cam2: {e}")
#
#     try:
#         frame3 = cam3.image_queue.get(timeout=1)
#         img3 = Image.fromarray(frame3)
#         stream3 = BytesIO()
#         img3.save(stream3, format="JPEG")
#         stream3.seek(0)
#         streams.append(stream3)
#     except Exception as e:
#         print(f"Error capturing image from cam3: {e}")
#
#     return streams

def send_photo(chat_id, frame):
    try:
        url = f'https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendPhoto'
        img = Image.fromarray(frame)
        stream = BytesIO()
        img.save(stream, format="JPEG")
        stream.seek(0)
        files = {'photo': ('photo.jpg', stream, 'image/jpeg')}
        data = {'chat_id': chat_id}
        response = requests.post(url, data=data, files=files)
        if response.status_code != 200:
            logger.error(f"Error sending photo: {response.status_code} - {response.text}")
        else:
            logger.info("Photo sent successfully.")


    except Exception as e:
        logger.error(f"Error sending photo: {e}")

def cam_2():
    chat_id = settings.TELEGRAM_CHAT
    for cam in [cam1, cam2, cam3]:
        try:
            frame = cam.image_queue.get(timeout=1)
            send_photo(chat_id, frame)
        except Exception as e:
            logger.error(f"Error processing frame from {cam}: {e}")

# def cam_2():
#     try:
#         frame1 = cam1.image_queue.get(timeout=1)
#         img1 = Image.fromarray(frame1)
#         stream1 = BytesIO()
#         img1.save(stream1, format="JPEG")
#         stream1.seek(0)
#         #update.message.reply_photo(photo=stream1)
#         bot = Bot(token=settings.TELEGRAM_TOKEN)
#         chat_id = settings.TELEGRAM_CHAT
#         bot.send_photo(chat_id=chat_id, photo=stream1)
#     except:
#         pass
#
#     try:
#         frame2 = cam2.image_queue.get(timeout=1)
#         img2 = Image.fromarray(frame2)
#         stream2 = BytesIO()
#         img2.save(stream2, format="JPEG")
#         stream2.seek(0)
#         #update.message.reply_photo(photo=stream2)
#         bot = Bot(token=settings.TELEGRAM_TOKEN)
#         chat_id = settings.TELEGRAM_CHAT
#         bot.send_photo(chat_id=chat_id, photo=stream2)
#     except:
#         pass
#
#     try:
#         frame3 = cam3.image_queue.get(timeout=1)
#         img3 = Image.fromarray(frame3)
#         stream3 = BytesIO()
#         img3.save(stream3, format="JPEG")
#         stream3.seek(0)
#         #update.message.reply_photo(photo=stream3)
#         bot = Bot(token=settings.TELEGRAM_TOKEN)
#         chat_id = settings.TELEGRAM_CHAT
#         bot.send_photo(chat_id=chat_id, photo=stream3)
#     except:
#         pass


def plot(update, context):

    try:
        user_id = str(update.effective_user.id)

        if user_id not in settings.TELEGRAM_USERS.values():
            print('WARNING: New Telegram User ID:', user_id)

        else:

            try:
                days = int(context.args[0])
                if days < 1:
                    days = 3
                    #days = 14
            except:
                days = 3
                #days = 14

            try:
                photo = os.path.join(settings.DATA_DIRECTORY, 'plots.jpg')
                utils.x_max = days
                time.sleep(1)
                queues.update_plots.put(True)
                time.sleep(20)
                update.message.reply_photo(photo=open(photo, 'rb'))
            except:
                pass
    except:
        pass


def report(update, context):
    try:
        user_id = str(update.effective_user.id)

        if user_id not in settings.TELEGRAM_USERS.values():
            print('WARNING: New Telegram User ID:', user_id)

        else:
            status(update, context)
            cam(update, context)
            plot(update, context)
    except:
        pass



def telegram_thread():
    updater = Updater(settings.TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("status", status, pass_args=True))
    dp.add_handler(CommandHandler("plot", plot, pass_args=True))
    dp.add_handler(CommandHandler("cam", cam, pass_args=True))
    dp.add_handler(CommandHandler("report", report, pass_args=True))
    dp.add_handler(CommandHandler("cam_2", report, pass_args=True))

    updater.start_polling()


threading.Thread(target=telegram_thread, daemon=True).start()




# without internet connection
#
# def alarm_mice():
#     print("alarm mice")
#
# def alarm_temperature(temperature):
#     print("alarm temperature")
#
# def alarm_session_time(seconds):
#     print("alarm session time")
#
# def alarm_mouse(my_list):
#     print("alarm mouse")
#
# def alarm_bpod(text):
#     print("alarm bpod")
#
# def alarm_softcodes():
#     print("alarm arduino")
#
# def alarm_serials():
#     print("alarm serials")
#
# def alarm_few_trials(n_trials, subject_name):
#     print("alarm few trials")
#
# def alarm_touchscreen(subject_name):
#     print("alarm touchscreen")
