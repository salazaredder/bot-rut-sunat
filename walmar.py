from functions import *
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert
from PIL import Image
from io import BytesIO
import pytesseract

SEARCH = '20102179898'
URL_SUNAT = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS03Alias'


# browser = get_chrome_driver(proxy=False)


def buscar_rut(search_rut):
    try:
        browser = get_chrome_driver(proxy=False)
        browser.get(URL_SUNAT)
        search = get_element_by_xpath(browser, '//*[@id="s1"]/input')
        input_captcha = get_element_by_xpath(
            browser, '/html/body/form/table/tbody/tr/td/table[2]/tbody/tr[6]/td[3]/table/tbody/tr/td[1]/input')
        search.clear()
        search.send_keys(search_rut)
        captcha = get_element_by_xpath(browser, '/html/body/form/table/tbody/tr/td/table[2]/tbody/tr[5]/td[3]/img')
        mi_img_base_64 = captcha.screenshot_as_png
        im_file = BytesIO(mi_img_base_64)
        img = Image.open(im_file)
        captcha_text = pytesseract.image_to_string(img)
        captcha_text = captcha_text.strip()[0:4]
        input_captcha.send_keys(captcha_text)

        buscar = get_element_by_xpath(
            browser, '/html/body/form/table/tbody/tr/td/table[2]/tbody/tr[6]/td[3]/table/tbody/tr/td[2]/input')
        buscar.click()
    except UnexpectedAlertPresentException as error:
        print(error)
        browser.close()
        return {'error': error.alert_text}
    except Exception as error:
        print(f"Error inesperado: {error}")
        browser.close()
        return {'error': error.__str__()}

    response = {}
    try:
        response['rut'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[2]/td[2]')
        response['tipo_contribuyente'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[3]/td[2]')
        response['nombre_comercial'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[4]/td[2]')
        response['fecha_inscripcion'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[5]/td[2]')
        response['estado'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[6]/td[2]')
        response['condicion'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[7]/td[2]')
        response['domicilio_fiscal'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[8]/td[2]')
        response['actividades_economicas'] = get_element_by_xpath(browser,
                                                                  '/html/body/table[1]/tbody/tr[9]/td[2]/select')
        response['comprobantes_pago'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[10]/td[2]/select')
        response['sistema_emision'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[11]/td[2]/select')
        response['afilido_ple'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[12]/td[2]')
        response['padrones'] = get_element_by_xpath(browser, '/html/body/table[1]/tbody/tr[13]/td[2]/select')

        for item in response:
            response[item] = response[item].text.strip()
            if item in ['actividades_economicas', 'comprobantes_pago', 'padrones']:
                temp = response[item].split('\n                \n                \n')
                data = []
                for t in temp:
                    t = t.strip('\n')
                    t = t.strip()
                    data.append(t)
                response[item] = data
        # nueva_consulta = get_element_by_xpath(browser, '/html/body/table[2]/tbody/tr[3]/td/input')
        # nueva_consulta.click()
        browser.close()
        return response
    except UnexpectedAlertPresentException as error:
        print('Error Alert')
        print(error.alert_text)
        browser.close()
        return {'error': error.alert_text}
    except Exception as error:
        print(f"Error inesperado: {error}")
        browser.close()
        return {'error': error.__str__()}

    # for item in response:
    #     print(f"{item}: {response[item]}")
