import logging
from gevent.subprocess import check_output, check_call, Popen, PIPE
from inspect import cleandoc
from os import remove, path
from bottle import Bottle, template, get, post, request
from gevent import sleep, monkey
monkey.patch_all()

logging.basicConfig(
    filename=f'{path.basename(__file__)}.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

app = Bottle()


@app.get('/')
def configure():
    logger.info('Loading wifi config page')

    def get_ssids(iter=0):
        # Get SSIDs found on wlan0
        logger.info(f'Getting SSIDs')
        proc = Popen("sudo iw wlan0 scan | egrep 'SSID: \w' | awk '{print $2}'",
                     shell=True,
                     stdout=PIPE,
                     encoding='utf8')

        # clean up SSIDs
        ssids = [x.replace("\n", "").rstrip() for x in proc.stdout.readlines()]

        # make a few attempts if ssids is empty
        if not ssids and iter < 5:
            logger.info(f'SSIDs not found, trying again')
            sleep(1)
            get_ssids(iter+1)
        elif not ssids and iter > 4:
            logger.error(f'Could not find any SSIDs')
        else:
            logger.info(f'SSIDs found: {",".join(ssids)}')
        
        return ssids

    return template(
        'index.html',
        root='/home/pi',
        stage=None,
        ssids=get_ssids(),
        message='none')


@app.get('/restart')
def restart():
    try:
        wpa_passphrase = check_output(
            f'sudo ifdown --force ap0; sudo ifdown --force wlan0; sudo ifup wlan0',
            shell=True,
            encoding='utf8')
    except Exception as e:
        logger.error(e)
    

@app.post('/')
def post():
    logger.info(f'Form submitted')
    message = 'none'
    stage = None

    while request.forms:
        if request.forms.get('username') is None:
            message = 'SSID was not selected'
            logger.info(message)
            break
        elif request.forms.get('password') is None:
            message = 'Key was not submitted'
            logger.info(message)
            break
        else:
            logger.info(f'Wifi SSID and key submitted')
            username = request.forms.get('username')
            password = request.forms.get('password')
            message = 'none'

        def failed(message):
            stage = None
            message = message
            logger.error(message)


        # update wpa_supplicant
        try:
            logger.info(f'Updating wpa_supplicant-wlan0.conf')
            # get wpa_passphrase
            wpa_passphrase = check_output(
                f'wpa_passphrase {username} {password} | grep -E "\s(ssid|psk)"',
                shell=True,
                encoding='utf8')
            wpa_supplicant = open(
                '/etc/wpa_supplicant/wpa_supplicant-wlan0.conf', 'w')
            wpa_supplicant.write(cleandoc(f'''
                ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev
                update_config=1
                network={{
                    {wpa_passphrase}
                    id_str="AP"
                }}'''))
            wpa_supplicant.close()
        except Exception as e:
            failed(f'Updating wpa_supplicant-wlan0.conf failed: {e}')
            break


        # add wpa_supplicant to /etc/network/interfaces
        try:
            logger.info(f'Configuring interfaces')
            check_call(
                "sudo sed -e '/#wpa-conf/ s/#wpa-conf/wpa-conf/' -i /etc/network/interfaces",
                shell=True)
            stage = 'configured'
        except Exception as e:
            failed(f'Updating interfaces file failed: {e}')
            break

    return template(
        'index.html',
        root='/home/pi',
        ssids=ssids,
        stage=stage,
        message=message)


if __name__ == '__main__':
    logger.info('Starting wifi config portal')
    app.run(host='0.0.0.0', port=8000, server='gevent', quiet=True)
