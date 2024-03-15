import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
# import json
# import xml.etree.ElementTree as ET


class DrivingLicenseScraper:
    def __init__(self, source_url, endpoint, driving_licence_number, date_of_birth, captcha_image_id):
        self.source_url = source_url
        self.endpoint = endpoint
        self.driving_licence_number = driving_licence_number
        self.dob = date_of_birth
        self.captcha_image_id = captcha_image_id
        self.session = requests.Session()

    
    def __render_image_from_url(self, image_url):
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.show()
        else:
            raise Exception("Error! Unable to fetch captcha.")

    def __scrapWebPage(self):
        webpage = requests.get(self.source_url+self.endpoint)
        soup = BeautifulSoup(webpage.content, "html.parser")

        if webpage.status_code == 404:
            raise Exception("Error! Page not found.")
        
        if webpage.status_code != 200:
            raise Exception("Error! Unable to access webpage.")
        
        captcha_img = soup.select_one(f'img[id*="{self.captcha_image_id}"]')
        image_endpoint = captcha_img['src']
        viewStateValue = soup.select_one(f'input[name*="javax.faces.ViewState"]').attrs['value']
        self.__render_image_from_url(self.source_url+image_endpoint)
        return viewStateValue

    def sendRequest(self, endpoint):
        viewStateValue = self.__scrapWebPage()
        captcha = input("Enter captcha: ")

        payload = {
            "javax.faces.partial.ajax": True,
            "javax.faces.source: form_rcdl":"j_idt50",
            "javax.faces.partial.execute": "@all",
            "javax.faces.partial.render": "form_rcdl:pnl_show form_rcdl:pg_show form_rcdl:rcdl_pnl",
            "form_rcdl:j_idt50": "form_rcdl:j_idt50",
            "form_rcdl": "form_rcdl",
            "javax.faces.ViewState": viewStateValue,
            "form_rcdl:tf_dlNO": self.driving_licence_number,
            "form_rcdl:tf_dob_input": self.dob,
            "form_rcdl:j_idt39:CaptchaID": captcha
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        xml_response = requests.post(self.source_url+endpoint, headers=headers, data=payload)._content
        print(xml_response)
        return xml_response


if __name__ == "__main__":
    # dl_number = "DL0420110149646"
    # dob = "09-02-1976"
    dl_number = input("Enter Driving Licence Number: ")
    dob = input("Enter Date of Birth (DD-MM-YYYY): ")
    source_url = 'https://parivahan.gov.in'
    endpoint = "/rcdlstatus/?pur_cd=101"
    captcha_image_id="form_rcdl:j_idt39:j_idt44"

    scraper = DrivingLicenseScraper(source_url, endpoint, dl_number, dob, captcha_image_id)
    scraper.sendRequest("/rcdlstatus/vahan/rcDlHome.xhtml")
