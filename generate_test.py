import json
from ast import literal_eval
import yaml


from mimesis.locales import Locale
from mimesis.schema import Field,Schema
from mimesis import Internet 
from mimesis.enums import URLScheme 
from mimesis import Numeric
from mimesis import BinaryFile 
from mimesis import Cryptographic 
from mimesis.random import get_random_item 

class SchemaGen() :
	def __init__(self) :
		self.internet = Internet()
		self.numeric = Numeric()
		self.binary =  BinaryFile()
		self.crypto = Cryptographic()

	def CreateJson(self,scenariofile,filepath,iterationtimes=10,arraysize=1) :
		reqdict,schemadata = self.GetSchema(scenariofile)
		schema = Schema(schema=lambda:schemadata)
		#multiple jsonfile maked
		for i in range(1,iterationtimes+1) :
			filename = "test" + "_" +str(i)+ ".json"
			outyaml = "test" + reqdict["yamltitle"] + "_" +str(i)+ "_" + "tavern.yaml"
			schema.to_json(file_path=filepath+filename,iterations=arraysize)
			self.GenerateYaml(reqdict,filename,filepath+outyaml)
	
	def GenerateYaml(self,reqdict,jsonfile,outyaml) :
		test_dict = {}	
		test_dict["test_name"] = reqdict["test_name"] 
		request = {
			"url":reqdict["url"],
			"method":reqdict["method"],
		}

		request["headers"] = {"content-type":"application/json"}
		if request["method"] != "GET":
			request["json"] = jsonfile

		response = {"strict":False,"status_code":reqdict["response"]}
		inner_dict = {"name":"api_test","request":request,"response":response}
		test_dict["stages"] = [inner_dict]

		with open(outyaml,'a') as file :
			yaml.dump(test_dict,file,explicit_start=True,default_flow_style=False)	


	def GetSchema(self,scenariofile) :
		json_open = open(scenariofile)
		json_load = json.load(json_open)
		reqdict = {}	
		reqdict["yamltitle"] = json_load["yamltitle"]
		reqdict["test_name"] = json_load["testname"]
		reqdict["url"] = json_load["testurl"]
		reqdict["method"] = json_load["testmethod"]
		reqdict["response"] = json_load["testresponse"]
		
		datasource = json_load["testdata"]
		data = self.gendata(datasource)
		return reqdict,data

	def gendata(self,datasource) :
		schemadata = {}
		for k , v in datasource.items() : 
			schemavalue , error = self.transschema(v)
			if error != "" :
				print(error)
			else : 
				schemadata[k] = schemavalue
		return schemadata


	def transschema(self,words) :
		if words == "test_uuid" :
			return self.crypto.uuid(),""
		elif words == "test_ipaddr" :
			return self.internet.ip_v4(),""
		elif "test_float" in words :
			maxminstr = words.replace("test_float","")
			maxmin = literal_eval(maxminstr) 
			return self.numeric.float_number(start=maxmin[0],end=maxmin[1]),""
		elif "test_enum" in words :
			enumlist = words.replace("test_enum","")
			enum = literal_eval(enumlist)
			return get_random_item(enum),""
		elif "test_binary:" in words : 
			length = int(words.replace("test_binary:",""))
			if length < 0 :
				return "","LengthError"
			else :
				return self.crypto.token_hex(entropy=length),""
		else :
			return "","key word is not found"	

schemagen = SchemaGen()
schemagen.CreateJson("data.json","./testdata/",iterationtimes=10)



#if __name__ == "__main__":
#    if len(sys.argv) < 2:
#        display_help()

#    outputfile = "test_001_tavern.yaml"
#    generate_tavern_yaml(sys.argv[1],outputfile)
