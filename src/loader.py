import os
import os.path
import sys
import socket, struct
import getpass
import subprocess
import getopt
import datetime
import tarfile
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring, ElementTree
import random as r
import pydoc
import shutil

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
import yaml

class ParseXML:
	def __init__(self, xml_conf_file):
		self.xml_conf_file = xml_conf_file
		# print(self.xml_conf_file)
		self.xml_data = open(self.xml_conf_file)
		self.xml_str = self.xml_data.read()
		self.xml_tree = ElementTree(fromstring(self.xml_str))
		self.xml_root = self.xml_tree.getroot()

	def read_xml(self):
		return ET.tostring(self.xml_root, encoding='unicode', method='xml')

	def read_xml_value(self, node, value):
		# print(self.xml_tree)
		for tag in self.xml_tree.findall(node):
			p_value = tag.get(value)
			return p_value


	def edit_xml(self, node, value, **kwargs):
		if "attribute" in kwargs:
			try:
				for element in self.xml_root.findall(node):
					element.set(kwargs['attribute'],value)
					welement.set(attr,value)
			except NameError:
				pass
			return ET.tostring(self.xml_root, encoding='unicode', method='xml')
		else:
			for i in self.xml_root.iter(node):
				self.xml_root.set(node, value)
				i.text = value
			return ET.tostring(self.xml_root, encoding='unicode', method='xml')

@dataclass
class manifestConfig:
    name: str
    group: str
    memory: int
    vcpus: int
    disk: Dict[str, Any]
    network: Dict[str, Any]

class manifestLoader:
    def load_config(config_path: str) -> manifestConfig:
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Convert nested dictionaries to dataclass instances
        manifest = DatabaseConfig(**config_dict)
        
        return AppConfig(manifest=manifest)

