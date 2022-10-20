from Hefesto.main import Hefesto
import yaml

# Import YAML configuration file with all parameters:
with open("CDEconfig.yaml") as file:
    configuration = yaml.load(file, Loader=yaml.FullLoader)

test = Hefesto.transform_shape(path_datainput ="exemplarCDEdata.csv", configuration=configuration)
test.to_csv ("resultCDE.csv", index = False, header=True)