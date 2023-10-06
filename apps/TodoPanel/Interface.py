from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from DataCenter import GCmd
from jsonschema import draft202012_format_checker

class ModelPresenter(metaclass=ABCMeta):
    @abstractmethod
    def setDataToView(self):
        pass

    @abstractmethod
    def updateConnData(self):
        pass

    @abstractmethod
    def update_basic_field(self, id:str, field_values):
        pass

    @abstractmethod
    def handleShowOtherModel(self, model_name, model_id):
        pass

    @abstractmethod
    def handleDeleteModel(self, _id):
        pass

    @abstractmethod
    def update_other_model(self, model_name:str, update_cmd:GCmd):
        pass

class PanelPresenter(metaclass=ABCMeta):
    @abstractmethod
    def refresh(self, setting:dict = None):
        pass

    @abstractmethod
    def setUI(self, view, parent_widget = None):
        pass

    @abstractmethod
    def Accept(self, cmd):
        pass

    @abstractmethod
    def handleAction(self, action):
        pass

    @abstractmethod
    def handleSettingChange(self, setting):
        pass

@dataclass(frozen=True)
class Schema:
    todo_panel_checkstatus = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "check_status",
    "description": "check_status of the todo panel",
    "type": "object",
    "properties": {
        "mission_range": {
            "description": "a number and a boolean: missions at which stage should be included; should the destroyed ones be included? ",
            "type": "array",
            "items":[
                {
                    "type":"integer",
                    "minimum":0,
                },
                {
                    "type":"boolean",
                }
            ]
        },
        "progress_check_status": {
            "description": "a list of boolean indicating whether todos at a certain progress should be included",
            "type": "array",
            "items":{
                "type": "boolean",
                "minLength":3,
                "maxLength":3
            }
        },
        "urgence_range": {
            "description": "two booleans indicating whether todos at a urgence state should be included",
            "type": "array",
            "items": {
                "type": "boolean",
                "minLength": 2,
                "maxLength": 2
            }
        },
        "project_check_status": {
            "description": "a list of booleans indicating whether todo from projects at a certain state should be included",
            "type": "array",
            "items": {
                "type": "boolean",
                "minLength": 7,
                "maxLength": 7
            }
        },
        "timespace_distance_checked": {
            "description": "a list of number indicating the todo of certain timespace distance needed",
            "type": "array",
            "items":{
                "type": "integer",
                "minimum": 0,
                "minLength": 3,
                "maxLength": 3
            }
        },
        "arrange_strategy":{
            "description": "a number indicating the strategy,ARRANGE_WEIGHT = 0, ARRANGE_COMPANY = 1, "
                           "ARRANGE_PROJECT = 2,ARRANGE_OFFI_TYPE = 0 ",
            "type": "integer",
        }
    },
}