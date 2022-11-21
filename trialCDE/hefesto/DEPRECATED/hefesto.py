
import pandas as pd
import requests


class Hefesto():
    def __init__(self, path):

        # Import CSV using pandas:
        self.path = path
        self.df = pd.read_csv(path)

        # Create an object as dictonary to reduce duplicate calls:
        self.reg = dict()

    def get_uri(self, col, ont):

        # Column duplication to work in new column:
        self.df[col+"_uri"] = self.df.loc[:, col]

        # Loop throught new column to replace current value with API term:
        for i in self.df[col+"_uri"].index:
            term = self.df.at[i,col+"_uri"]
            if term in self.reg:
                self.df.at[i,col+"_uri"] = self.reg[term] 

            else: # API call to OLS
                url= "http://www.ebi.ac.uk/ols/api/search?q="+ term +"&ontology=" + ont
                r = requests.get(url,headers= {"accept":"application/json"})
                data = r.json()
                # JSON navigation:
                data_iri = data["response"]["docs"][0]["iri"]
                # Attach new value to the Dataframe:
                self.reg[term] = data_iri
                self.df.at[i,col+"_uri"] = data_iri 

        print(self.df)
        return self.df



    def get_label(self, col):

        # Column duplication to work in new column:
        self.df[col+"_label"] = self.df.loc[:, col]

        # Loop throught new column to replace current value with API term:
        for i in self.df[col+"_label"].index:
            term = self.df.at[i,col+"_label"]
            if term in self.reg:
                self.df.at[i,col+"_label"] = self.reg[term] 

            else: # API call to OLS
                url= 'http://www.ebi.ac.uk/ols/api/terms?iri='+ term
                r = requests.get(url,headers= {"accept":"application/json"}) # API call to OLS
                data = r.json()
                # JSON navigation:
                data_label = data["_embedded"]["terms"][0]["label"]
                # Attach new value to the Dataframe:
                self.reg[term] = data_label
                self.df.at[i,col+"_label"] = data_label 

        print(self.df)
        return self.df
    
    def replace_inf(self,col, key, value, duplicate):
        if duplicate == "True":
            # Column duplication to work in new column:
            self.df[col+"_dup"] = self.df.loc[:, col]
            self.df[col+"_dup"] = self.df[col+"_dup"].replace([key],value)
        else:
            self.df[col] = self.df[col].replace([key],value) 
        print(self.df)
        return self.df


# trial

trial = Hefesto('/home/pabloalarconm/Desktop/EJP/MEDUSA/trialCDE/hefesto/DEPRECATED/trial_hefesto.csv')
trial.get_uri("output1","sio")
trial.get_label("output2")
trial.replace_inf("output1", "information content entity","information content procedure")



