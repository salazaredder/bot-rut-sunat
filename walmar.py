from functions import *
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert
SEARCH = '20102179898'


# browser = get_chrome_driver(proxy=False)


def buscar_rut(search_rut):
    try:
        browser = get_chrome_driver(proxy=False)
        browser.get('https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/frameCriterioBusqueda.jsp')
        search = get_element_by_xpath(
            browser,
            '/html/body/form/table/tbody/tr/td/table[2]/tbody/tr[1]/td[3]/div/input'
        )
        search.clear()
        search.send_keys(search_rut)
        buscar = get_element_by_xpath(browser, '/html/body/form/table/tbody/tr/td/table[2]/tbody/tr[1]/td[4]/input')
        buscar.click()
        time.sleep(2)
        windows = browser.window_handles
        if len(windows) == 2:
            browser.switch_to.window(windows[1])
        else:
            alert = Alert(browser)
            print(alert.text)
            alert.accept()
            browser.close()
            return False
    except UnexpectedAlertPresentException as error:
        print(error)
        browser.close()
        return False
    except Exception as error:
        print(f"Error inesperado: {error}")
        browser.close()
        return False

    if len(windows) == 2:
        browser.switch_to.window(windows[1])
    else:
        print('No abrio la pestaña')
        browser.close()
        return False

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
        browser.close()
        browser.switch_to.window(windows[0])
        browser.close()
        return response

    except Exception as error:
        browser.close()
        browser.switch_to.window(windows[0])
        browser.close()
        return False

    # for item in response:
    #     print(f"{item}: {response[item]}")
