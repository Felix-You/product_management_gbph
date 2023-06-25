import openpyxl

import xml.etree.ElementTree as ET
import os

class ChinaGeo(object):

    def __init__(self):
        geo_file = os.path.join("./LocListCN.xml")
        geo_tree = ET.parse(geo_file)
        self.geo_root = geo_tree.getroot()
        self._country_code = '1'
        self.countries = self.geo_root.findall('CountryRegion')

    @staticmethod
    def convertInt(str: str):
        if str.isdigit():
            return int(str)
        else:
            return str

    def checkCityCodeChineseVersion(self, code):
        if len(str(code)) != 4:
            return False
        if isinstance(code, int):
            return True
        tmp = self.convertInt(code)
        if isinstance(tmp, int):
            return True
        return False

    def checkTownCodeChineseVersion(self,code):
        if len(str(code)) != 6:
            return False
        if isinstance(code, int):
            return True
        tmp = self.convertInt(code)
        if isinstance(tmp, int):
            return True
        return False

    @property
    def country_code(self):
        return self._country_code

    def setCountryCode(self, country_code: str):
        self._country_code = country_code

    def getAllProvinces(self, country_code='1') -> list[tuple[str, str]]:
        '''
        return: list[(Code, Name),]
        '''
        country = self.getCountry(country_code=country_code)
        provinces = country.findall('State')
        if len(provinces) > 1:
            return [(province.attrib.get("Code", None), province.attrib.get('Name', None)) for province in provinces]
        else:
            return []

    def getCities(self, province_code: str):
        '''
        return: list[(Code, Name),]
        '''
        province = self.getCountryProvince(state_code=province_code)
        cities = province.findall('City')
        if len(cities) > 1:
            return [(city.attrib.get("Code", None), city.attrib.get('Name', None)) for city in cities]
        else:
            return []
    def getTowns(self, city_code: str, province_code=None, country_code:str=None):
        '''
        return: list[(Code, Name),]
        '''
        str_code = str(city_code)
        is_china_old = self.checkCityCodeChineseVersion(city_code)

        if is_china_old and not province_code:
            province_code = str_code[:2]
            city_code = str_code[2:4]
            city_code = str(self.convertInt(city_code))
        else:
            city_code = str_code

        province = self.getCountryProvince(state_code=province_code, country_code=country_code)

        city = self.getCity(province, city_code)

        region = city.find('Region')

        if region is not None:
            towns = city.findall('Region')
            town_items = [(town.attrib.get("Code", None), town.attrib.get('Name', None)) for town in towns]
            return town_items
        else:
            return None

    def getCountry(self, country_code: str = None):
        if not country_code:
            country_code = self._country_code
        return self.geo_root.find(f'.//CountryRegion[@Code="{country_code}"]')

    def getCountryProvince(self, country_code=None, state_code='11'):
        country = self.getCountry(country_code)
        if len(country.findall("State")) == 1:
            return country.find("State")
        state = country.find(f'.//State[@Code="{state_code}"]')
        return state

    def getCity(self, state: ET.Element, city_code: str):
        city = state.find(f'.//City[@Code="{city_code}"]')
        return city

    def getTown(self, city: ET.Element, town_code: str):
        town = city.find(f'.//Region[@Code="{town_code}"]')
        return town

    def getName(self, element: ET.Element):
        return element.attrib.get('Name', None)

    def getCode(self, element: ET.Element):
        return element.attrib.get('Code', None)

    def makeGeoExcel(self):
        work_book = openpyxl.Workbook()
        work_sheet = work_book.active
        work_sheet.append(['省份名称','省份代码', '市级名称', '市级代码', '县/区级名称', '县区级代码'])
        provinces = self.getCountry().findall('State')
        line1 = []
        for province in provinces:
            line1 = [ province.attrib.get('Name', None), province.attrib.get("Code", None)]
            cities = province.findall('City')
            for city in cities:
                line2 = line1 + [city.attrib.get('Name', None), city.attrib.get("Code", None)]
                towns = city.findall('Region')
                if not towns:
                    line3 = line2 + ['', '']
                    work_sheet.append(line3)
                    continue
                for town in towns:
                    line3 = line2+[town.attrib.get('Name', None),town.attrib.get("Code", None)]
                    work_sheet.append(line3)

        work_book.save(f'./行政区编码.xlsx')

if __name__ == '__main__':
    geo = ChinaGeo()
    geo.makeGeoExcel()